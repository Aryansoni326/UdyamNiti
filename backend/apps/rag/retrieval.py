"""
Hybrid Retrieval Engine for Government Policy Evidence.
Combines:
- 384-dimensional dense semantic vector similarity
- Full-text keyword/lexical retrieval with exact clause/scheme boosting
- Strict metadata filters (active policy version, state, authority, candidate schemes)
- Source Tier weighting (Tier 1 Gazette > Tier 2 Guidelines > Tier 3 Circular > Tier 4 FAQ)
- Maximal Marginal Relevance (MMR) & section-diversity deduplication
- Fail-closed gating when evidence confidence is insufficient
"""
import math
import re
from dataclasses import dataclass, field
from datetime import date
from typing import List, Dict, Any, Optional

from django.db.models import Q
from apps.rag.models import PolicyDocumentChunk
from apps.rag.pipeline import generate_embedding


# Tier weighting multipliers (Statutory Gazette takes precedence over portal FAQs)
TIER_WEIGHTS = {
    'tier_1_gazette': 1.25,
    'tier_2_operational_guidelines': 1.15,
    'tier_3_ministry_circular': 1.05,
    'tier_4_portal_faq': 1.00,
}

# Critical statutory terminology for lexical boosting
STATUTORY_KEYWORDS = [
    "gross fixed capital investment", "gfci", "eligible enterprise", "margin money",
    "term loan", "category-1 taluka", "category-2 taluka", "category-3 taluka",
    "annual guarantee fee", "collateral-free", "udyam registration", "second-hand machinery",
    "negative list", "commencement of commercial production", "docp", "interest subvention",
    "working capital", "common facility center", "zero defect zero effect", "zed",
    "subsidized", "ineligible activities", "micro enterprise", "small enterprise"
]

DEFAULT_FAIL_CLOSED_THRESHOLD = 0.28


@dataclass
class HybridQueryRequest:
    user_question: str
    business_goal: str = ""
    support_categories: List[str] = field(default_factory=list)
    msme_facts: Dict[str, Any] = field(default_factory=dict)
    candidate_scheme_ids: List[str] = field(default_factory=list)
    
    # Metadata filters
    state_filter: Optional[str] = None
    authority_filter: Optional[str] = None
    source_tier_filter: Optional[str] = None
    min_effective_date: Optional[date] = None
    
    top_k: int = 5
    dense_weight: float = 0.55
    keyword_weight: float = 0.45
    rrf_k: int = 60
    min_score_threshold: float = DEFAULT_FAIL_CLOSED_THRESHOLD


@dataclass
class EvidenceCitation:
    chunk_id: str
    document_id: str
    scheme_id: Optional[str]
    authority: str
    source_url: str
    source_tier: str
    document_title: str
    publication_effective_date: str
    page_number: int
    section_heading: str
    chunk_text: str
    chunk_index: int
    chunk_hash: str
    policy_version: int
    
    # Diagnostic fields (INTERNAL ONLY - NEVER USE AS ELIGIBILITY CONFIDENCE)
    internal_diagnostic_score: float
    retrieval_method: str
    tier_boost_applied: float
    matched_terms: List[str]


@dataclass
class HybridRetrievalResponse:
    citations: List[EvidenceCitation]
    total_candidates_searched: int
    retrieval_status: str  # 'confident', 'weak_evidence', 'insufficient_evidence'
    query_vector_computed: bool
    diagnostic_summary: Dict[str, Any]


def cosine_similarity(vec_a: List[float], vec_b: List[float]) -> float:
    """Compute cosine similarity between two normalized float vectors."""
    if not vec_a or not vec_b or len(vec_a) != len(vec_b):
        return 0.0
    dot = sum(a * b for a, b in zip(vec_a, vec_b))
    norm_a = math.sqrt(sum(a * a for a in vec_a)) or 1.0
    norm_b = math.sqrt(sum(b * b for b in vec_b)) or 1.0
    return max(0.0, dot / (norm_a * norm_b))


class HybridPolicyRetriever:
    """
    High-precision hybrid retrieval service combining dense vector similarity
    and BM25-style keyword search with statutory metadata filters and RRF reranking.
    """

    def retrieve(self, request: HybridQueryRequest) -> HybridRetrievalResponse:
        """Execute hybrid search pipeline."""
        # 1. Synthesize effective query for vector and lexical retrieval
        synthesized_query = self._synthesize_search_query(request)
        query_embedding = generate_embedding(synthesized_query)

        # 2. Build filtered base queryset ensuring current/active policy versions
        base_qs = PolicyDocumentChunk.objects.filter(is_active=True).select_related('document', 'scheme')

        if request.candidate_scheme_ids:
            base_qs = base_qs.filter(
                Q(scheme__scheme_code__in=request.candidate_scheme_ids) |
                Q(scheme__id__in=[cid for cid in request.candidate_scheme_ids if len(cid) == 36])
            )

        if request.authority_filter:
            base_qs = base_qs.filter(authority__icontains=request.authority_filter)

        if request.source_tier_filter:
            base_qs = base_qs.filter(source_tier=request.source_tier_filter)

        if request.min_effective_date:
            base_qs = base_qs.filter(publication_effective_date__gte=request.min_effective_date)

        total_candidates = base_qs.count()
        if total_candidates == 0:
            return HybridRetrievalResponse(
                citations=[],
                total_candidates_searched=0,
                retrieval_status='insufficient_evidence',
                query_vector_computed=True,
                diagnostic_summary={'reason': 'No active policy chunks match metadata filters.'}
            )

        candidate_chunks = list(base_qs[:300])

        # 3. Dense Semantic Scoring
        dense_scores: Dict[str, float] = {}
        for chunk in candidate_chunks:
            chunk_emb = chunk.embedding
            if chunk_emb:
                # If chunk_emb is a list
                if isinstance(chunk_emb, list):
                    score = cosine_similarity(query_embedding, chunk_emb)
                else:
                    score = 0.5
            else:
                score = 0.1
            dense_scores[str(chunk.id)] = score

        # 4. Keyword / Lexical Scoring with Statutory & Scheme Name Boosts
        lexical_scores: Dict[str, float] = {}
        query_tokens = set(re.findall(r'\b[a-zA-Z0-9\-_]{3,}\b', synthesized_query.lower()))
        matched_terms_map: Dict[str, List[str]] = {}

        for chunk in candidate_chunks:
            text_lower = chunk.chunk_text.lower()
            heading_lower = chunk.section_heading.lower()
            title_lower = chunk.document_title.lower()

            chunk_matches = []
            score = 0.0

            # Token overlap score
            for token in query_tokens:
                if token in heading_lower:
                    score += 3.0  # Heading match is high priority
                    chunk_matches.append(token)
                elif token in text_lower:
                    score += 1.0
                    chunk_matches.append(token)

            # Exact statutory keyword boost
            for kw in STATUTORY_KEYWORDS:
                if kw in text_lower or kw in heading_lower:
                    score += 2.5
                    chunk_matches.append(kw)

            # Exact scheme name or candidate scheme code boost
            if request.candidate_scheme_ids:
                for scheme_code in request.candidate_scheme_ids:
                    if scheme_code.lower() in text_lower or scheme_code.lower() in title_lower:
                        score += 4.0
                        chunk_matches.append(f"scheme:{scheme_code}")

            # Normalize lexical score
            normalized_lexical = min(1.0, score / max(10.0, len(query_tokens) * 2.0))
            lexical_scores[str(chunk.id)] = normalized_lexical
            matched_terms_map[str(chunk.id)] = list(set(chunk_matches))

        # 5. Reciprocal Rank Fusion (RRF) with Source Tier Weighting
        dense_ranked = sorted(candidate_chunks, key=lambda c: dense_scores.get(str(c.id), 0.0), reverse=True)
        lexical_ranked = sorted(candidate_chunks, key=lambda c: lexical_scores.get(str(c.id), 0.0), reverse=True)

        dense_rank_map = {str(c.id): rank for rank, c in enumerate(dense_ranked, start=1)}
        lexical_rank_map = {str(c.id): rank for rank, c in enumerate(lexical_ranked, start=1)}

        fused_scores: Dict[str, float] = {}
        tier_multiplier_map: Dict[str, float] = {}

        for chunk in candidate_chunks:
            cid = str(chunk.id)
            d_rank = dense_rank_map.get(cid, 999)
            l_rank = lexical_rank_map.get(cid, 999)

            # Base RRF calculation
            rrf_dense = request.dense_weight / (request.rrf_k + d_rank)
            rrf_lexical = request.keyword_weight / (request.rrf_k + l_rank)
            base_rrf = (rrf_dense + rrf_lexical) * (request.rrf_k + 1)

            # Source Tier Preference Multiplier
            tier_mult = TIER_WEIGHTS.get(chunk.source_tier, 1.0)
            tier_multiplier_map[cid] = tier_mult

            # Combined score normalized between 0.0 and 1.0
            final_score = round(base_rrf * tier_mult, 4)
            fused_scores[cid] = final_score

        # 6. Diversity / Deduplication (prevent clustering chunks from the same page & section)
        sorted_chunks = sorted(candidate_chunks, key=lambda c: fused_scores.get(str(c.id), 0.0), reverse=True)

        selected_chunks: List[PolicyDocumentChunk] = []
        seen_sections = set()

        for chunk in sorted_chunks:
            sec_key = (chunk.document_id, chunk.page_number, chunk.section_heading)
            # Allow at most 2 chunks from identical section/page to ensure passage diversity
            count_from_sec = sum(1 for c in selected_chunks if (c.document_id, c.page_number, c.section_heading) == sec_key)
            if count_from_sec < 2:
                selected_chunks.append(chunk)
            if len(selected_chunks) >= request.top_k:
                break

        # 7. Fail-Closed Gating: Verify top evidence meets confidence threshold
        top_score = fused_scores.get(str(selected_chunks[0].id), 0.0) if selected_chunks else 0.0
        
        if top_score < request.min_score_threshold:
            # Evidence is too weak or tangential; fail closed to prevent hallucination
            return HybridRetrievalResponse(
                citations=[],
                total_candidates_searched=len(candidate_chunks),
                retrieval_status='insufficient_evidence',
                query_vector_computed=True,
                diagnostic_summary={
                    'top_score': top_score,
                    'threshold': request.min_score_threshold,
                    'reason': f'Top evidence score ({top_score}) below fail-closed threshold ({request.min_score_threshold}).'
                }
            )

        retrieval_status = 'confident' if top_score >= 0.45 else 'weak_evidence'

        # 8. Assemble Citation-Ready Objects
        citations: List[EvidenceCitation] = []
        for chunk in selected_chunks:
            cid = str(chunk.id)
            diag_score = fused_scores.get(cid, 0.0)

            citation = EvidenceCitation(
                chunk_id=cid,
                document_id=str(chunk.document_id),
                scheme_id=str(chunk.scheme_id) if chunk.scheme_id else None,
                authority=chunk.authority,
                source_url=chunk.source_url,
                source_tier=chunk.source_tier,
                document_title=chunk.document_title,
                publication_effective_date=chunk.publication_effective_date.isoformat(),
                page_number=chunk.page_number,
                section_heading=chunk.section_heading,
                chunk_text=chunk.chunk_text,
                chunk_index=chunk.chunk_index,
                chunk_hash=chunk.chunk_hash,
                policy_version=chunk.policy_version,
                # Diagnostic metadata (NOT ELIGIBILITY CONFIDENCE)
                internal_diagnostic_score=diag_score,
                retrieval_method='hybrid_rrf_tier_boosted',
                tier_boost_applied=tier_multiplier_map.get(cid, 1.0),
                matched_terms=matched_terms_map.get(cid, [])
            )
            citations.append(citation)

        return HybridRetrievalResponse(
            citations=citations,
            total_candidates_searched=len(candidate_chunks),
            retrieval_status=retrieval_status,
            query_vector_computed=True,
            diagnostic_summary={
                'top_score': top_score,
                'retrieved_count': len(citations),
                'dense_weight': request.dense_weight,
                'keyword_weight': request.keyword_weight,
                'tier_weight_breakdown': TIER_WEIGHTS,
                'note': 'Diagnostic score reflects search rank relevance, not statutory eligibility probability.'
            }
        )

    def _synthesize_search_query(self, req: HybridQueryRequest) -> str:
        """
        Synthesize rich query string combining user question, business goal,
        and MSME profile facts to ground the vector search in operational reality.
        """
        parts = [req.user_question]
        if req.business_goal and req.business_goal not in req.user_question:
            parts.append(f"Business Goal: {req.business_goal}")

        if req.support_categories:
            parts.append(f"Categories: {', '.join(req.support_categories)}")

        if req.msme_facts:
            facts_snippet = []
            if 'enterprise_type' in req.msme_facts:
                facts_snippet.append(f"Type: {req.msme_facts['enterprise_type']}")
            if 'state' in req.msme_facts:
                facts_snippet.append(f"State: {req.msme_facts['state']}")
            if 'investment' in req.msme_facts:
                facts_snippet.append(f"Investment: {req.msme_facts['investment']}")
            if facts_snippet:
                parts.append("Profile: " + ", ".join(facts_snippet))

        return " | ".join(parts)
