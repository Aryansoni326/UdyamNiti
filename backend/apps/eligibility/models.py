"""
Eligibility evaluation models.
"""
from django.db import models
import uuid
from apps.policies.models import Scheme
from apps.business_profiles.models import BusinessProfile, BusinessGoal


class EligibilityEvaluation(models.Model):
    """
    Full eligibility evaluation of a scheme against a business profile, for a specific goal.
    """
    STATUS_CHOICES = [
        ('MATCH', 'Match'),
        ('POTENTIAL_MATCH', 'Potential Match'),
        ('DOES_NOT_MATCH', 'Does Not Match'),
        ('UNKNOWN', 'Unknown'),
        ('REQUIRES_OFFICIAL_VERIFICATION', 'Requires Official Verification'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    goal = models.ForeignKey(BusinessGoal, on_delete=models.CASCADE, related_name='evaluations')
    scheme = models.ForeignKey(Scheme, on_delete=models.CASCADE, related_name='evaluations')
    business_profile = models.ForeignKey(BusinessProfile, on_delete=models.CASCADE, related_name='evaluations')
    
    overall_status = models.CharField(max_length=40, choices=STATUS_CHOICES)
    score = models.FloatField(default=0.0)
    
    condition_results = models.JSONField(default=list)
    mandatory_failures = models.JSONField(default=list)
    missing_info = models.JSONField(default=list)
    summary_explanation = models.TextField(blank=True)
    
    # Relevance to goal
    relevance_score = models.FloatField(default=0.0, help_text='How relevant is this scheme to the stated goal')
    relevance_explanation = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'eligibility_evaluations'
        unique_together = ['goal', 'scheme']
        ordering = ['-score', '-relevance_score']

    def __str__(self):
        return f"{self.scheme.scheme_code} → {self.overall_status} ({self.business_profile.business_name})"


class ConditionEvaluation(models.Model):
    """
    Discrete condition evaluation ensuring point-in-time reproducibility.
    Pins the exact rule, evaluated facts, and source clause quote.
    """
    STATUS_CHOICES = [
        ('PASS', 'Pass'),
        ('FAIL', 'Fail'),
        ('UNKNOWN', 'Unknown'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    evaluation = models.ForeignKey(EligibilityEvaluation, on_delete=models.CASCADE, related_name='condition_records')
    rule_name = models.CharField(max_length=200)
    rule_id = models.CharField(max_length=100, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    
    evaluated_value = models.JSONField(null=True, blank=True)
    expected_value = models.JSONField(null=True, blank=True)
    importance = models.CharField(max_length=20, default='mandatory')
    source_clause = models.TextField(blank=True)
    display_label = models.CharField(max_length=255, blank=True)
    explanation = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'condition_evaluations'
        indexes = [
            models.Index(fields=['evaluation', 'status']),
        ]

    def __str__(self):
        return f"{self.display_label or self.rule_name}: {self.status}"


class Blocker(models.Model):
    """
    Identifies specific blockers preventing an opportunity from transitioning to MATCH.
    """
    BLOCKER_CATEGORY_CHOICES = [
        ('mandatory_failure', 'Mandatory Condition Failed'),
        ('missing_fact', 'Missing Business Profile Fact'),
        ('jurisdiction_exclusion', 'Taluka or State Excluded'),
        ('quota_exhausted', 'Annual Scheme Budget / Quota Exhausted'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    evaluation = models.ForeignKey(EligibilityEvaluation, on_delete=models.CASCADE, related_name='blockers')
    condition_evaluation = models.ForeignKey(ConditionEvaluation, on_delete=models.SET_NULL, null=True, blank=True)
    blocker_category = models.CharField(max_length=40, choices=BLOCKER_CATEGORY_CHOICES)
    description = models.TextField()
    resolution_path = models.TextField(blank=True)
    is_resolvable = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'evaluation_blockers'
