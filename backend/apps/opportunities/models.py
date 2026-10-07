"""
Opportunity Discovery & Unlock Engine Models.
Stores actionable statutory prerequisites that turn eligibility gaps into expanded opportunities.
"""
import uuid
from django.db import models
from apps.strategy.models import Strategy
from apps.policies.models import Scheme


class PrerequisiteType(models.TextChoices):
    REGISTRATION = 'registration', 'Statutory / Regulatory Registration'
    CERTIFICATION = 'certification', 'Quality / Sustainability Certification'
    DOCUMENTATION = 'documentation', 'Sanction Letter / CA Certificate'
    PREREQUISITE_SCHEME = 'prerequisite_scheme', 'Prerequisite Scheme Milestone'
    VERIFICATION = 'verification', 'Profile Fact Clarification'


class OpportunityUnlock(models.Model):
    """
    Identifies high-impact actionable items that unlock higher subsidy rates or new schemes.
    Grounded in deterministic graph traversal and statutory rules.
    """
    DIFFICULTY_CHOICES = [
        ('low', 'Low Effort (Self-declaration or portal filing)'),
        ('medium', 'Medium Effort (Document or certification upload)'),
        ('high', 'High Effort (Audit, inspection, or banking sanction)'),
    ]

    STATUS_CHOICES = [
        ('open', 'Open'),
        ('in_progress', 'In Progress'),
        ('resolved', 'Resolved'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    strategy = models.ForeignKey(
        Strategy,
        on_delete=models.CASCADE,
        related_name='unlocks'
    )
    scheme = models.ForeignKey(
        Scheme,
        on_delete=models.CASCADE,
        related_name='unlock_recommendations',
        null=True,
        blank=True
    )
    
    # Core prompt output contract fields
    unlock_action = models.CharField(max_length=300, help_text="Actionable title of unlock candidate")
    current_blocker = models.TextField(help_text="The missing condition or barrier causing non-match or uncertainty")
    affected_opportunities = models.JSONField(
        default=list,
        blank=True,
        help_text="List of schemes that become relevant/eligible once this unlock is completed"
    )
    evidence_ids = models.JSONField(
        default=list,
        blank=True,
        help_text="Statutory chunk/document IDs supporting this unlock mechanism"
    )
    required_user_confirmation = models.TextField(
        help_text="What proof or user confirmation is required to verify resolution"
    )
    explanation = models.TextField(
        help_text="Explanation of the causal unlock path without false promises"
    )

    # Classification & Metadata
    prerequisite_type = models.CharField(
        max_length=40,
        choices=PrerequisiteType.choices,
        default=PrerequisiteType.DOCUMENTATION
    )
    is_resolvable = models.BooleanField(default=True)
    potential_benefit_lakhs = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    difficulty = models.CharField(max_length=20, choices=DIFFICULTY_CHOICES, default='medium')
    estimated_days = models.IntegerField(default=7)
    
    # Backwards compatibility fields for existing UI components
    title = models.CharField(max_length=255, blank=True)
    description = models.TextField(blank=True)
    missing_fact_key = models.CharField(max_length=100, blank=True)
    action_required = models.TextField(blank=True)

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='open')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'opportunity_unlocks'
        ordering = ['-potential_benefit_lakhs', 'created_at']

    def save(self, *args, **kwargs):
        # Sync backwards compatibility fields
        if not self.title:
            self.title = self.unlock_action
        if not self.description:
            self.description = self.explanation
        if not self.action_required:
            self.action_required = self.required_user_confirmation
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Unlock: {self.unlock_action} ({len(self.affected_opportunities)} opportunities)"

    def to_dict(self):
        return {
            "id": str(self.id),
            "unlock_action": self.unlock_action,
            "current_blocker": self.current_blocker,
            "affected_opportunities": self.affected_opportunities,
            "evidence_ids": self.evidence_ids,
            "required_user_confirmation": self.required_user_confirmation,
            "explanation": self.explanation,
            "prerequisite_type": self.prerequisite_type,
            "is_resolvable": self.is_resolvable,
            "potential_benefit_lakhs": float(self.potential_benefit_lakhs or 0),
            "difficulty": self.difficulty,
            "estimated_days": self.estimated_days,
            "status": self.status
        }
