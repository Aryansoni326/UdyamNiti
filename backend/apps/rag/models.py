"""
RAG Ingestion Domain Models.
Guarantees verifiable provenance, document versioning, section-aware chunking,
quarantine tracking, and execution audit reports.
"""
import uuid
from django.db import models
from django.utils import timezone
from apps.policies.models import Scheme

try:
    from pgvector.django import VectorField
except ImportError:
    VectorField = None


class PolicySourceDocument(models.Model):
    """
    Official ingested government source document (Gazette, Guidelines, Circular, FAQ).
    Retains cryptographic checksums, version history, and quarantine state.
    """
    SOURCE_TIER_CHOICES = [
        ('tier_1_gazette', 'Tier 1: Gazette Notification'),
        ('tier_2_operational_guidelines', 'Tier 2: Operational Guidelines'),
        ('tier_3_ministry_circular', 'Tier 3: Ministry Circular / OM'),
        ('tier_4_portal_faq', 'Tier 4: Portal FAQ / Manual'),
    ]

    DOCUMENT_TYPE_CHOICES = [
        ('pdf', 'Portable Document Format (PDF)'),
        ('html', 'Official Web Page / Portal HTML'),
        ('notification', 'Statutory Notification'),
        ('circular', 'Executive Circular'),
        ('resolution', 'Government Resolution (G.R.)'),
        ('faq', 'Public FAQ'),
    ]

    STATUS_CHOICES = [
        ('pending', 'Pending Ingestion'),
        ('processing', 'Processing & Chunking'),
        ('published', 'Published & Active in Vector Store'),
        ('quarantined', 'Quarantined (Parsing/Validation Failure)'),
        ('superseded', 'Superseded by Newer Policy Version'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    scheme = models.ForeignKey(
        Scheme,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='source_documents',
        help_text='Associated scheme if known at ingestion time'
    )

    title = models.CharField(max_length=350, help_text='Full official title of the policy document')
    authority = models.CharField(max_length=255, help_text='Issuing ministry or department e.g. Ministry of MSME')
    source_url = models.URLField(max_length=500, help_text='Direct canonical download URL')
    source_tier = models.CharField(max_length=35, choices=SOURCE_TIER_CHOICES, default='tier_2_operational_guidelines')
    document_type = models.CharField(max_length=20, choices=DOCUMENT_TYPE_CHOICES, default='pdf')
    notification_number = models.CharField(max_length=150, blank=True)

    file = models.FileField(upload_to='policy_documents/%Y/%m/', null=True, blank=True)
    file_hash = models.CharField(max_length=64, db_index=True, help_text='SHA-256 checksum for exact deduplication')
    content_simhash = models.CharField(max_length=64, blank=True, help_text='SimHash for near-duplicate text detection')

    version_number = models.PositiveIntegerField(default=1)
    effective_date = models.DateField(help_text='Statutory date this document came into force')
    effective_until = models.DateField(null=True, blank=True, help_text='Sunset or superseded date')

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', db_index=True)
    quarantine_reason = models.TextField(blank=True, help_text='Error details if parsing or validation fails')

    total_pages = models.PositiveIntegerField(default=1)
    total_chunks = models.PositiveIntegerField(default=0)

    ingested_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'rag_policy_source_documents'
        ordering = ['-effective_date', '-ingested_at']
        indexes = [
            models.Index(fields=['file_hash']),
            models.Index(fields=['status', 'source_tier']),
            models.Index(fields=['authority', 'effective_date']),
        ]

    def __str__(self):
        return f"{self.title} (v{self.version_number}) [{self.status}]"


class PolicyDocumentChunk(models.Model):
    """
    A discrete semantic passage extracted from an official document.
    Maintains complete provenance (page, clause, authority, tier, version, and embedding).
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    document = models.ForeignKey(
        PolicySourceDocument,
        on_delete=models.CASCADE,
        related_name='chunks'
    )
    scheme = models.ForeignKey(
        Scheme,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='policy_chunks'
    )

    # Replicated Provenance Headers for Zero-Join Fast Retrieval
    authority = models.CharField(max_length=255)
    source_url = models.URLField(max_length=500)
    source_tier = models.CharField(max_length=35)
    document_title = models.CharField(max_length=350)
    publication_effective_date = models.DateField()
    policy_version = models.PositiveIntegerField(default=1)

    # Chunk Localization
    page_number = models.PositiveIntegerField(help_text='PDF page number where chunk occurs')
    section_heading = models.CharField(max_length=255, blank=True, help_text='e.g. Clause 4.2: Eligible Investment')
    chunk_index = models.PositiveIntegerField()

    chunk_text = models.TextField()
    chunk_hash = models.CharField(max_length=64, help_text='SHA-256 hash of the chunk text')
    token_count = models.PositiveIntegerField(default=0)

    # Dense Vector Embedding (384 dimensions)
    embedding = VectorField(dimensions=384, null=True, blank=True) if VectorField else models.JSONField(null=True, blank=True)

    is_active = models.BooleanField(default=True, db_index=True)
    ingested_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'rag_policy_document_chunks'
        ordering = ['document', 'chunk_index']
        indexes = [
            models.Index(fields=['document', 'chunk_index']),
            models.Index(fields=['is_active', 'source_tier']),
            models.Index(fields=['chunk_hash']),
        ]

    def __str__(self):
        return f"{self.document.title} [p.{self.page_number} | {self.section_heading or 'Chunk ' + str(self.chunk_index)}]"


class IngestionReport(models.Model):
    """
    Audit log of an ingestion run or automated pipeline batch.
    """
    STATUS_CHOICES = [
        ('completed', 'Completed Successfully'),
        ('partial_quarantine', 'Completed with Quarantined Documents'),
        ('failed', 'Batch Failed'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    batch_id = models.CharField(max_length=100, unique=True, db_index=True)
    status = models.CharField(max_length=25, choices=STATUS_CHOICES, default='completed')

    total_sources = models.PositiveIntegerField(default=0)
    processed_sources = models.PositiveIntegerField(default=0)
    quarantined_sources = models.PositiveIntegerField(default=0)
    total_chunks_created = models.PositiveIntegerField(default=0)
    duplicates_detected = models.PositiveIntegerField(default=0)

    duration_seconds = models.FloatField(default=0.0)
    error_log = models.JSONField(default=list)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'rag_ingestion_reports'
        ordering = ['-created_at']

    def __str__(self):
        return f"Report {self.batch_id} ({self.status}) - {self.total_chunks_created} chunks"
