"""
Action Plan & Execution Tracking Domain Models.
Defines dependency-aware, grounded statutory next steps for MSMEs.
"""
import uuid
from django.db import models
from apps.business_profiles.models import BusinessProfile
from apps.strategy.models import Strategy
from apps.policies.models import Scheme


class TaskCategory(models.TextChoices):
    VERIFICATION = 'verification', 'Verify Scheme Condition / Fact'
    PREREQUISITE = 'prerequisite', 'Prerequisite — Must Complete First'
    DOCUMENTATION = 'documentation', 'Prepare Documentation / Project Report'
    CERTIFICATION = 'certification', 'Investigate / Attain Certification'
    RELATIONSHIP_REVIEW = 'relationship_review', 'Review Relationship & Stacking Evidence'
    PORTAL_SUBMISSION = 'portal_submission', 'Visit Official Application Portal'
    COMPLIANCE = 'compliance', 'Statutory Compliance'


class CompletionStatus(models.TextChoices):
    PENDING = 'pending', 'Pending'
    IN_PROGRESS = 'in_progress', 'In Progress'
    COMPLETED = 'completed', 'Completed'
    SKIPPED = 'skipped', 'Skipped'


class ActionTask(models.Model):
    """
    A concrete prioritized action item in an MSME's government-support strategy.
    Adheres strictly to zero-fabricated deadlines and dependency-aware ordering.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    strategy = models.ForeignKey(
        Strategy,
        on_delete=models.CASCADE,
        related_name='tasks',
        help_text='Strategy plan this action belongs to'
    )
    business_profile = models.ForeignKey(
        BusinessProfile,
        on_delete=models.CASCADE,
        related_name='action_tasks'
    )
    scheme = models.ForeignKey(
        Scheme,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='action_tasks'
    )

    priority = models.IntegerField(default=1, help_text='Execution order (1 is top priority)')
    title = models.CharField(max_length=300, help_text="Actionable task headline")
    rationale = models.TextField(help_text="Why this task is required for statutory progress")
    description = models.TextField(blank=True, help_text="Detailed procedural step-by-step instructions")
    category = models.CharField(
        max_length=40,
        choices=TaskCategory.choices,
        default=TaskCategory.PORTAL_SUBMISSION
    )

    # Dependency tracking
    dependency_ids = models.JSONField(
        default=list,
        blank=True,
        help_text="List of task UUIDs that must be completed before this task can start"
    )
    related_scheme_ids = models.JSONField(
        default=list,
        blank=True,
        help_text="List of scheme codes related to this action"
    )
    evidence_ids = models.JSONField(
        default=list,
        blank=True,
        help_text="Statutory chunk IDs or Gazette clause references justifying this step"
    )

    # Portal & Compliance
    external_url = models.URLField(
        blank=True,
        null=True,
        help_text="Direct link to official government portal (e.g. udyamregistration.gov.in, ifp.gujarat.gov.in)"
    )
    portal_label = models.CharField(max_length=100, blank=True, help_text="e.g. Gujarat IFP Portal")
    requires_user_action = models.BooleanField(
        default=True,
        help_text="Always True: UdyamNiti does not automatically submit applications without explicit user action"
    )

    # Deadlines (strictly from official data; never fabricated)
    official_deadline = models.CharField(
        max_length=200,
        blank=True,
        help_text="Official statutory deadline if specified in Gazette (e.g. 'Within 1 year from DOCP')"
    )
    estimated_time = models.CharField(max_length=50, default='1-2 days')

    # Status tracking
    status = models.CharField(
        max_length=20,
        choices=CompletionStatus.choices,
        default=CompletionStatus.PENDING
    )
    completed_at = models.DateTimeField(null=True, blank=True)

    # Legacy fields preserved for backward compatibility
    portal_url = models.URLField(blank=True, null=True)
    blocker_for = models.JSONField(default=list, blank=True)
    unlocks_scheme_code = models.CharField(max_length=50, blank=True)
    potential_benefit_lakhs = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'action_tasks'
        ordering = ['priority', 'created_at']
        indexes = [
            models.Index(fields=['strategy', 'status']),
            models.Index(fields=['business_profile', 'priority']),
        ]

    def save(self, *args, **kwargs):
        # Sync external_url and portal_url
        if self.external_url and not self.portal_url:
            self.portal_url = self.external_url
        elif self.portal_url and not self.external_url:
            self.external_url = self.portal_url
        if not self.description:
            self.description = self.rationale
        super().save(*args, **kwargs)

    @property
    def completion_status(self) -> str:
        return self.status

    def to_dict(self):
        return {
            "id": str(self.id),
            "title": self.title,
            "rationale": self.rationale,
            "category": self.category,
            "priority": self.priority,
            "dependency_ids": self.dependency_ids,
            "related_scheme_ids": self.related_scheme_ids,
            "evidence_ids": self.evidence_ids,
            "completion_status": self.status,
            "external_url": self.external_url or self.portal_url,
            "requires_user_action": self.requires_user_action,
            "official_deadline": self.official_deadline or None,
            "estimated_time": self.estimated_time,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None
        }

    def __str__(self):
        return f"[{self.priority}] {self.title} ({self.status})"


class ApplicationPreparationWorkspace(models.Model):
    """
    Dedicated preparation workspace for a selected scheme opportunity.
    Aggregates known/unknown eligibility conditions, required info, required documents,
    preparation checklist, and official government application route.
    Invariants:
    - Never automate government submission, OTP, CAPTCHA, declarations, or departmental approval.
    - Provide a clear 'Continue to official government portal' action.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    business_profile = models.ForeignKey(BusinessProfile, on_delete=models.CASCADE, related_name='application_workspaces')
    scheme = models.ForeignKey(Scheme, on_delete=models.CASCADE, related_name='application_workspaces')
    strategy = models.ForeignKey(Strategy, on_delete=models.SET_NULL, null=True, blank=True, related_name='application_workspaces')

    status = models.CharField(
        max_length=30,
        choices=[
            ('in_preparation', 'In Preparation'),
            ('ready_for_portal', 'Ready to Continue to Portal'),
            ('applied_external', 'Applied on Official Portal'),
            ('archived', 'Archived')
        ],
        default='in_preparation'
    )

    # Official government route & disclaimer
    official_portal_url = models.URLField(max_length=500, help_text="e.g. https://ifp.gujarat.gov.in or https://cgtmse.in")
    official_portal_name = models.CharField(max_length=150, help_text="e.g. Gujarat Investor Facilitation Portal (IFP)")
    application_mode = models.CharField(max_length=50, default="Online Single Window Portal")
    disclaimer_notice = models.TextField(
        default="UdyamNiti prepares your documentation and eligibility facts. In accordance with government regulations, final submission, OTP/Aadhaar verification, and legal declarations must be executed directly by the authorized applicant on the official government portal."
    )

    # Readiness checklist state (JSON tracking prepared items)
    # { "required_documents": [...], "required_information": [...], "known_conditions": [...], "unknown_conditions": [...] }
    workspace_data = models.JSONField(default=dict)

    # Metrics
    documents_ready_count = models.IntegerField(default=0)
    documents_total_count = models.IntegerField(default=0)
    info_ready_count = models.IntegerField(default=0)
    info_total_count = models.IntegerField(default=0)
    tasks_completed_count = models.IntegerField(default=0)
    tasks_total_count = models.IntegerField(default=0)
    unknowns_count = models.IntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'application_workspaces'
        ordering = ['-updated_at']
        unique_together = ['business_profile', 'scheme']

    def __str__(self):
        return f"Workspace for {self.business_profile.business_name} -> {self.scheme.name} ({self.status})"

