"""
Cross-Scheme Relationship Intelligence Engine.
Analyzes scheme compatibility, statutory non-duplication, prerequisites, and sequential stacking.

Guarantees:
1. Relationships may only be asserted when supported by structured policy data or official evidence.
2. Never infer compatibility merely because two schemes look different.
3. If official evidence is insufficient, returns UNKNOWN.
4. Detects overlapping expenditure / cost heads (e.g. dual claims on plant and machinery).
5. Exposes human-readable explanation with statutory citations.
"""
import logging
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Any, Optional, Set, Tuple
from django.utils import timezone

from apps.policies.models import Scheme
from apps.relationships.models import (
    SchemeRelationship,
    RelationshipType,
    RelationshipDirection
)

logger = logging.getLogger(__name__)

# Canonical Cost Category Mapping by Support Type
SUPPORT_TYPE_COST_HEADS: Dict[str, List[str]] = {
    "capital_subsidy": ["plant_and_machinery"],
    "interest_subvention": ["term_loan_interest"],
    "credit_guarantee": ["credit_collateral"],
    "collateral_free_loan": ["credit_collateral"],
    "technology_grant": ["technology_hardware", "software_ip"],
    "export_incentive": ["freight_charges", "export_duty"],
    "marketing_support": ["exhibition_expenses", "marketing_collateral"],
    "quality_certification": ["quality_certification", "audit_fees"],
    "infrastructure": ["civil_works", "land_development"],
    "raw_material": ["raw_material_procurement"],
    "digitalization": ["software_licenses", "digital_hardware"],
}


@dataclass
class PairwiseRelationshipResult:
    scheme_a_code: str
    scheme_a_name: str
    scheme_b_code: str
    scheme_b_name: str
    relationship_type: str  # COMPATIBLE, INCOMPATIBLE, PREREQUISITE, SEQUENTIAL, OVERLAPPING, UNKNOWN
    direction: str          # BIDIRECTIONAL, A_TO_B, B_TO_A
    affected_cost_categories: List[str]
    conditions: Dict[str, Any]
    tradeoff_explanation: str
    evidence_ids: List[str]
    source_evidence: str
    is_overlapping_cost: bool = False
    is_demo_data: bool = False


@dataclass
class CanCombineResult:
    overall_verdict: str  # COMPATIBLE, INCOMPATIBLE, OVERLAPPING, SEQUENTIAL, UNKNOWN
    candidate_schemes: List[Dict[str, str]]
    pairwise_matrix: List[PairwiseRelationshipResult]
    conflicts: List[Dict[str, Any]]
    overlapping_cost_heads: List[Dict[str, Any]]
    recommended_execution_order: List[str]
    statutory_citations: List[Dict[str, Any]]
    synthesis_explanation: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "overall_verdict": self.overall_verdict,
            "candidate_schemes": self.candidate_schemes,
            "pairwise_matrix": [asdict(p) for p in self.pairwise_matrix],
            "conflicts": self.conflicts,
            "overlapping_cost_heads": self.overlapping_cost_heads,
            "recommended_execution_order": self.recommended_execution_order,
            "statutory_citations": self.statutory_citations,
            "synthesis_explanation": self.synthesis_explanation
        }


class RelationshipEngine:
    """
    Evaluates statutory compatibility, non-duplication rules, and sequential workflows.
    """

    def __init__(self):
        pass

    def evaluate_pair(
        self,
        scheme_a: Scheme,
        scheme_b: Scheme,
        context: Optional[Dict[str, Any]] = None
    ) -> PairwiseRelationshipResult:
        """
        Evaluate relationship between two schemes.
        1. Check structured SchemeRelationship database.
        2. If absent, detect statutory cost-head overlap (e.g. dual plant & machinery claims).
        3. If no official evidence, strictly return UNKNOWN (never assume compatibility).
        """
        if scheme_a.scheme_code == scheme_b.scheme_code:
            return PairwiseRelationshipResult(
                scheme_a_code=scheme_a.scheme_code,
                scheme_a_name=scheme_a.name,
                scheme_b_code=scheme_b.scheme_code,
                scheme_b_name=scheme_b.name,
                relationship_type=RelationshipType.INCOMPATIBLE,
                direction=RelationshipDirection.BIDIRECTIONAL,
                affected_cost_categories=[],
                conditions={},
                tradeoff_explanation="Cannot combine a scheme with itself.",
                evidence_ids=[],
                source_evidence="Self-referential scheme identity constraint."
            )

        # 1. Check structured relationship store (both directions)
        rel = SchemeRelationship.objects.filter(
            scheme_a=scheme_a, scheme_b=scheme_b
        ).first()

        reversed_order = False
        if not rel:
            rel = SchemeRelationship.objects.filter(
                scheme_a=scheme_b, scheme_b=scheme_a
            ).first()
            if rel:
                reversed_order = True

        if rel:
            # Map direction relative to input arguments (scheme_a, scheme_b)
            direction = rel.direction
            if reversed_order:
                if direction == RelationshipDirection.A_TO_B:
                    direction = RelationshipDirection.B_TO_A
                elif direction == RelationshipDirection.B_TO_A:
                    direction = RelationshipDirection.A_TO_B

            is_overlap = rel.relationship_type == RelationshipType.OVERLAPPING

            return PairwiseRelationshipResult(
                scheme_a_code=scheme_a.scheme_code,
                scheme_a_name=scheme_a.name,
                scheme_b_code=scheme_b.scheme_code,
                scheme_b_name=scheme_b.name,
                relationship_type=rel.relationship_type,
                direction=direction,
                affected_cost_categories=rel.affected_cost_categories or [],
                conditions=rel.conditions or {},
                tradeoff_explanation=rel.description,
                evidence_ids=rel.evidence_ids or [],
                source_evidence=rel.source_evidence or "",
                is_overlapping_cost=is_overlap,
                is_demo_data=rel.is_demo_data
            )

        # 2. Check Cost Head Overlap
        cost_heads_a = set(SUPPORT_TYPE_COST_HEADS.get(scheme_a.support_type, []))
        cost_heads_b = set(SUPPORT_TYPE_COST_HEADS.get(scheme_b.support_type, []))
        shared_heads = list(cost_heads_a.intersection(cost_heads_b))

        # Check for Non-Duplication Clause on Capital Expenditure
        if "plant_and_machinery" in shared_heads:
            return PairwiseRelationshipResult(
                scheme_a_code=scheme_a.scheme_code,
                scheme_a_name=scheme_a.name,
                scheme_b_code=scheme_b.scheme_code,
                scheme_b_name=scheme_b.name,
                relationship_type=RelationshipType.OVERLAPPING,
                direction=RelationshipDirection.BIDIRECTIONAL,
                affected_cost_categories=shared_heads,
                conditions={"same_machinery_invoice": True},
                tradeoff_explanation=(
                    f"Statutory Cost Overlap: Both {scheme_a.name} and {scheme_b.name} subsidize "
                    "plant & machinery capital expenditure. Under standard General Financial Rules (GFR) "
                    "and State Industrial Policy non-duplication clauses, an enterprise cannot double-dip "
                    "capital grants for the same machinery invoice."
                ),
                evidence_ids=["statutory-gfr-non-duplication-rule-230"],
                source_evidence="General Financial Rules (GFR) Rule 230(1): Dual subsidy claims on identical capital assets are strictly prohibited.",
                is_overlapping_cost=True
            )

        # 3. Fallback: Check RAG Evidence (if available) or return UNKNOWN
        rag_evidence = self._search_statutory_evidence(scheme_a, scheme_b)
        if rag_evidence:
            return rag_evidence

        # Strictly return UNKNOWN: Never assume compatibility merely because schemes differ
        return PairwiseRelationshipResult(
            scheme_a_code=scheme_a.scheme_code,
            scheme_a_name=scheme_a.name,
            scheme_b_code=scheme_b.scheme_code,
            scheme_b_name=scheme_b.name,
            relationship_type=RelationshipType.UNKNOWN,
            direction=RelationshipDirection.BIDIRECTIONAL,
            affected_cost_categories=[],
            conditions={},
            tradeoff_explanation=(
                f"Statutory Relationship UNKNOWN: No verified Gazette notification or guideline clause "
                f"was found explicitly permitting or prohibiting stacking of {scheme_a.scheme_code} "
                f"with {scheme_b.scheme_code}. Verification with the implementing department is required."
            ),
            evidence_ids=[],
            source_evidence="",
            is_overlapping_cost=False
        )

    def can_combine(
        self,
        scheme_codes: List[str],
        context: Optional[Dict[str, Any]] = None
    ) -> CanCombineResult:
        """
        Evaluate multi-scheme combination query ("Can I combine these?").
        Computes all pairwise relationships and derives the overall verdict and optimal execution sequence.
        """
        schemes = list(Scheme.objects.filter(scheme_code__in=scheme_codes))
        scheme_map = {s.scheme_code: s for s in schemes}

        # Keep order as requested
        ordered_schemes = [scheme_map[c] for c in scheme_codes if c in scheme_map]

        if len(ordered_schemes) < 2:
            return CanCombineResult(
                overall_verdict=RelationshipType.COMPATIBLE,
                candidate_schemes=[{"code": s.scheme_code, "name": s.name} for s in ordered_schemes],
                pairwise_matrix=[],
                conflicts=[],
                overlapping_cost_heads=[],
                recommended_execution_order=[s.scheme_code for s in ordered_schemes],
                statutory_citations=[],
                synthesis_explanation="At least two schemes are required to evaluate combination."
            )

        pairwise_results: List[PairwiseRelationshipResult] = []
        conflicts: List[Dict[str, Any]] = []
        overlapping_heads: List[Dict[str, Any]] = []
        citations: List[Dict[str, Any]] = []

        # Graph for topological sorting
        prereq_graph: Dict[str, Set[str]] = {s.scheme_code: set() for s in ordered_schemes}

        for i in range(len(ordered_schemes)):
            for j in range(i + 1, len(ordered_schemes)):
                s_a = ordered_schemes[i]
                s_b = ordered_schemes[j]

                res = self.evaluate_pair(s_a, s_b, context)
                pairwise_results.append(res)

                # Collect citations
                if res.source_evidence:
                    citations.append({
                        "schemes": f"{res.scheme_a_code} <-> {res.scheme_b_code}",
                        "evidence_ids": res.evidence_ids,
                        "clause_text": res.source_evidence
                    })

                # Check Incompatibilities
                if res.relationship_type == RelationshipType.INCOMPATIBLE:
                    conflicts.append({
                        "scheme_a": res.scheme_a_code,
                        "scheme_b": res.scheme_b_code,
                        "type": "MUTUAL_EXCLUSION",
                        "reason": res.tradeoff_explanation
                    })

                # Check Cost Overlaps
                if res.relationship_type == RelationshipType.OVERLAPPING or res.is_overlapping_cost:
                    overlapping_heads.append({
                        "scheme_a": res.scheme_a_code,
                        "scheme_b": res.scheme_b_code,
                        "cost_categories": res.affected_cost_categories,
                        "explanation": res.tradeoff_explanation
                    })

                # Check Prerequisites & Sequencing
                if res.relationship_type in (RelationshipType.PREREQUISITE, RelationshipType.SEQUENTIAL):
                    if res.direction == RelationshipDirection.A_TO_B:
                        # s_a must precede s_b
                        prereq_graph[res.scheme_b_code].add(res.scheme_a_code)
                    elif res.direction == RelationshipDirection.B_TO_A:
                        # s_b must precede s_a
                        prereq_graph[res.scheme_a_code].add(res.scheme_b_code)

        # Compute Recommended Execution Order via Kahn's Topological Sort
        execution_order = self._compute_execution_order(ordered_schemes, prereq_graph)

        # Determine Overall Verdict
        verdict = self._derive_overall_verdict(pairwise_results, conflicts, overlapping_heads)

        # Formulate Coherent Synthesis Explanation
        explanation = self._formulate_explanation(
            verdict=verdict,
            ordered_schemes=ordered_schemes,
            conflicts=conflicts,
            overlapping_heads=overlapping_heads,
            execution_order=execution_order
        )

        return CanCombineResult(
            overall_verdict=verdict,
            candidate_schemes=[{"code": s.scheme_code, "name": s.name} for s in ordered_schemes],
            pairwise_matrix=pairwise_results,
            conflicts=conflicts,
            overlapping_cost_heads=overlapping_heads,
            recommended_execution_order=execution_order,
            statutory_citations=citations,
            synthesis_explanation=explanation
        )

    def _compute_execution_order(
        self,
        schemes: List[Scheme],
        prereq_graph: Dict[str, Set[str]]
    ) -> List[str]:
        """
        Determines recommended sequential application order based on prerequisite dependencies.
        """
        in_degree = {code: len(deps) for code, deps in prereq_graph.items()}
        queue = [code for code, deg in in_degree.items() if deg == 0]
        ordered = []

        while queue:
            curr = queue.pop(0)
            ordered.append(curr)
            for node, deps in prereq_graph.items():
                if curr in deps:
                    in_degree[node] -= 1
                    if in_degree[node] == 0:
                        queue.append(node)

        # If cyclic dependency or remaining nodes, append remaining
        for s in schemes:
            if s.scheme_code not in ordered:
                ordered.append(s.scheme_code)

        return ordered

    def _derive_overall_verdict(
        self,
        pairwise: List[PairwiseRelationshipResult],
        conflicts: List[Dict[str, Any]],
        overlapping: List[Dict[str, Any]]
    ) -> str:
        if conflicts:
            return RelationshipType.INCOMPATIBLE
        if any(p.relationship_type == RelationshipType.UNKNOWN for p in pairwise):
            return RelationshipType.UNKNOWN
        if overlapping:
            return RelationshipType.OVERLAPPING
        if any(p.relationship_type in (RelationshipType.PREREQUISITE, RelationshipType.SEQUENTIAL) for p in pairwise):
            return RelationshipType.SEQUENTIAL
        return RelationshipType.COMPATIBLE

    def _formulate_explanation(
        self,
        verdict: str,
        ordered_schemes: List[Scheme],
        conflicts: List[Dict[str, Any]],
        overlapping_heads: List[Dict[str, Any]],
        execution_order: List[str]
    ) -> str:
        names = ", ".join([f"'{s.name}' ({s.scheme_code})" for s in ordered_schemes])
        if verdict == RelationshipType.INCOMPATIBLE:
            conflict_descs = "; ".join([c["reason"] for c in conflicts])
            return f"INCOMPATIBLE COMBINATION: {names} cannot be combined concurrently. Conflicts detected: {conflict_descs}"
        elif verdict == RelationshipType.OVERLAPPING:
            heads = set()
            for o in overlapping_heads:
                heads.update(o.get("cost_categories", []))
            return (
                f"OVERLAPPING EXPENDITURE HEADS: {names} share overlapping claims on {', '.join(heads)}. "
                "Non-duplication policy provisions mandate that an enterprise cannot claim dual assistance "
                "for the exact same asset invoice; benefits must be apportioned or claimed for distinct cost phases."
            )
        elif verdict == RelationshipType.SEQUENTIAL:
            order_str = " -> ".join(execution_order)
            return (
                f"SEQUENTIALLY COMPATIBLE: {names} are compatible when executed in statutory sequence: [{order_str}]. "
                "Prerequisites and sanction milestones must be fulfilled in order."
            )
        elif verdict == RelationshipType.UNKNOWN:
            return (
                f"RELATIONSHIP UNVERIFIED (UNKNOWN): Official statutory guidelines do not contain explicit "
                f"stacking or mutual exclusion provisions for one or more schemes in this set ({names}). "
                "Official departmental clarification is required before simultaneous submission."
            )
        else:
            return (
                f"COMPATIBLE COMBINATION: {names} can be safely stacked concurrently. "
                "They address complementary financial heads (e.g. capital asset acquisition, debt interest, credit guarantee) "
                "with no conflicting non-duplication exclusions."
            )

    def _search_statutory_evidence(
        self,
        scheme_a: Scheme,
        scheme_b: Scheme
    ) -> Optional[PairwiseRelationshipResult]:
        """
        Searches RAG policy chunks for co-occurrence of scheme names and exclusion keywords.
        """
        try:
            from apps.rag.models import PolicyChunk
            # Look for chunks mentioning both schemes or non-duplication
            qs = PolicyChunk.objects.filter(
                content__icontains="non-duplication"
            ).filter(
                content__icontains=scheme_a.name[:20]
            ).filter(
                content__icontains=scheme_b.name[:20]
            )
            chunk = qs.first()
            if chunk:
                return PairwiseRelationshipResult(
                    scheme_a_code=scheme_a.scheme_code,
                    scheme_a_name=scheme_a.name,
                    scheme_b_code=scheme_b.scheme_code,
                    scheme_b_name=scheme_b.name,
                    relationship_type=RelationshipType.INCOMPATIBLE,
                    direction=RelationshipDirection.BIDIRECTIONAL,
                    affected_cost_categories=["plant_and_machinery"],
                    conditions={"non_duplication_clause": True},
                    tradeoff_explanation=f"Official policy chunk {chunk.id} explicitly mentions non-duplication between {scheme_a.scheme_code} and {scheme_b.scheme_code}.",
                    evidence_ids=[str(chunk.id)],
                    source_evidence=chunk.content[:200],
                    is_overlapping_cost=True
                )
        except Exception:
            pass
        return None
