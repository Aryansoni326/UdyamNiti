"""
Policy Monitoring & Change Detection Domain Models.
Tracks granular changes across eligibility rules, thresholds, dates, benefits,
prerequisites, documents, and application routes with manual curation workflows.
"""
from django.db import models
from django.utils import timezone
import uuid
from apps.business_profiles.models import BusinessProfile
from apps.policies.models import Scheme


class ChangeType(models.TextChoices):
    ELIGIBILITY_RULES = 'eligibility_rules', 'Eligibility Rules Change'
    THRESHOLDS = 'thresholds', 'Financial / Numeric Threshold Change'
    DATES = 'dates', 'Effective Date / Deadline Change'
    BENEFIT_DETAILS = 'benefit_details', 'Benefit Amount / Percentage Change'
    PREREQUISITES = 'prerequisites', 'Prerequisite / Gateway Condition Change'
    REQUIRED_DOCUMENTS = 'required_documents', 'Documentation Requirement Change'
    APPLICATION_ROUTE = 'application_route', 'Portal / Submission Route Change'
    GENERAL = 'general', 'General Policy Amendment'


class MaterialityClassification(models.TextChoices):
    MATERIAL = 'material', 'Material - Directly Impacts Eligibility / Benefit Quantum'
    INFORMATIONAL = 'informational', 'Informational - Non-Scoring Procedural Clarification'


class ReviewStatus(models.TextChoices):
    PENDING_REVIEW = 'pending_review', 'Pending Curated Human Review'
    APPROVED_ACTIVE = 'approved_active', 'Approved & Active in Rule Engine'
    REJECTED = 'rejected', 'Rejected by Curator'


class PolicyChange(models.Model):
    """
    Structured record of a detected policy change between policy versions.
    Requires manual/curated approval before material changes become active in the decision engine.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    scheme = models.ForeignKey(Scheme, on_delete=models.CASCADE, related_name='policy_changes')
    
    change_type = models.CharField(max_length=40, choices=ChangeType.choices)
    materiality = models.CharField(
        max_length=20,
        choices=MaterialityClassification.choices,
        default=MaterialityClassification.MATERIAL
    )
    
    change_summary = models.TextField(help_text="Human-readable explanation of change")
    old_value = models.JSONField(null=True, blank=True, help_text="Prior policy / rule state")
    new_value = models.JSONField(null=True, blank=True, help_text="New policy / rule state")
    affected_rule_ids = models.JSONField(default=list, blank=True, help_text="Rule IDs impacted by this change")
    
    effective_date = models.DateField(null=True, blank=True, help_text="Statutory effective date of the amendment")
    evidence_source = models.TextField(help_text="Official Gazette citation, clause, page, or document reference")
    confidence_of_extraction = models.FloatField(default=1.0, help_text="Extraction confidence score (0.0 to 1.0)")
    requires_human_review = models.BooleanField(
        default=False,
        help_text="If True, change must be approved before triggering downstream profile re-evaluations"
    )
    review_status = models.CharField(
        max_length=30,
        choices=ReviewStatus.choices,
        default=ReviewStatus.APPROVED_ACTIVE
    )
    
    reviewed_by = models.CharField(max_length=150, blank=True, help_text="Username or email of reviewing curator")
    reviewed_at = models.DateTimeField(null=True, blank=True)
    
    detected_at = models.DateTimeField(auto_now_add=True)
    processed = models.BooleanField(default=False, help_text="Whether downstream impact mapping has completed")

    # Backward compatibility field
    source_notification = models.CharField(max_length=255, blank=True)

    class Meta:
        db_table = 'policy_changes'
        ordering = ['-detected_at']
        indexes = [
            models.Index(fields=['scheme', 'review_status']),
            models.Index(fields=['change_type', 'materiality']),
            models.Index(fields=['detected_at']),
        ]

    def save(self, *args, **kwargs):
        if not self.source_notification and self.evidence_source:
            self.source_notification = self.evidence_source[:200]
        # Automatically require human review if material and confidence < 0.98 or explicitly flagged
        if self.requires_human_review and self.review_status == ReviewStatus.APPROVED_ACTIVE and not self.reviewed_at:
            self.review_status = ReviewStatus.PENDING_REVIEW
        super().save(*args, **kwargs)

    def approve(self, curator_name: str = "curator"):
        """Approves the detected change, transitioning it to active."""
        self.review_status = ReviewStatus.APPROVED_ACTIVE
        self.reviewed_by = curator_name
        self.reviewed_at = timezone.now()
        self.save(update_fields=['review_status', 'reviewed_by', 'reviewed_at'])

    def reject(self, curator_name: str = "curator"):
        """Rejects the detected change."""
        self.review_status = ReviewStatus.REJECTED
        self.reviewed_by = curator_name
        self.reviewed_at = timezone.now()
        self.save(update_fields=['review_status', 'reviewed_by', 'reviewed_at'])

    def __str__(self):
        return f"[{self.materiality.upper()}] {self.scheme.scheme_code} - {self.change_type} ({self.review_status})"


class ImpactEvaluation(models.Model):
    """Tracks which business profiles are impacted by an approved policy change."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    policy_change = models.ForeignKey(PolicyChange, on_delete=models.CASCADE, related_name='impacts')
    business_profile = models.ForeignKey(BusinessProfile, on_delete=models.CASCADE, related_name='policy_impacts')
    
    # Transition classification
    impact_type = models.CharField(max_length=50)  # e.g. 'unlocked_new_match', 'benefit_increased', 'disqualified', 'prerequisite_added'
    status_transition = models.CharField(max_length=80, blank=True, help_text="e.g. 'DOES_NOT_MATCH -> POTENTIAL_MATCH'")
    previous_status = models.CharField(max_length=40, blank=True)
    new_status = models.CharField(max_length=40, blank=True)
    
    # Financial impact deltas
    previous_benefit_lakhs = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    new_benefit_lakhs = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    delta_benefit_lakhs = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    
    # Traceability & Grounding
    evidence_ids = models.JSONField(default=list, blank=True, help_text="Official statutory chunk IDs")
    official_citation = models.TextField(blank=True, help_text="Statutory clause reference or quotation")
    user_facing_explanation = models.TextField(help_text="Plain-language explanation grounded in evidence with zero false guarantees")
    impact_summary = models.TextField(blank=True)

    notification_sent = models.BooleanField(default=False)
    re_evaluated_at = models.DateTimeField(default=timezone.now)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'impact_evaluations'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['business_profile', 'impact_type']),
            models.Index(fields=['policy_change', 're_evaluated_at']),
        ]

    def save(self, *args, **kwargs):
        if not self.impact_summary:
            self.impact_summary = self.user_facing_explanation[:200]
        super().save(*args, **kwargs)

    def to_dict(self):
        return {
            "id": str(self.id),
            "policy_change_id": str(self.policy_change.id),
            "scheme_code": self.policy_change.scheme.scheme_code,
            "scheme_name": self.policy_change.scheme.name,
            "business_profile_id": str(self.business_profile.id),
            "business_name": self.business_profile.business_name,
            "impact_type": self.impact_type,
            "status_transition": self.status_transition,
            "previous_status": self.previous_status,
            "new_status": self.new_status,
            "previous_benefit_lakhs": float(self.previous_benefit_lakhs) if self.previous_benefit_lakhs is not None else None,
            "new_benefit_lakhs": float(self.new_benefit_lakhs) if self.new_benefit_lakhs is not None else None,
            "delta_benefit_lakhs": float(self.delta_benefit_lakhs) if self.delta_benefit_lakhs is not None else None,
            "evidence_ids": self.evidence_ids,
            "official_citation": self.official_citation,
            "user_facing_explanation": self.user_facing_explanation,
            "re_evaluated_at": self.re_evaluated_at.isoformat() if self.re_evaluated_at else None
        }

    def __str__(self):
        return f"Impact on {self.business_profile.business_name}: {self.status_transition or self.impact_type}"
