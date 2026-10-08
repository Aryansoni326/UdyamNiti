"""
Policy and Scheme domain models.
"""
from django.db import models
import uuid
try:
    from pgvector.django import VectorField
except ImportError:
    VectorField = None


class Scheme(models.Model):
    """
    A government support scheme/program for MSMEs.
    """
    SCHEME_LEVEL_CHOICES = [
        ('central', 'Central Government'),
        ('state', 'State Government'),
        ('state_gujarat', 'Gujarat State'),
    ]
    SUPPORT_TYPE_CHOICES = [
        ('capital_subsidy', 'Capital Subsidy'),
        ('interest_subvention', 'Interest Subvention'),
        ('credit_guarantee', 'Credit Guarantee'),
        ('collateral_free_loan', 'Collateral Free Loan'),
        ('technology_grant', 'Technology Grant'),
        ('export_incentive', 'Export Incentive'),
        ('marketing_support', 'Marketing Support'),
        ('skill_training', 'Skill Training'),
        ('infrastructure', 'Infrastructure Support'),
        ('quality_certification', 'Quality Certification'),
        ('digitalization', 'Digitalization Support'),
        ('equity', 'Equity/VC Support'),
        ('raw_material', 'Raw Material Support'),
        ('multiple', 'Multiple Benefits'),
    ]
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('suspended', 'Suspended'),
        ('expired', 'Expired'),
        ('upcoming', 'Upcoming'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Identity
    scheme_code = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=300)
    short_name = models.CharField(max_length=100, blank=True)
    ministry_department = models.CharField(max_length=200)
    implementing_agency = models.CharField(max_length=200, blank=True)
    
    # Classification
    level = models.CharField(max_length=30, choices=SCHEME_LEVEL_CHOICES)
    division = models.CharField(max_length=150, blank=True, default='', help_text='Departmental division, e.g. MSME, Gujarat State, Agriculture, Social Welfare')
    pdf_filename = models.CharField(max_length=255, blank=True, default='', help_text='Source PDF document filename')
    support_type = models.CharField(max_length=30, choices=SUPPORT_TYPE_CHOICES)
    target_sectors = models.JSONField(default=list, help_text='NIC codes or sector names')
    target_msme_categories = models.JSONField(default=list, help_text='["micro","small","medium"]')
    target_states = models.JSONField(default=list, help_text='Empty means all states')
    
    # Benefit details
    max_benefit_amount_lakhs = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    benefit_percentage = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    benefit_description = models.TextField()
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    launch_date = models.DateField(null=True, blank=True)
    valid_until = models.DateField(null=True, blank=True)
    
    # Official sources
    official_portal_url = models.URLField(blank=True)
    official_document_url = models.URLField(blank=True)
    gazette_notification = models.CharField(max_length=200, blank=True)
    
    # Content
    description = models.TextField()
    eligibility_summary = models.TextField(blank=True)
    application_process = models.TextField(blank=True)
    
    # AI/Search
    embedding = VectorField(dimensions=384, null=True, blank=True) if VectorField else models.JSONField(null=True, blank=True)
    search_text = models.TextField(blank=True, help_text='Combined text for full-text search')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'schemes'
        ordering = ['name']
        indexes = [
            models.Index(fields=['status', 'level']),
            models.Index(fields=['status', 'support_type']),
            models.Index(fields=['scheme_code']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return f"{self.scheme_code}: {self.name}"


class SchemeVersion(models.Model):
    """Track policy changes over time for monitoring."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    scheme = models.ForeignKey(Scheme, on_delete=models.CASCADE, related_name='versions')
    version_number = models.IntegerField()
    change_summary = models.TextField()
    changed_fields = models.JSONField(default=dict)
    effective_date = models.DateField()
    source_document = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'scheme_versions'
        ordering = ['-effective_date']
        unique_together = ['scheme', 'version_number']


class SchemeRule(models.Model):
    """
    A deterministic eligibility condition for a scheme.
    Evaluated by the rule engine against BusinessProfile facts.
    """
    OPERATOR_CHOICES = [
        ('eq', 'Equals'),
        ('ne', 'Not Equals'),
        ('gt', 'Greater Than'),
        ('gte', 'Greater Than or Equal'),
        ('lt', 'Less Than'),
        ('lte', 'Less Than or Equal'),
        ('in', 'In List'),
        ('not_in', 'Not In List'),
        ('contains', 'Contains'),
        ('bool_true', 'Must Be True'),
        ('bool_false', 'Must Be False'),
        ('not_null', 'Must Be Present'),
        ('range', 'Within Range'),
    ]
    IMPORTANCE_CHOICES = [
        ('mandatory', 'Mandatory - disqualifies if fails'),
        ('preferred', 'Preferred - reduces score if fails'),
        ('bonus', 'Bonus - improves score if passes'),
        ('info', 'Informational - no scoring impact'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    scheme = models.ForeignKey(Scheme, on_delete=models.CASCADE, related_name='rules')
    
    rule_name = models.CharField(max_length=200)
    field_path = models.CharField(max_length=100, help_text='BusinessProfile field to evaluate')
    operator = models.CharField(max_length=20, choices=OPERATOR_CHOICES)
    expected_value = models.JSONField(null=True, blank=True)
    importance = models.CharField(max_length=20, choices=IMPORTANCE_CHOICES, default='mandatory')
    
    # Evidence
    source_clause = models.TextField(blank=True, help_text='Exact clause from official document')
    source_document = models.CharField(max_length=255, blank=True)
    source_page = models.CharField(max_length=20, blank=True)
    
    display_label = models.CharField(max_length=200, blank=True)
    failure_message = models.TextField(blank=True)
    
    order = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = 'scheme_rules'
        ordering = ['order', 'importance']
        indexes = [
            models.Index(fields=['scheme', 'is_active', 'order']),
            models.Index(fields=['field_path', 'is_active']),
            models.Index(fields=['importance']),
        ]

    def __str__(self):
        return f"{self.scheme.scheme_code}: {self.rule_name}"


class SchemeBenefit(models.Model):
    """Specific benefit components within a scheme."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    scheme = models.ForeignKey(Scheme, on_delete=models.CASCADE, related_name='benefits')
    
    benefit_name = models.CharField(max_length=200)
    benefit_type = models.CharField(max_length=50)
    amount_or_percentage = models.CharField(max_length=100)
    cap_amount_lakhs = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    conditions = models.TextField(blank=True)
    source_clause = models.TextField(blank=True)

    class Meta:
        db_table = 'scheme_benefits'


class DocumentChunk(models.Model):
    """
    A chunked passage from an official government document for RAG retrieval.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    scheme = models.ForeignKey(Scheme, on_delete=models.CASCADE, related_name='chunks', null=True, blank=True)
    
    # Source metadata
    document_title = models.CharField(max_length=300)
    document_url = models.URLField(blank=True)
    document_type = models.CharField(max_length=50, blank=True)
    ministry = models.CharField(max_length=200, blank=True)
    effective_date = models.DateField(null=True, blank=True)
    page_number = models.IntegerField(null=True, blank=True)
    clause_reference = models.CharField(max_length=100, blank=True)
    
    # Content
    chunk_text = models.TextField()
    chunk_index = models.IntegerField(default=0)
    
    # Vector embedding for semantic search
    embedding = VectorField(dimensions=384, null=True, blank=True) if VectorField else models.JSONField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'document_chunks'
        ordering = ['document_title', 'chunk_index']

    def __str__(self):
        return f"{self.document_title} [chunk {self.chunk_index}]"


class SourceMetadata(models.Model):
    """
    Official Gazette or Ministry Document Metadata repository.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    document_title = models.CharField(max_length=300)
    issuing_ministry = models.CharField(max_length=255)
    document_type = models.CharField(max_length=50) # Gazette, Guideline, Circular, FAQ
    notification_number = models.CharField(max_length=150, blank=True)
    official_url = models.URLField()
    publication_date = models.DateField(null=True, blank=True)
    last_verified_date = models.DateField(auto_now=True)
    sha256_checksum = models.CharField(max_length=64, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'source_metadata'

    def __str__(self):
        return f"{self.document_title} ({self.issuing_ministry})"


class SchemeDocument(models.Model):
    """
    Association between an official source document and a scheme.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    scheme = models.ForeignKey(Scheme, on_delete=models.CASCADE, related_name='scheme_documents')
    source_metadata = models.ForeignKey(SourceMetadata, on_delete=models.CASCADE)
    local_file = models.FileField(upload_to='official_policies/%Y/', blank=True, null=True)
    total_pages = models.PositiveIntegerField(default=1)
    is_current = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'scheme_documents'

    def __str__(self):
        return f"{self.scheme.scheme_code} - {self.source_metadata.document_title}"


# Temporal Policy Versioning
from apps.policies.versioning_models import PolicyVersion
