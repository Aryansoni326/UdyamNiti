"""
Core domain models for MSME Business Profiles.
"""
from django.db import models
from django.contrib.auth.models import User
import uuid


class BusinessProfile(models.Model):
    """
    An MSME business entity with all material attributes needed for eligibility evaluation.
    """
    MSME_CATEGORY_CHOICES = [
        ('micro', 'Micro'),
        ('small', 'Small'),
        ('medium', 'Medium'),
    ]
    ENTITY_TYPE_CHOICES = [
        ('proprietorship', 'Proprietorship'),
        ('partnership', 'Partnership'),
        ('llp', 'Limited Liability Partnership'),
        ('pvt_ltd', 'Private Limited Company'),
        ('public_ltd', 'Public Limited Company'),
        ('cooperative', 'Cooperative'),
        ('opc', 'One Person Company'),
    ]
    GENDER_CHOICES = [
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other'),
    ]
    CASTE_CHOICES = [
        ('general', 'General'),
        ('obc', 'OBC'),
        ('sc', 'SC'),
        ('st', 'ST'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='business_profiles', null=True, blank=True)
    
    # Identity
    business_name = models.CharField(max_length=255)
    udyam_registration_number = models.CharField(max_length=50, blank=True, null=True, unique=True)
    gstin = models.CharField(max_length=15, blank=True, null=True)
    pan = models.CharField(max_length=10, blank=True, null=True)
    
    # Classification
    msme_category = models.CharField(max_length=20, choices=MSME_CATEGORY_CHOICES)
    entity_type = models.CharField(max_length=30, choices=ENTITY_TYPE_CHOICES)
    nic_code = models.CharField(max_length=10, blank=True, null=True, help_text='NIC 2008 activity code')
    industry_sector = models.CharField(max_length=100, blank=True)
    industry_subsector = models.CharField(max_length=100, blank=True)
    is_manufacturing = models.BooleanField(default=True)
    is_service = models.BooleanField(default=False)
    
    # Location
    state = models.CharField(max_length=50)
    district = models.CharField(max_length=100)
    city = models.CharField(max_length=100, blank=True)
    pincode = models.CharField(max_length=6, blank=True)
    is_rural = models.BooleanField(default=False)
    is_aspirational_district = models.BooleanField(default=False)
    
    # Financials
    investment_in_plant_machinery_lakhs = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    annual_turnover_lakhs = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    
    # Ownership
    owner_gender = models.CharField(max_length=10, choices=GENDER_CHOICES, blank=True)
    owner_caste = models.CharField(max_length=10, choices=CASTE_CHOICES, blank=True)
    is_sc_st_owned = models.BooleanField(default=False)
    is_women_owned = models.BooleanField(default=False)
    is_minority_owned = models.BooleanField(default=False)
    is_differently_abled_owner = models.BooleanField(default=False)
    
    # Operations
    years_in_operation = models.IntegerField(null=True, blank=True)
    total_employees = models.IntegerField(null=True, blank=True)
    has_bank_account = models.BooleanField(default=True)
    has_existing_loan = models.BooleanField(default=False)
    existing_loan_bank = models.CharField(max_length=100, blank=True)
    is_npa = models.BooleanField(default=False)
    credit_score = models.IntegerField(null=True, blank=True)
    
    # Certifications
    has_iso_certification = models.BooleanField(default=False)
    has_bis_certification = models.BooleanField(default=False)
    has_gem_registration = models.BooleanField(default=False)
    has_export_license = models.BooleanField(default=False)
    
    # Technology
    has_technology_upgrade_plan = models.BooleanField(default=False)
    uses_digital_payments = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'business_profiles'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.business_name} ({self.msme_category})"

    @property
    def investment_crores(self):
        if self.investment_in_plant_machinery_lakhs:
            return float(self.investment_in_plant_machinery_lakhs) / 100
        return None

    @property
    def turnover_crores(self):
        if self.annual_turnover_lakhs:
            return float(self.annual_turnover_lakhs) / 100
        return None

    def to_snapshot_dict(self):
        """Returns a serializable dictionary representation of the business profile for snapshotting."""
        provenances = {
            p.field_name: {
                "source_type": p.source_type,
                "document_reference": p.document_reference,
                "verified": p.verified,
                "verification_date": p.verification_date.isoformat() if p.verification_date else None
            }
            for p in self.field_provenances.all()
        }
        return {
            "id": str(self.id),
            "business_name": self.business_name,
            "udyam_registration_number": self.udyam_registration_number,
            "gstin": self.gstin,
            "pan": self.pan,
            "msme_category": self.msme_category,
            "entity_type": self.entity_type,
            "industry_sector": self.industry_sector,
            "industry_subsector": self.industry_subsector,
            "is_manufacturing": self.is_manufacturing,
            "is_service": self.is_service,
            "state": self.state,
            "district": self.district,
            "city": self.city,
            "pincode": self.pincode,
            "is_rural": self.is_rural,
            "is_aspirational_district": self.is_aspirational_district,
            "investment_in_plant_machinery_lakhs": float(self.investment_in_plant_machinery_lakhs) if self.investment_in_plant_machinery_lakhs is not None else None,
            "annual_turnover_lakhs": float(self.annual_turnover_lakhs) if self.annual_turnover_lakhs is not None else None,
            "total_employees": self.total_employees,
            "years_in_operation": self.years_in_operation,
            "has_bank_account": self.has_bank_account,
            "has_existing_loan": self.has_existing_loan,
            "is_npa": self.is_npa,
            "credit_score": self.credit_score,
            "has_iso_certification": self.has_iso_certification,
            "has_bis_certification": self.has_bis_certification,
            "has_gem_registration": self.has_gem_registration,
            "has_export_license": self.has_export_license,
            "is_women_owned": self.is_women_owned,
            "is_sc_st_owned": self.is_sc_st_owned,
            "owner_gender": self.owner_gender,
            "owner_caste": self.owner_caste,
            "field_provenances": provenances,
        }

    def create_snapshot(self, trigger_reason: str = "manual_update"):
        """Creates an immutable frozen snapshot for reproducible evaluations."""
        latest_snapshot = self.snapshots.order_by('-snapshot_version').first()
        next_version = (latest_snapshot.snapshot_version + 1) if latest_snapshot else 1
        snapshot_data = self.to_snapshot_dict()
        return ProfileSnapshot.objects.create(
            business_profile=self,
            snapshot_version=next_version,
            snapshot_data=snapshot_data,
            trigger_reason=trigger_reason
        )



class BusinessGoal(models.Model):
    """
    A specific business goal entered by the MSME user in natural language.
    """
    GOAL_STATUS_CHOICES = [
        ('pending', 'Pending Analysis'),
        ('analyzing', 'Analyzing'),
        ('ready', 'Strategy Ready'),
        ('error', 'Analysis Error'),
    ]
    SUPPORT_CATEGORY_CHOICES = [
        ('capital_subsidy', 'Capital Subsidy'),
        ('credit_guarantee', 'Credit Guarantee'),
        ('technology', 'Technology Upgrade'),
        ('marketing', 'Market Development'),
        ('export', 'Export Support'),
        ('skill', 'Skill Development'),
        ('infrastructure', 'Infrastructure'),
        ('quality', 'Quality Certification'),
        ('digital', 'Digitalization'),
        ('general', 'General Support'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    business_profile = models.ForeignKey(BusinessProfile, on_delete=models.CASCADE, related_name='goals')
    
    # Raw input
    raw_goal_text = models.TextField()
    
    # Parsed structured intent (from Goal Agent)
    parsed_objective = models.TextField(blank=True)
    parsed_project_type = models.CharField(max_length=100, blank=True)
    parsed_investment_amount_lakhs = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    parsed_support_categories = models.JSONField(default=list)
    parsed_industry_hints = models.JSONField(default=list)
    parsed_missing_info = models.JSONField(default=list, help_text='High-impact missing profile facts')
    
    status = models.CharField(max_length=20, choices=GOAL_STATUS_CHOICES, default='pending')
    error_message = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'business_goals'
        ordering = ['-created_at']

    def __str__(self):
        return f"Goal: {self.raw_goal_text[:60]}... ({self.business_profile.business_name})"


class BusinessFact(models.Model):
    """
    A discrete verifiable fact about a business, with evidence and confidence.
    """
    FACT_TYPE_CHOICES = [
        ('self_declared', 'Self Declared'),
        ('document_verified', 'Document Verified'),
        ('official_registry', 'Official Registry'),
        ('system_derived', 'System Derived'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    business_profile = models.ForeignKey(BusinessProfile, on_delete=models.CASCADE, related_name='facts')
    
    fact_key = models.CharField(max_length=100, help_text='e.g., msme_category, annual_turnover')
    fact_value = models.JSONField()
    fact_type = models.CharField(max_length=30, choices=FACT_TYPE_CHOICES, default='self_declared')
    confidence = models.FloatField(default=1.0, help_text='0.0 to 1.0')
    source_description = models.CharField(max_length=255, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'business_facts'
        unique_together = ['business_profile', 'fact_key']

    def __str__(self):
        return f"{self.business_profile.business_name}: {self.fact_key} = {self.fact_value}"


class FactEvidence(models.Model):
    """
    Provenance evidence linking a BusinessFact to a document upload or registry.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    business_fact = models.ForeignKey(BusinessFact, on_delete=models.CASCADE, related_name='evidence_links')
    source_type = models.CharField(
        max_length=40,
        choices=[
            ('self_declared', 'Self Declared'),
            ('document_supported', 'Document Supported'),
            ('official_registry', 'Official Registry Verified'),
            ('ca_certified', 'Chartered Accountant Certified')
        ],
        default='self_declared'
    )
    document_reference = models.CharField(max_length=255, blank=True)
    verification_notes = models.TextField(blank=True)
    verified = models.BooleanField(default=False)
    confidence_score = models.FloatField(default=1.0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'fact_evidence'

    def __str__(self):
        return f"Evidence for {self.business_fact.fact_key} ({self.source_type})"


class ConsistencyCheck(models.Model):
    """
    Detects discrepancies between self-declared profile facts and verified documents.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    business_profile = models.ForeignKey(BusinessProfile, on_delete=models.CASCADE, related_name='consistency_checks')
    fact_key = models.CharField(max_length=100)
    self_declared_value = models.JSONField()
    verified_document_value = models.JSONField()
    has_discrepancy = models.BooleanField(default=False)
    discrepancy_explanation = models.TextField(blank=True)
    checked_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'consistency_checks'

    def __str__(self):
        return f"Consistency check for {self.business_profile.business_name}: {self.fact_key} (Discrepancy: {self.has_discrepancy})"


class ProfileSnapshot(models.Model):
    """
    Immutable frozen snapshot of an MSME Business Profile at an instant in time.
    Ensures fully reproducible eligibility evaluations, audits, and statutory reviews.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    business_profile = models.ForeignKey(BusinessProfile, on_delete=models.CASCADE, related_name='snapshots')
    snapshot_version = models.IntegerField(default=1)
    snapshot_data = models.JSONField(help_text="Complete frozen dictionary of business profile fields and provenances")
    trigger_reason = models.CharField(
        max_length=100,
        default='manual_update',
        help_text="Reason snapshot was created: evaluation_run, material_field_change, pre_update, manual_snapshot"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'profile_snapshots'
        ordering = ['-snapshot_version', '-created_at']
        unique_together = ['business_profile', 'snapshot_version']

    def __str__(self):
        return f"Snapshot v{self.snapshot_version} for {self.business_profile.business_name} ({self.created_at.strftime('%Y-%m-%d %H:%M')})"


class ProfileFieldProvenance(models.Model):
    """
    Field-level provenance tracker recording whether an attribute is self-declared,
    document-supported, official registry verified, or CA certified.
    """
    PROVENANCE_SOURCE_CHOICES = [
        ('self_declared', 'Self Declared'),
        ('document_supported', 'Document Supported'),
        ('official_registry', 'Official Registry Verified'),
        ('ca_certified', 'Chartered Accountant Certified'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    business_profile = models.ForeignKey(BusinessProfile, on_delete=models.CASCADE, related_name='field_provenances')
    field_name = models.CharField(max_length=100, help_text="e.g. annual_turnover_lakhs, udyam_registration_number, state")
    source_type = models.CharField(max_length=40, choices=PROVENANCE_SOURCE_CHOICES, default='self_declared')
    document_reference = models.CharField(max_length=255, blank=True, null=True, help_text="e.g. UDYAM-REG-01-0012, GST-GSTR3B-2025-Q3")
    verified = models.BooleanField(default=False)
    verified_by = models.CharField(max_length=100, blank=True, null=True)
    verification_date = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'profile_field_provenances'
        unique_together = ['business_profile', 'field_name']

    def __str__(self):
        return f"{self.business_profile.business_name} - {self.field_name}: {self.source_type} (Verified={self.verified})"


class ProfileChangeHistory(models.Model):
    """
    Audit log of field updates on an MSME Business Profile.
    Captures old value, new value, materiality, and user/source attribution.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    business_profile = models.ForeignKey(BusinessProfile, on_delete=models.CASCADE, related_name='change_history')
    field_name = models.CharField(max_length=100)
    old_value = models.JSONField(null=True, blank=True)
    new_value = models.JSONField(null=True, blank=True)
    is_material = models.BooleanField(
        default=False,
        help_text="True if this change materially affects scheme eligibility criteria (e.g. turnover, investment, state, category)"
    )
    changed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    change_reason = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'profile_change_history'
        ordering = ['-created_at']

    def __str__(self):
        return f"Change on {self.business_profile.business_name} - {self.field_name} at {self.created_at.strftime('%Y-%m-%d %H:%M')}"

