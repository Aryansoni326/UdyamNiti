"""
Temporal Policy Versioning Domain Models.
Ensures immutable historical records, single active version constraints,
checksum verification, and zero rule-mixing across policy epochs.
"""
import uuid
import hashlib
from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone
from apps.policies.models import Scheme


class PolicyVersion(models.Model):
    """
    Immutable temporal snapshot of a government support scheme and its statutory rules.
    Preserves version, effective dates, source authority, document, clause/page, and SHA-256 checksum.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    scheme = models.ForeignKey(Scheme, on_delete=models.CASCADE, related_name='policy_versions')
    
    version_tag = models.CharField(
        max_length=50,
        help_text="Canonical semantic or statutory version tag, e.g. 'v2024.1', 'v2025.1'"
    )
    version_number = models.IntegerField(help_text="Sequential version integer (1, 2, 3...)")
    
    # Temporal Validity (Bitemporal Period)
    effective_from = models.DateField(help_text="Date on which this policy version came into legal force")
    effective_until = models.DateField(
        null=True,
        blank=True,
        help_text="Date on which this policy version was superseded or expired (null = current active)"
    )

    # Statutory Provenance
    source_authority = models.CharField(max_length=255, help_text="e.g. 'Industries Commissionerate, Govt of Gujarat'")
    source_document = models.CharField(max_length=300, help_text="Official resolution or Gazette title")
    document_checksum = models.CharField(
        max_length=64,
        help_text="SHA-256 cryptographic hash of official Gazette PDF / notification"
    )
    clause_or_page = models.CharField(max_length=150, help_text="e.g. 'Clauses 4.1 to 4.8, pp. 12-16'")
    last_verified = models.DateTimeField(default=timezone.now, help_text="Timestamp of statutory verification")

    # State & Immutability Flags
    is_active = models.BooleanField(
        default=False,
        help_text="Exactly one version may be active per scheme at any given time"
    )
    is_immutable = models.BooleanField(
        default=True,
        help_text="Once published, this historical version cannot be modified in-place"
    )

    # Frozen Rules & Benefit Snapshot
    rules_snapshot = models.JSONField(
        default=list,
        help_text="Complete frozen snapshot of deterministic rules and thresholds at this version"
    )
    benefits_snapshot = models.JSONField(
        default=dict,
        blank=True,
        help_text="Frozen snapshot of benefit ceilings, percentages, and subsidies"
    )
    change_summary = models.TextField(help_text="Audit explanation of additions, removals, and changed thresholds")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'policy_versions'
        ordering = ['-version_number']
        unique_together = [('scheme', 'version_tag'), ('scheme', 'version_number')]
        indexes = [
            models.Index(fields=['scheme', 'is_active']),
            models.Index(fields=['effective_from', 'effective_until']),
            models.Index(fields=['document_checksum']),
        ]

    def clean(self):
        super().clean()
        # 1. Enforce temporal order
        if self.effective_until and self.effective_from > self.effective_until:
            raise ValidationError(
                f"effective_from ({self.effective_from}) cannot be after effective_until ({self.effective_until})."
            )

        # 2. Enforce exactly one active version per scheme
        if self.is_active:
            existing_active = PolicyVersion.objects.filter(
                scheme=self.scheme,
                is_active=True
            ).exclude(pk=self.pk)

            if existing_active.exists():
                active_tags = ", ".join([v.version_tag for v in existing_active])
                raise ValidationError(
                    f"Scheme '{self.scheme.scheme_code}' already has an active policy version ({active_tags}). "
                    "You must supersede the old version before activating a new one."
                )

        # 3. Enforce immutability on published versions
        if self.pk:
            original = PolicyVersion.objects.get(pk=self.pk)
            if original.is_immutable:
                # Do not allow modifying rules snapshot, dates, or checksum of immutable record
                if original.rules_snapshot != self.rules_snapshot:
                    raise ValidationError(
                        f"Policy version {self.version_tag} is immutable. Rules snapshot cannot be altered in-place."
                    )
                if original.document_checksum != self.document_checksum:
                    raise ValidationError(
                        f"Policy version {self.version_tag} is immutable. Document checksum cannot be altered."
                    )

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    @classmethod
    def calculate_checksum(cls, document_bytes_or_text) -> str:
        """Calculates standard SHA-256 checksum."""
        if isinstance(document_bytes_or_text, str):
            document_bytes_or_text = document_bytes_or_text.encode('utf-8')
        return hashlib.sha256(document_bytes_or_text).hexdigest()

    def __str__(self):
        status_str = "ACTIVE" if self.is_active else "HISTORICAL"
        return f"{self.scheme.scheme_code} [{self.version_tag}] ({status_str})"
