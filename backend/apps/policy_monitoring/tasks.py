"""
Celery Background Tasks for Policy Monitoring and Change Detection.
Executes asynchronous diffing, checksum validation, and triggers curator notifications.
"""
import logging
from celery import shared_task
from apps.policies.models import Scheme
from .diff_service import PolicyDiffPipelineService

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def detect_policy_changes_task(
    self,
    scheme_code: str,
    old_policy_data: dict,
    new_policy_data: dict,
    evidence_source: str,
    effective_date_str: str = None,
    confidence_of_extraction: float = 1.0
):
    """
    Celery task to run the Policy Diff Pipeline asynchronously.
    """
    try:
        scheme = Scheme.objects.get(scheme_code=scheme_code)
        import datetime
        eff_date = datetime.date.fromisoformat(effective_date_str) if effective_date_str else datetime.date.today()

        changes = PolicyDiffPipelineService.execute_diff_pipeline(
            scheme=scheme,
            old_policy_data=old_policy_data,
            new_policy_data=new_policy_data,
            evidence_source=evidence_source,
            effective_date=eff_date,
            confidence_of_extraction=confidence_of_extraction,
            persist=True
        )

        material_count = sum(1 for c in changes if c.materiality == 'material')
        pending_review_count = sum(1 for c in changes if c.review_status == 'pending_review')

        logger.info(
            f"Asynchronous policy diff task finished for {scheme_code}: "
            f"{len(changes)} detected, {material_count} material, {pending_review_count} pending review."
        )

        return {
            "status": "success",
            "scheme_code": scheme_code,
            "total_changes": len(changes),
            "material_changes": material_count,
            "pending_review": pending_review_count
        }

    except Exception as exc:
        logger.error(f"Error in detect_policy_changes_task for {scheme_code}: {exc}", exc_info=True)
        raise self.retry(exc=exc)
