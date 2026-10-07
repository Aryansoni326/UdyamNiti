"""
Document Verification & Evidence Provenance Domain Models.
"""
import uuid
from django.db import models
from django.contrib.auth import get_user_model
from apps.business_profiles.models import BusinessProfile

User = get_user_model()


class BusinessDocument(models.Model):
    """
    Official uploaded document used to verify self-declared MSME facts.
    Maintains cryptographic integrity, OCR extracted facts, and verification audit trail.
    """
    DOCUMENT_TYPE_CHOICES = [
        ('udyam_certificate', 'Udyam Registration Certificate'),
        ('gstin_certificate', 'GSTIN Registration Certificate'),
        ('pan_card', 'Enterprise / Promoter PAN Card'),
        ('balance_sheet', 'Audited Balance Sheet & P&L'),
        ('bank_statement', '6-Month Operational Bank Statement'),
        ('caste_certificate', 'SC / ST / OBC Caste Certificate'),
        ('land_rent_deed', 'Factory Land Deed or Registered Rent Agreement'),
        ('ca_certificate', 'Chartered Accountant Investment & Turnover Certificate'),
        ('machinery_quotation_invoice', 'Machinery Quotation / Commercial Invoice'),
        ('zed_certificate', 'ZED Bronze / Silver / Gold Certificate'),
        ('other', 'Other Supporting Official Document'),
    ]

    STATUS_CHOICES = [
        ('unverified', 'Unverified — Pending Review'),
        ('processing', 'Processing OCR & Fact Extraction'),
        ('verified', 'Verified — Authenticated by Document Service'),
        ('rejected', 'Rejected — Discrepancy Found'),
        ('expired', 'Expired — Document Past Validity Date'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    business_profile = models.ForeignKey(
        BusinessProfile,
        on_delete=models.CASCADE,
        related_name='documents',
        help_text='Enterprise associated with this document'
    )
    
    document_type = models.CharField(max_length=40, choices=DOCUMENT_TYPE_CHOICES)
    title = models.CharField(max_length=255, help_text='Display name or file title')
    file = models.FileField(upload_to='documents/%Y/%m/', blank=True, null=True)
    file_hash = models.CharField(
        max_length=64,
        blank=True,
        help_text='SHA-256 checksum ensuring document tamper-proofing'
    )
    
    verification_status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='unverified'
    )
    
    # Structured facts extracted from the document
    extracted_facts = models.JSONField(
        default=dict,
        blank=True,
        help_text='Extracted key facts (e.g. udyam_number, turnover, investment, caste)'
    )
    
    # Optional extraction metadata
    page_count = models.IntegerField(default=1)
    extraction_method = models.CharField(
        max_length=30,
        choices=[
            ('native_pdf', 'Native PDF Text Extraction'),
            ('paddle_ocr', 'PaddleOCR / Image OCR'),
            ('regex_heuristic', 'Regex / Structured Heuristic'),
            ('manual', 'Manual Entry')
        ],
        default='native_pdf'
    )
    raw_extracted_text = models.TextField(blank=True, help_text='Extracted raw text for debugging and audit')
    document_issue_date = models.DateField(null=True, blank=True, help_text='Date of issue / generation printed on document')
    document_period = models.CharField(max_length=50, blank=True, help_text='e.g. FY 2023-24, Q3 2024-25')
    
    rejection_reason = models.TextField(blank=True)
    verified_at = models.DateTimeField(null=True, blank=True)
    verified_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='verified_documents'
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'business_documents'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['business_profile', 'document_type']),
            models.Index(fields=['verification_status']),
        ]

    def __str__(self):
        return f"{self.business_profile.business_name} - {self.get_document_type_display()} ({self.verification_status})"


class DocumentFactProposal(models.Model):
    """
    Extracted candidate fact from an uploaded document waiting for user review.
    Enforces the core product invariant: NEVER overwrite profile facts silently.
    Shows extracted value vs current self-declared value and confidence.
    """
    PROPOSAL_STATUS_CHOICES = [
        ('pending_review', 'Pending User Review'),
        ('accepted', 'Accepted by User — Applied to Profile'),
        ('rejected', 'Rejected by User — Retained Self-Declared Value'),
        ('conflict_reported', 'Conflict Reported — Discrepancy Noted'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    document = models.ForeignKey(BusinessDocument, on_delete=models.CASCADE, related_name='fact_proposals')
    business_profile = models.ForeignKey(BusinessProfile, on_delete=models.CASCADE, related_name='document_fact_proposals')
    
    fact_key = models.CharField(max_length=100, help_text="e.g. udyam_registration_number, annual_turnover_lakhs, investment_in_plant_machinery_lakhs")
    current_value = models.JSONField(null=True, blank=True, help_text="Current profile / self-declared value")
    extracted_value = models.JSONField(help_text="Value parsed from official document")
    source_page = models.IntegerField(default=1, help_text="Page number in source document where fact was detected")
    evidence_snippet = models.TextField(blank=True, help_text="Exact string or clause excerpt from document")
    
    confidence_score = models.FloatField(default=1.0, help_text="0.0 to 1.0 confidence of OCR / extraction")
    has_conflict = models.BooleanField(default=False, help_text="True if extracted value contradicts current profile value")
    conflict_notes = models.TextField(blank=True, help_text="Explanation of conflict or divergence")
    
    status = models.CharField(max_length=30, choices=PROPOSAL_STATUS_CHOICES, default='pending_review')
    reviewed_at = models.DateTimeField(null=True, blank=True)
    reviewed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'document_fact_proposals'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.fact_key}: Current={self.current_value} vs Extracted={self.extracted_value} ({self.status})"


class CrossDocumentConsistencyReport(models.Model):
    """
    Consistency audit report comparing facts across 5 sources:
    Business Profile ↔ Udyam Certificate ↔ GST Data ↔ Financial Statement ↔ Machinery Quotation.
    Detects MATCH, MISSING, CONFLICT, OUTDATED, UNKNOWN.
    Invariants:
    - Never decide which conflicting value is legally correct.
    - Show both values, provenance and dates.
    - Require user review.
    - Allow facts to remain unresolved.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    business_profile = models.ForeignKey(BusinessProfile, on_delete=models.CASCADE, related_name='consistency_reports')
    
    # Detailed matrix of field comparisons
    consistency_matrix = models.JSONField(
        default=dict,
        help_text="Detailed comparison per attribute across Profile, Udyam, GST, Financials, Quotation"
    )
    
    # Metrics
    total_checks = models.IntegerField(default=0)
    matches_count = models.IntegerField(default=0)
    conflicts_count = models.IntegerField(default=0)
    missing_count = models.IntegerField(default=0)
    outdated_count = models.IntegerField(default=0)
    unknown_count = models.IntegerField(default=0)
    
    overall_status = models.CharField(
        max_length=30,
        choices=[
            ('clean_match', 'All Active Facts Consistent'),
            ('conflicts_detected', 'Conflicts Detected — User Review Required'),
            ('missing_evidence', 'Missing Documentary Evidence'),
            ('outdated_documents', 'Outdated Documents Detected'),
        ],
        default='clean_match'
    )
    
    summary_notes = models.TextField(blank=True)
    generated_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'cross_document_consistency_reports'
        ordering = ['-generated_at']

    def __str__(self):
        return f"Consistency Report for {self.business_profile.business_name} ({self.overall_status}) at {self.generated_at.strftime('%Y-%m-%d %H:%M')}"



class DocumentAuditLog(models.Model):
    """
    Immutable audit log for document lifecycle transitions and verification events.
    """
    ACTION_CHOICES = [
        ('uploaded', 'Document Uploaded'),
        ('hash_verified', 'Cryptographic Hash Verified'),
        ('facts_extracted', 'Facts Extracted via OCR/Parser'),
        ('proposals_generated', 'Fact Proposals Generated for User Review'),
        ('proposal_accepted', 'Proposal Accepted by User'),
        ('proposal_rejected', 'Proposal Rejected by User'),
        ('status_changed', 'Verification Status Changed'),
        ('deleted', 'Document Deleted per Retention Policy'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    document = models.ForeignKey(
        BusinessDocument,
        on_delete=models.CASCADE,
        related_name='audit_logs',
        null=True,
        blank=True
    )
    document_title = models.CharField(max_length=255, blank=True)
    action = models.CharField(max_length=30, choices=ACTION_CHOICES)
    details = models.JSONField(default=dict)
    performed_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'document_audit_logs'
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.document_title or (self.document.title if self.document else 'Doc')} - {self.action} at {self.timestamp}"

