"""
Views and API Endpoints for Policy Monitoring & Change Detection.
"""
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
import datetime
import uuid

from apps.policies.models import Scheme
from .models import PolicyChange, ReviewStatus
from .diff_service import PolicyDiffPipelineService


@api_view(['POST'])
def execute_policy_diff(request):
    """
    Execute policy diff pipeline between old and new scheme definitions.
    Request body:
    {
      "scheme_code": "GJ-CAPITAL-2025",
      "old_policy_data": {...},
      "new_policy_data": {...},
      "evidence_source": "Resolution Clause 4.1",
      "effective_date": "2026-04-01",
      "confidence_of_extraction": 0.98,
      "async": false
    }
    """
    scheme_code = request.data.get('scheme_code')
    old_data = request.data.get('old_policy_data', {})
    new_data = request.data.get('new_policy_data', {})
    evidence_source = request.data.get('evidence_source', 'Statutory Notification')
    effective_date_str = request.data.get('effective_date')
    confidence = float(request.data.get('confidence_of_extraction', 1.0))
    run_async = request.data.get('async', False)

    scheme = get_object_or_404(Scheme, scheme_code=scheme_code)
    eff_date = datetime.date.fromisoformat(effective_date_str) if effective_date_str else datetime.date.today()

    if run_async:
        from .tasks import detect_policy_changes_task
        task = detect_policy_changes_task.delay(
            scheme_code=scheme_code,
            old_policy_data=old_data,
            new_policy_data=new_data,
            evidence_source=evidence_source,
            effective_date_str=eff_date.isoformat(),
            confidence_of_extraction=confidence
        )
        return Response({
            "message": "Policy diff task enqueued asynchronously.",
            "task_id": task.id
        }, status=status.HTTP_202_ACCEPTED)

    changes = PolicyDiffPipelineService.execute_diff_pipeline(
        scheme=scheme,
        old_policy_data=old_data,
        new_policy_data=new_data,
        evidence_source=evidence_source,
        effective_date=eff_date,
        confidence_of_extraction=confidence,
        persist=True
    )

    data = [{
        "id": str(c.id),
        "scheme_code": c.scheme.scheme_code,
        "change_type": c.change_type,
        "materiality": c.materiality,
        "summary": c.change_summary,
        "old_value": c.old_value,
        "new_value": c.new_value,
        "affected_rule_ids": c.affected_rule_ids,
        "effective_date": str(c.effective_date) if c.effective_date else None,
        "evidence_source": c.evidence_source,
        "confidence_of_extraction": c.confidence_of_extraction,
        "requires_human_review": c.requires_human_review,
        "review_status": c.review_status
    } for c in changes]

    return Response({
        "scheme_code": scheme_code,
        "total_changes_detected": len(changes),
        "changes": data
    }, status=status.HTTP_200_OK)


@api_view(['GET'])
def policy_changes_list(request):
    """
    List detected policy changes with optional filters:
    - scheme_code
    - materiality: material / informational
    - review_status: pending_review / approved_active / rejected
    """
    qs = PolicyChange.objects.select_related('scheme').all()

    scheme_code = request.query_params.get('scheme_code')
    if scheme_code:
        qs = qs.filter(scheme__scheme_code=scheme_code)

    materiality = request.query_params.get('materiality')
    if materiality:
        qs = qs.filter(materiality=materiality.lower())

    review_status = request.query_params.get('review_status')
    if review_status:
        qs = qs.filter(review_status=review_status.lower())

    data = [{
        'id': str(c.id),
        'scheme_code': c.scheme.scheme_code,
        'scheme_name': c.scheme.name,
        'change_type': c.change_type,
        'materiality': c.materiality,
        'summary': c.change_summary,
        'change_summary': c.change_summary,
        'old_value': c.old_value,
        'new_value': c.new_value,
        'affected_rule_ids': c.affected_rule_ids,
        'effective_date': str(c.effective_date) if c.effective_date else None,
        'evidence_source': c.evidence_source,
        'source': c.evidence_source,
        'confidence_of_extraction': c.confidence_of_extraction,
        'requires_human_review': c.requires_human_review,
        'review_status': c.review_status,
        'reviewed_by': c.reviewed_by,
        'reviewed_at': c.reviewed_at.isoformat() if c.reviewed_at else None,
        'detected_at': c.detected_at.isoformat(),
    } for c in qs[:50]]

    return Response({'count': len(data), 'results': data}, status=status.HTTP_200_OK)


@api_view(['POST'])
def approve_policy_change(request, pk):
    """Curator action to approve a detected policy change."""
    change = get_object_or_404(PolicyChange, pk=pk)
    curator_name = request.data.get('curator_name', 'admin_curator')
    change.approve(curator_name=curator_name)
    return Response({
        "id": str(change.id),
        "review_status": change.review_status,
        "reviewed_by": change.reviewed_by,
        "reviewed_at": change.reviewed_at.isoformat()
    }, status=status.HTTP_200_OK)


@api_view(['POST'])
def reject_policy_change(request, pk):
    """Curator action to reject a detected policy change."""
    change = get_object_or_404(PolicyChange, pk=pk)
    curator_name = request.data.get('curator_name', 'admin_curator')
    change.reject(curator_name=curator_name)
    return Response({
        "id": str(change.id),
        "review_status": change.review_status,
        "reviewed_by": change.reviewed_by,
        "reviewed_at": change.reviewed_at.isoformat()
    }, status=status.HTTP_200_OK)


from .impact_service import PersonalizedImpactService
from .models import ImpactEvaluation


@api_view(['POST'])
def evaluate_change_impact(request):
    """
    Run personalized impact re-evaluation pipeline for an approved policy change.
    Request body:
    {
      "policy_change_id": "uuid"
    }
    """
    change_id = request.data.get('policy_change_id')
    if not change_id:
        return Response({"error": "policy_change_id is required."}, status=status.HTTP_400_BAD_REQUEST)

    change = get_object_or_404(PolicyChange, pk=change_id)
    impacts = PersonalizedImpactService.process_policy_change_impact(change, persist=True)

    return Response({
        "policy_change_id": str(change.id),
        "scheme_code": change.scheme.scheme_code,
        "total_impacted_profiles": len(impacts),
        "impacts": [imp.to_dict() for imp in impacts]
    }, status=status.HTTP_200_OK)


@api_view(['GET'])
def profile_impact_list(request, profile_id):
    """
    List all personalized policy impact notices for a specific business profile.
    """
    impacts = ImpactEvaluation.objects.filter(
        business_profile_id=profile_id
    ).select_related('policy_change__scheme').order_by('-created_at')

    return Response({
        "business_profile_id": str(profile_id),
        "count": impacts.count(),
        "impact_notices": [imp.to_dict() for imp in impacts]
    }, status=status.HTTP_200_OK)


@api_view(['POST'])
def simulate_demo_impact(request):
    """
    Demo simulation mode: evaluates a hypothetical policy change (e.g. turnover limit ₹5 Cr -> ₹10 Cr)
    across stored profiles in memory without making permanent database changes.
    Request body:
    {
      "scheme_code": "GJ-CAPITAL-2025",
      "simulated_change": {
        "change_type": "thresholds",
        "change_summary": "Turnover threshold expanded from 5 Cr to 10 Cr",
        "old_value": {"expected_value": 500.0},
        "new_value": {"expected_value": 1000.0},
        "evidence_source": "Gujarat Budget Announcement 2026"
      }
    }
    """
    scheme_code = request.data.get('scheme_code')
    simulated_change = request.data.get('simulated_change', {})

    if not scheme_code:
        return Response({"error": "scheme_code is required."}, status=status.HTTP_400_BAD_REQUEST)

    trace_id = (
        request.META.get('HTTP_X_CORRELATION_ID') or
        request.META.get('HTTP_X_TRACE_ID') or
        getattr(request, 'trace_id', None) or
        getattr(request, 'correlation_id', None) or
        f"trc_sim_{uuid.uuid4().hex[:8]}"
    )

    res = PersonalizedImpactService.simulate_demo_impact(
        scheme_code=scheme_code,
        simulated_change=simulated_change
    )
    res['correlation_id'] = trace_id
    res['trace_id'] = trace_id

    response = Response(res, status=status.HTTP_200_OK)
    response['X-Correlation-ID'] = trace_id
    response['X-Trace-ID'] = trace_id
    return response
