"""
Celery asynchronous tasks for official document RAG ingestion.
Provides idempotent execution, retry backoff, and distributed locking.
"""
import logging
from celery import shared_task
from django.db import transaction

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def ingest_policy_document_task(self, doc_id: str, force: bool = False):
    """
    Idempotent background task to parse, chunk, embed, and publish
    an official policy source document.
    """
    from apps.rag.models import PolicySourceDocument
    from apps.rag.pipeline import RAGIngestionPipeline

    logger.info(f"Starting ingestion task for document ID: {doc_id}")

    try:
        # Atomic check-and-lock to guarantee idempotency across concurrent workers
        with transaction.atomic():
            doc = PolicySourceDocument.objects.select_for_update().get(id=doc_id)
            if doc.status == 'published' and not force:
                logger.info(f"Document {doc_id} is already published. Skipping duplicate task.")
                return {'status': 'skipped', 'doc_id': doc_id, 'reason': 'already_published'}
            if doc.status == 'processing' and not force:
                logger.warning(f"Document {doc_id} is currently being processed by another worker.")
                return {'status': 'in_progress', 'doc_id': doc_id}

        pipeline = RAGIngestionPipeline()
        processed_doc = pipeline.process_document(doc_id=doc.id, force=force)

        return {
            'status': processed_doc.status,
            'doc_id': str(processed_doc.id),
            'total_chunks': processed_doc.total_chunks,
            'quarantine_reason': processed_doc.quarantine_reason
        }

    except Exception as exc:
        logger.error(f"Error in ingest_policy_document_task for {doc_id}: {str(exc)}")
        # Retry with exponential backoff if temporary failure
        raise self.retry(exc=exc, countdown=60 * (2 ** self.request.retries))


@shared_task(bind=True)
def run_batch_ingestion_task(self, batch_id: str, documents_spec: list):
    """
    Background batch processor for bulk policy document imports.
    """
    from apps.rag.pipeline import RAGIngestionPipeline

    logger.info(f"Executing batch ingestion job: {batch_id} ({len(documents_spec)} sources)")
    pipeline = RAGIngestionPipeline()
    report = pipeline.run_batch(documents_spec, batch_id=batch_id)

    return {
        'batch_id': report.batch_id,
        'status': report.status,
        'processed': report.processed_sources,
        'quarantined': report.quarantined_sources,
        'total_chunks': report.total_chunks_created,
        'duplicates': report.duplicates_detected,
        'duration_seconds': report.duration_seconds
    }
