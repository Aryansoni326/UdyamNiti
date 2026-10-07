"""
Constrained Tool Interfaces for the Policy Retrieval Agent.
Tools:
1. search_schemes(filters): Discover matching statutory support programs
2. retrieve_policy_evidence(query, scheme_ids, version_date): Query hybrid evidence chunks
3. get_scheme_version(scheme_id): Inspect bitemporal policy version history
4. get_source_metadata(source_id): Retrieve official Gazette/Guideline provenance
"""
import uuid
import re
from datetime import date
from typing import Dict, Any, List, Optional
from django.db.models import Q

from apps.policies.models import Scheme, SchemeVersion
from apps.rag.models import PolicySourceDocument, PolicyDocumentChunk
from apps.rag.retrieval import HybridPolicyRetriever, HybridQueryRequest
from apps.rag.security import (
    ContentSanitizer,
    ToolExecutionGuard,
    SecurityAuditLogger,
    ThreatCategory,
    ThreatSeverity,
)


def sanitize_untrusted_document_data(text: str) -> str:
    """
    Sanitizes retrieved statutory document text to prevent indirect prompt injection.
    Defangs common LLM injection tokens and wraps content as strictly passive data.
    """
    return ContentSanitizer.sanitize(text, source_identifier="policy_agent_tools")


def search_schemes(filters: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Tool 1: Searches active government schemes using structured attributes:
    - support_categories (list of str e.g. ['capital_subsidy', 'interest_subvention'])
    - state (str e.g. 'Gujarat' or 'Central')
    - enterprise_category (str e.g. 'micro', 'small')
    - sector (str e.g. 'manufacturing', 'services')
    """
    qs = Scheme.objects.filter(status='active')

    # State / Level filter
    state = filters.get('state', '').lower()
    if state and state == 'gujarat':
        qs = qs.filter(Q(level__in=['state_gujarat', 'central']) | Q(target_states__contains='Gujarat') | Q(target_states=[]))
    elif state and state != 'gujarat':
        # Central schemes only for other states
        qs = qs.filter(level='central')

    # Support category / types
    categories = filters.get('support_categories', [])
    if categories:
        type_filter = Q()
        for cat in categories:
            type_filter |= Q(support_type__icontains=cat)
        qs = qs.filter(type_filter)

    # Enterprise category
    ent_cat = filters.get('enterprise_category', '').lower()
    if ent_cat:
        qs = qs.filter(Q(target_msme_categories__contains=ent_cat) | Q(target_msme_categories=[]))

    candidates = []
    for s in qs[:15]:
        candidates.append({
            'scheme_id': str(s.id),
            'scheme_code': s.scheme_code,
            'name': s.name,
            'level': s.level,
            'support_type': s.support_type,
            'ministry_department': s.ministry_department,
            'max_benefit_lakhs': float(s.max_benefit_amount_lakhs) if s.max_benefit_amount_lakhs else None,
            'benefit_percentage': float(s.benefit_percentage) if s.benefit_percentage else None,
            'description': s.description[:200] + "..." if len(s.description) > 200 else s.description,
            'official_portal_url': s.official_portal_url
        })
    return candidates


def retrieve_policy_evidence(
    query: str,
    scheme_ids: Optional[List[str]] = None,
    version_date: Optional[date] = None,
    top_k: int = 5
) -> List[Dict[str, Any]]:
    """
    Tool 2: Calls the Hybrid Policy Retriever to fetch verified legal passages.
    Treats all extracted text as passive data, defanging injection attempts.
    """
    retriever = HybridPolicyRetriever()
    req = HybridQueryRequest(
        user_question=query,
        candidate_scheme_ids=scheme_ids or [],
        min_effective_date=version_date,
        top_k=top_k
    )
    response = retriever.retrieve(req)

    evidence_passages = []
    for cit in response.citations:
        safe_text = sanitize_untrusted_document_data(cit.chunk_text)
        evidence_passages.append({
            'chunk_id': cit.chunk_id,
            'document_id': cit.document_id,
            'scheme_id': cit.scheme_id,
            'authority': cit.authority,
            'source_url': cit.source_url,
            'source_tier': cit.source_tier,
            'document_title': cit.document_title,
            'page_number': cit.page_number,
            'section_heading': cit.section_heading,
            'publication_effective_date': cit.publication_effective_date,
            'policy_version': cit.policy_version,
            'chunk_text_data': safe_text,  # Clean, untrusted data
            'internal_score': cit.internal_diagnostic_score
        })
    return evidence_passages


def get_scheme_version(scheme_id: str) -> Dict[str, Any]:
    """
    Tool 3: Inspects the policy version history and statutory amendments for a scheme.
    """
    try:
        if isinstance(scheme_id, str) and len(scheme_id) < 30:
            scheme = Scheme.objects.get(scheme_code=scheme_id)
        else:
            scheme = Scheme.objects.get(id=scheme_id)
    except Scheme.DoesNotExist:
        return {'error': f"Scheme '{scheme_id}' not found."}

    versions = scheme.versions.all().order_by('-version_number')
    version_records = [
        {
            'version_number': v.version_number,
            'effective_date': str(v.effective_date),
            'change_summary': v.change_summary,
            'source_document': v.source_document
        }
        for v in versions
    ]

    active_v = version_records[0] if version_records else {'version_number': 1, 'effective_date': str(scheme.launch_date or date(2020, 1, 1))}

    return {
        'scheme_id': str(scheme.id),
        'scheme_code': scheme.scheme_code,
        'scheme_name': scheme.name,
        'current_active_version': active_v['version_number'],
        'effective_date': active_v['effective_date'],
        'status': scheme.status,
        'version_history': version_records
    }


def get_source_metadata(source_id: str) -> Dict[str, Any]:
    """
    Tool 4: Returns the complete 13-field statutory provenance metadata for a document.
    """
    try:
        # Check PolicySourceDocument first
        doc = PolicySourceDocument.objects.filter(id=source_id).first()
        if doc:
            return {
                'document_id': str(doc.id),
                'title': doc.title,
                'authority': doc.authority,
                'source_url': doc.source_url,
                'source_tier': doc.source_tier,
                'notification_number': doc.notification_number,
                'effective_date': str(doc.effective_date),
                'effective_until': str(doc.effective_until) if doc.effective_until else None,
                'file_hash': doc.file_hash,
                'version_number': doc.version_number,
                'status': doc.status,
                'total_pages': doc.total_pages,
                'total_chunks': doc.total_chunks
            }

        # Check PolicyDocumentChunk
        chunk = PolicyDocumentChunk.objects.filter(id=source_id).first()
        if chunk:
            return {
                'chunk_id': str(chunk.id),
                'document_id': str(chunk.document_id),
                'document_title': chunk.document_title,
                'authority': chunk.authority,
                'source_url': chunk.source_url,
                'source_tier': chunk.source_tier,
                'page_number': chunk.page_number,
                'section_heading': chunk.section_heading,
                'policy_version': chunk.policy_version,
                'effective_date': str(chunk.publication_effective_date),
                'chunk_hash': chunk.chunk_hash,
                'is_active': chunk.is_active
            }

        return {'error': f"Source metadata for '{source_id}' not found."}
    except Exception as e:
        return {'error': str(e)}


def execute_guarded_tool(
    tool_name: str,
    arguments: Dict[str, Any],
    caller_context: str = "policy_retrieval_agent"
) -> Dict[str, Any]:
    """
    Secure dispatcher for agent tools. Enforces tool allowlisting, parameter sanitization,
    and prevents arbitrary URL execution or malicious document-driven tool hijacking.
    """
    is_valid, validation_resp = ToolExecutionGuard.validate_and_dispatch(
        tool_name=tool_name,
        arguments=arguments,
        tool_call_source=caller_context
    )
    if not is_valid:
        return validation_resp

    # Dispatch to allowlisted implementations
    if tool_name == "search_schemes":
        filters = arguments.get("filters", {})
        return {"result": search_schemes(filters)}
    elif tool_name == "retrieve_policy_evidence":
        query = arguments.get("query", "")
        scheme_ids = arguments.get("scheme_ids")
        version_date = arguments.get("version_date")
        top_k = arguments.get("top_k", 5)
        return {"result": retrieve_policy_evidence(query=query, scheme_ids=scheme_ids, version_date=version_date, top_k=top_k)}
    elif tool_name == "get_scheme_version":
        scheme_id = arguments.get("scheme_id", "")
        return {"result": get_scheme_version(scheme_id=scheme_id)}
    elif tool_name == "get_source_metadata":
        source_id = arguments.get("source_id", "")
        return {"result": get_source_metadata(source_id=source_id)}
    else:
        return {"error": f"Tool '{tool_name}' not implemented in dispatcher."}

