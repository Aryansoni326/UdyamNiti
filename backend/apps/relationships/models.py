"""
Cross-Scheme Relationship Domain Models.
Defines statutory compatibility, prerequisites, sequencing, and cost-head non-duplication rules.
"""
from django.db import models
from django.utils import timezone
import uuid
from apps.policies.models import Scheme


class RelationshipType(models.TextChoices):
    COMPATIBLE = 'COMPATIBLE', 'Compatible — can be applied together'
    INCOMPATIBLE = 'INCOMPATIBLE', 'Incompatible — mutually exclusive'
    PREREQUISITE = 'PREREQUISITE', 'Prerequisite — Scheme A must be obtained before Scheme B'
    SEQUENTIAL = 'SEQUENTIAL', 'Sequential — Apply in specified sequence'
    OVERLAPPING = 'OVERLAPPING', 'Overlapping — Subsidies fund the same expenditure/cost head'
    UNKNOWN = 'UNKNOWN', 'Unknown — Insufficient official statutory evidence'


class RelationshipDirection(models.TextChoices):
    BIDIRECTIONAL = 'BIDIRECTIONAL', 'Bidirectional / Mutual'
    A_TO_B = 'A_TO_B', 'A to B (Scheme A -> Scheme B)'
    B_TO_A = 'B_TO_A', 'B to A (Scheme B -> Scheme A)'


class SchemeRelationship(models.Model):
    """
    Asserted relationship between two government schemes.
    May ONLY be asserted when supported by structured policy data and/or official evidence.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    scheme_a = models.ForeignKey(Scheme, on_delete=models.CASCADE, related_name='relationships_as_a')
    scheme_b = models.ForeignKey(Scheme, on_delete=models.CASCADE, related_name='relationships_as_b')
    
    relationship_type = models.CharField(
        max_length=30,
        choices=RelationshipType.choices,
        default=RelationshipType.UNKNOWN
    )
    direction = models.CharField(
        max_length=20,
        choices=RelationshipDirection.choices,
        default=RelationshipDirection.BIDIRECTIONAL
    )

    # Structured conditions under which this relationship holds (e.g. 'different_invoices', 'term_loan_backed')
    conditions = models.JSONField(
        default=dict,
        blank=True,
        help_text="Structured conditions for compatibility/exclusion"
    )

    # Cost categories affected: e.g. ['plant_and_machinery', 'term_loan_interest', 'civil_works']
    affected_cost_categories = models.JSONField(
        default=list,
        blank=True,
        help_text="Expenditure heads affected (e.g. plant_and_machinery, interest, collateral)"
    )

    # Verified evidence IDs from official Gazette / policy guidelines
    evidence_ids = models.JSONField(
        default=list,
        blank=True,
        help_text="List of verified chunk/document IDs supporting this assertion"
    )

    # Policy versions evaluated (e.g. {'scheme_a_version': 'v2025.1', 'scheme_b_version': 'v2024.2'})
    policy_versions = models.JSONField(
        default=dict,
        blank=True,
        help_text="Policy versions under which relationship is verified"
    )

    last_verified = models.DateTimeField(default=timezone.now)

    description = models.TextField(help_text="Plain-language explanation of relationship and tradeoffs")
    source_evidence = models.TextField(blank=True, help_text="Quotation or summary of official clause")
    confidence = models.FloatField(default=1.0)
    
    is_demo_data = models.BooleanField(
        default=False,
        help_text="Flags synthetic demo relationship data clearly for auditing"
    )

    class Meta:
        db_table = 'scheme_relationships'
        unique_together = ['scheme_a', 'scheme_b']

    def __str__(self):
        prefix = "[DEMO] " if self.is_demo_data else ""
        return f"{prefix}{self.scheme_a.scheme_code} -[{self.relationship_type}]-> {self.scheme_b.scheme_code}"


class RelationshipEvidence(models.Model):
    """
    Statutory Gazette or operational guideline clause justifying the relationship (e.g. non-duplication rule).
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    relationship = models.ForeignKey(
        SchemeRelationship,
        on_delete=models.CASCADE,
        related_name='evidence_records'
    )
    document_title = models.CharField(max_length=255)
    clause_reference = models.CharField(max_length=100)
    clause_text = models.TextField()
    official_url = models.URLField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'relationship_evidence'

    def __str__(self):
        return f"Evidence for {self.relationship}: Clause {self.clause_reference}"
