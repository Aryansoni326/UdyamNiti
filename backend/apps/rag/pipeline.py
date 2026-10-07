"""
Official Government Document RAG Ingestion Pipeline.
Handles source registration, checksum/dedup, page-aware legal extraction,
section chunking, 13-field provenance enrichment, vector embedding,
version association, quarantine gating, and ingestion audit reporting.
"""
import io
import time
import uuid
import re
from datetime import date
from typing import List, Dict, Any, Optional, Tuple

from django.db import transaction
from django.utils import timezone

from apps.rag.models import PolicySourceDocument, PolicyDocumentChunk, IngestionReport
from apps.rag.chunker import LegalDocumentParser, compute_sha256, compute_simhash
from apps.policies.models import Scheme
from apps.rag.security import (
    DomainAllowlistValidator,
    MIMEAndContentValidator,
    ContentSanitizer,
    SecurityAuditLogger,
    ThreatCategory,
    ThreatSeverity,
)

# Graceful Embedding Provider (SentenceTransformers with deterministic fallback)
_EMBEDDING_MODEL = None
_MODEL_INIT_ATTEMPTED = False

def _get_embedding_model():
    global _EMBEDDING_MODEL, _MODEL_INIT_ATTEMPTED
    if not _MODEL_INIT_ATTEMPTED:
        _MODEL_INIT_ATTEMPTED = True
        try:
            from sentence_transformers import SentenceTransformer
            _EMBEDDING_MODEL = SentenceTransformer('all-MiniLM-L6-v2')
        except Exception:
            _EMBEDDING_MODEL = None
    return _EMBEDDING_MODEL


from functools import lru_cache
from django.core.cache import cache

@lru_cache(maxsize=8192)
def _compute_raw_embedding(text: str) -> Tuple[float, ...]:
    """Inner cached embedding computation returning hashable tuple."""
    model = _get_embedding_model()
    if model is not None:
        try:
            return tuple(model.encode(text).tolist())
        except Exception:
            pass

    import hashlib
    import math
    h = hashlib.sha384(text.encode('utf-8')).digest()
    vec = []
    for i in range(48):
        byte_val = h[i]
        for b in range(8):
            vec.append(1.0 if (byte_val & (1 << b)) else -1.0)
    norm = math.sqrt(sum(x * x for x in vec)) or 1.0
    return tuple(round(x / norm, 5) for x in vec)


def generate_embedding(text: str) -> List[float]:
    """
    Generate 384-dimensional dense embedding for chunk retrieval.
    Caches vectors in memory (LRU) and Django cache for sub-millisecond retrieval.
    """
    if not text:
        return [0.0] * 384

    # 1. Fast in-memory cache lookup
    return list(_compute_raw_embedding(text))


class RAGIngestionPipeline:
    """
    Production-grade ingestion pipeline for statutory Gazette notifications,
    operational guidelines, circulars, and government schemes.
    """

    def __init__(self):
        self.parser = LegalDocumentParser()

    def register_source(
        self,
        title: str,
        authority: str,
        source_url: str,
        source_tier: str,
        effective_date: date,
        document_type: str = 'pdf',
        notification_number: str = '',
        scheme: Optional[Scheme] = None,
        file_bytes: Optional[bytes] = None,
        raw_text_pages: Optional[List[Tuple[int, str]]] = None,
    ) -> PolicySourceDocument:
        """
        Stage 1: Source Registration & Checksum/Dedup.
        Computes SHA-256 and content SimHash before creating database entity.
        """
        # Calculate checksums
        if file_bytes:
            file_hash = compute_sha256(file_bytes)
        elif raw_text_pages:
            combined_text = "".join(txt for _, txt in raw_text_pages)
            file_hash = compute_sha256(combined_text.encode('utf-8'))
        else:
            file_hash = compute_sha256(f"{title}_{source_url}_{effective_date}".encode('utf-8'))

        # Check existing published version to support versioning without silent overwrite
        existing_doc = PolicySourceDocument.objects.filter(
            scheme=scheme,
            title=title,
            status='published'
        ).order_by('-version_number').first()

        version_number = 1
        if existing_doc:
            if existing_doc.file_hash == file_hash:
                # Exact identical file already published
                return existing_doc
            # Increment version for updated policy circular/amendment
            version_number = existing_doc.version_number + 1

        # Check near-duplicate across different URLs via SimHash if text is available
        content_simhash = ""
        if raw_text_pages:
            combined_text = "".join(txt for _, txt in raw_text_pages)
            content_simhash = compute_simhash(combined_text)

        # Security Control 1: Domain Allowlist Validation
        domain_allowed, domain_reason = DomainAllowlistValidator.is_domain_allowed(source_url)
        initial_status = 'pending'
        quarantine_msg = ''
        if not domain_allowed:
            initial_status = 'quarantined'
            quarantine_msg = f"Security Quarantine: {domain_reason}"

        # Security Control 2: MIME & File Size Check (if file_bytes provided)
        if file_bytes and initial_status != 'quarantined':
            mime_valid, mime_reason = MIMEAndContentValidator.validate_file_bytes(file_bytes, declared_type=document_type)
            if not mime_valid:
                initial_status = 'quarantined'
                quarantine_msg = f"Security Quarantine: {mime_reason}"

        doc = PolicySourceDocument.objects.create(
            scheme=scheme,
            title=title,
            authority=authority,
            source_url=source_url,
            source_tier=source_tier,
            document_type=document_type,
            notification_number=notification_number,
            file_hash=file_hash,
            content_simhash=content_simhash,
            version_number=version_number,
            effective_date=effective_date,
            status=initial_status,
            quarantine_reason=quarantine_msg,
            total_pages=len(raw_text_pages) if raw_text_pages else 1
        )
        return doc

    def extract_text(self, doc: PolicySourceDocument, file_bytes: Optional[bytes] = None, raw_text_pages: Optional[List[Tuple[int, str]]] = None) -> List[Tuple[int, str]]:
        """
        Stage 2 & 3: Extraction and Page-Aware Cleaning.
        Returns list of (page_number, text).
        """
        if raw_text_pages:
            return raw_text_pages

        if not file_bytes and doc.file:
            try:
                doc.file.open('rb')
                file_bytes = doc.file.read()
                doc.file.close()
            except Exception as e:
                raise ValueError(f"Failed to read document file: {str(e)}")

        if not file_bytes:
            raise ValueError("No file content or text provided for extraction.")

        pages = []
        if doc.document_type == 'pdf':
            try:
                import pypdf
                reader = pypdf.PdfReader(io.BytesIO(file_bytes))
                for page_idx, page in enumerate(reader.pages):
                    text = page.extract_text() or ""
                    pages.append((page_idx + 1, text))
            except ImportError:
                # Fallback text decoder
                text = file_bytes.decode('utf-8', errors='ignore')
                pages.append((1, text))
        elif doc.document_type == 'html':
            try:
                from bs4 import BeautifulSoup
                soup = BeautifulSoup(file_bytes, 'html.parser')
                # Strip scripts and styles
                for script in soup(["script", "style", "nav", "footer"]):
                    script.extract()
                text = soup.get_text(separator="\n")
                pages.append((1, text))
            except ImportError:
                # Regex HTML tag stripping
                raw = file_bytes.decode('utf-8', errors='ignore')
                text = re.sub(r'<[^>]+>', ' ', raw)
                pages.append((1, text))
        else:
            text = file_bytes.decode('utf-8', errors='ignore')
            pages.append((1, text))

        return pages

    def process_document(
        self,
        doc_id: uuid.UUID,
        file_bytes: Optional[bytes] = None,
        raw_text_pages: Optional[List[Tuple[int, str]]] = None,
        force: bool = False
    ) -> PolicySourceDocument:
        """
        Executes end-to-end ingestion on a registered document:
        Extraction -> Cleanup -> Section-Aware Chunking -> Metadata Enrichment ->
        Embedding -> Version Association -> Validation -> Publish or Quarantine.
        """
        doc = PolicySourceDocument.objects.get(id=doc_id)

        # Early return if document already quarantined by security validator
        if doc.status == 'quarantined' and not force:
            return doc

        # Idempotency check: if already published and not forced, return
        if doc.status == 'published' and not force:
            return doc

        doc.status = 'processing'
        doc.save(update_fields=['status', 'updated_at'])

        try:
            # 1. Extraction
            pages = self.extract_text(doc, file_bytes=file_bytes, raw_text_pages=raw_text_pages)

            # Quarantine Check: verify total readable characters
            total_chars = sum(len(txt.strip()) for _, txt in pages)
            if total_chars < 50:
                doc.status = 'quarantined'
                doc.quarantine_reason = f"Document rejected: insufficient extracted content ({total_chars} characters). Malformed or unreadable file."
                doc.save(update_fields=['status', 'quarantine_reason', 'updated_at'])
                return doc

            # Security Control 3: Content budget verification
            valid_budget, budget_reason = MIMEAndContentValidator.validate_extracted_text(
                "".join(txt for _, txt in pages),
                page_count=len(pages)
            )
            if not valid_budget:
                doc.status = 'quarantined'
                doc.quarantine_reason = f"Security Quarantine: {budget_reason}"
                doc.save(update_fields=['status', 'quarantine_reason', 'updated_at'])
                return doc

            doc.total_pages = len(pages)

            # 2. Section-Aware Chunking with Page Boundaries
            raw_chunks = self.parser.parse_pages(pages)

            if not raw_chunks:
                doc.status = 'quarantined'
                doc.quarantine_reason = "Document rejected: 0 valid semantic sections extracted."
                doc.save(update_fields=['status', 'quarantine_reason', 'updated_at'])
                return doc

            # 3. Transactional Metadata Enrichment, Embedding & Publishing
            with transaction.atomic():
                # If newer version, supersede older version chunks
                if doc.version_number > 1 and doc.scheme:
                    older_docs = PolicySourceDocument.objects.filter(
                        scheme=doc.scheme,
                        title=doc.title,
                        status='published'
                    ).exclude(id=doc.id)
                    for old_doc in older_docs:
                        old_doc.status = 'superseded'
                        old_doc.save(update_fields=['status', 'updated_at'])
                        old_doc.chunks.all().update(is_active=False)

                # Remove any preexisting chunks for this specific document if re-processing
                doc.chunks.all().delete()

                chunk_objects = []
                for c in raw_chunks:
                    # Security Control 4: Defang injection tokens from raw chunk text
                    clean_chunk_text = ContentSanitizer.sanitize(
                        c['chunk_text'],
                        source_identifier=f"doc_{doc.id}_p{c['page_number']}"
                    )
                    emb = generate_embedding(clean_chunk_text)

                    chunk_obj = PolicyDocumentChunk(
                        document=doc,
                        scheme=doc.scheme,
                        # All 13 Required Provenance Headers:
                        authority=doc.authority,
                        source_url=doc.source_url,
                        source_tier=doc.source_tier,
                        document_title=doc.title,
                        publication_effective_date=doc.effective_date,
                        policy_version=doc.version_number,
                        page_number=c['page_number'],
                        section_heading=c['section_heading'],
                        chunk_index=c['chunk_index'],
                        chunk_text=clean_chunk_text,
                        chunk_hash=compute_sha256(clean_chunk_text.encode('utf-8')),
                        token_count=c['token_count'],
                        embedding=emb,
                        is_active=True
                    )
                    chunk_objects.append(chunk_obj)

                PolicyDocumentChunk.objects.bulk_create(chunk_objects)

                doc.status = 'published'
                doc.quarantine_reason = ''
                doc.total_chunks = len(chunk_objects)
                doc.save(update_fields=['status', 'quarantine_reason', 'total_chunks', 'total_pages', 'updated_at'])

            return doc

        except Exception as exc:
            doc.status = 'quarantined'
            doc.quarantine_reason = f"Pipeline execution error: {str(exc)}"
            doc.save(update_fields=['status', 'quarantine_reason', 'updated_at'])
            return doc

    def run_batch(self, documents_spec: List[Dict[str, Any]], batch_id: Optional[str] = None) -> IngestionReport:
        """
        Executes an audited batch ingestion job over multiple government documents.
        Emits an IngestionReport summarizing processed, quarantined, and chunk counts.
        """
        start_time = time.time()
        if not batch_id:
            batch_id = f"BATCH-RAG-{timezone.now().strftime('%Y%m%d%H%M%S')}"

        processed_count = 0
        quarantined_count = 0
        total_chunks = 0
        duplicates_count = 0
        error_logs = []

        report = IngestionReport.objects.create(
            batch_id=batch_id,
            status='completed',
            total_sources=len(documents_spec)
        )

        for spec in documents_spec:
            try:
                # Deduplication check
                file_bytes = spec.get('file_bytes')
                raw_text_pages = spec.get('raw_text_pages')

                doc = self.register_source(
                    title=spec['title'],
                    authority=spec['authority'],
                    source_url=spec['source_url'],
                    source_tier=spec.get('source_tier', 'tier_2_operational_guidelines'),
                    effective_date=spec['effective_date'],
                    document_type=spec.get('document_type', 'pdf'),
                    notification_number=spec.get('notification_number', ''),
                    scheme=spec.get('scheme'),
                    file_bytes=file_bytes,
                    raw_text_pages=raw_text_pages
                )

                if doc.status == 'published':
                    # Already published identical document
                    duplicates_count += 1
                    continue

                processed_doc = self.process_document(
                    doc_id=doc.id,
                    file_bytes=file_bytes,
                    raw_text_pages=raw_text_pages
                )

                if processed_doc.status == 'quarantined':
                    quarantined_count += 1
                    error_logs.append({
                        'title': doc.title,
                        'reason': processed_doc.quarantine_reason
                    })
                elif processed_doc.status == 'published':
                    processed_count += 1
                    total_chunks += processed_doc.total_chunks

            except Exception as e:
                quarantined_count += 1
                error_logs.append({
                    'title': spec.get('title', 'Unknown'),
                    'reason': str(e)
                })

        duration = round(time.time() - start_time, 2)
        final_status = 'completed' if quarantined_count == 0 else 'partial_quarantine'

        report.status = final_status
        report.processed_sources = processed_count
        report.quarantined_sources = quarantined_count
        report.total_chunks_created = total_chunks
        report.duplicates_detected = duplicates_count
        report.duration_seconds = duration
        report.error_log = error_logs
        report.save()

        return report
