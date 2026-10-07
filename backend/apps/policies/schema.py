"""
Canonical Policy Schema Specification for UdyamNiti.
Validates structured policy representations with normalized rule IDs,
evidence pointers, deterministic benefit calculations, and bitemporal dates.
"""
from typing import List, Dict, Any, Optional, Union
from enum import Enum
from datetime import date
from pydantic import BaseModel, Field


# ─── Enumerations ─────────────────────────────────────────────────────────────

class SourceTier(str, Enum):
    TIER_1_GAZETTE = "tier_1_gazette"  # Extraordinary Gazette Notification (Highest legal authority)
    TIER_2_GUIDELINES = "tier_2_operational_guidelines"  # Approved Operational Scheme Guidelines
    TIER_3_CIRCULAR = "tier_3_ministry_circular"  # Office Memorandum / Clarification Circular
    TIER_4_PORTAL_FAQ = "tier_4_portal_faq"  # Official Implementation Portal FAQ / Manual


class RuleOperator(str, Enum):
    EQ = "eq"  # Equals
    NE = "ne"  # Not equals
    GT = "gt"  # Greater than
    GTE = "gte"  # Greater than or equal to
    LT = "lt"  # Less than
    LTE = "lte"  # Less than or equal to
    IN = "in"  # Contained in set
    NOT_IN = "not_in"  # Not contained in set
    BOOL_TRUE = "bool_true"  # Must be strictly True
    BOOL_FALSE = "bool_false"  # Must be strictly False
    CONTAINS = "contains"  # String or array contains
    BETWEEN = "between"  # Numeric range [min, max]


class RuleImportance(str, Enum):
    MANDATORY = "mandatory"  # Disqualifies application if violated
    PREFERRED = "preferred"  # Scored criteria; failure lowers ranking
    BONUS = "bonus"  # Adds financial incentive multiplier if satisfied
    INFO = "info"  # Informational condition with no scoring effect


class RelationshipType(str, Enum):
    STACKS_WITH = "stacks_with"  # Can be claimed together on same expansion
    PREREQUISITE_FOR = "prerequisite_for"  # Must be approved prior to target scheme
    MUTUALLY_EXCLUSIVE = "mutually_exclusive"  # Statutory non-duplication restriction
    SEQUENTIAL = "sequential"  # Recommended execution sequence
    ALTERNATIVE_TO = "alternative_to"  # Substitute scheme option


# ─── Component Models ─────────────────────────────────────────────────────────

class EvidencePointer(BaseModel):
    """Pinpoints verifiable legal evidence for a rule, benefit, or relationship."""
    document_title: str = Field(..., description="Title of the official policy document")
    source_tier: SourceTier = Field(..., description="Legal authority tier of source")
    issuing_authority: str = Field(..., description="Ministry or Directorate publishing the document")
    notification_or_doc_number: str = Field(..., description="Official notification/circular ID")
    clause_or_section: str = Field(..., description="Specific clause, rule, or sub-section number")
    page_number: Optional[int] = Field(None, description="Physical PDF page number where clause appears")
    exact_quote: str = Field(..., description="Verbatim statutory text from official document")
    document_url: str = Field(..., description="Direct link to official gazette or government portal PDF")
    last_verified_date: date = Field(..., description="Date on which this clause was last verified against source")


class DeterministicRule(BaseModel):
    """Deterministic eligibility rule evaluated by the engine."""
    rule_id: str = Field(..., description="Normalized rule identifier e.g. R-GJ-CAP-001")
    rule_name: str = Field(..., description="Human-readable rule name")
    field_path: str = Field(..., description="BusinessProfile or fact attribute path evaluated")
    operator: RuleOperator = Field(..., description="Evaluation operator")
    expected_value: Any = Field(..., description="Target statutory limit or acceptable values")
    importance: RuleImportance = Field(default=RuleImportance.MANDATORY)
    display_label: str = Field(..., description="Label shown on user-facing evaluation checklists")
    failure_message: str = Field(..., description="Plain-English explanation provided when condition fails")
    ambiguity_notes: Optional[str] = Field(None, description="Notes on legal edge cases or discretionary officer interpretations")
    evidence: EvidencePointer = Field(..., description="Official clause backing this condition")
    effective_from: date = Field(..., description="Statutory date when rule came into force")
    effective_until: Optional[date] = Field(None, description="Sunset or expiry date if superseded")
    is_active: bool = Field(default=True)


class FinancialCondition(BaseModel):
    """Discrete financial parameters (turnover, investment, net worth)."""
    condition_id: str = Field(..., description="Unique condition code e.g. FC-01")
    parameter_name: str = Field(..., description="e.g. Investment in Plant & Machinery")
    field_path: str = Field(..., description="Profile field path")
    operator: RuleOperator = Field(...)
    threshold_value: float = Field(..., description="Numerical threshold limit")
    currency_unit: str = Field(default="INR_LAKHS", description="Unit of measurement")
    evidence: EvidencePointer


class RegistrationRequirement(BaseModel):
    """Statutory portal registrations required before or during application."""
    portal_name: str = Field(..., description="e.g. Udyam Registration, GeM, Gujarat Investor Portal")
    registration_type: str = Field(..., description="e.g. Statutory Prerequisite, Secondary Filing")
    mandatory: bool = Field(default=True)
    timing: str = Field(..., description="e.g. Prior to machine purchase, Prior to disbursement")
    verification_method: str = Field(..., description="API verification, Document certificate, Self-declaration")
    portal_url: str = Field(...)


class BenefitCalculationFormula(BaseModel):
    """Deterministic financial benefit calculation metadata."""
    formula_type: str = Field(..., description="percentage_of_capex, interest_rebate, credit_guarantee, lump_sum")
    base_field: str = Field(..., description="Project cost attribute on which subsidy is calculated")
    base_percentage: Optional[float] = Field(None, description="Standard assistance percentage")
    maximum_cap_lakhs: Optional[float] = Field(None, description="Upper ceiling in Lakhs")
    priority_multipliers: Dict[str, float] = Field(
        default_factory=dict,
        description="Additional subsidy percentage boosts (e.g. {'women_owned': 5.0, 'taluka_category_3': 5.0})"
    )
    formula_expression: str = Field(..., description="Mathematical representation e.g. min(capex * (0.20 + bonus), 25.0)")
    evidence: EvidencePointer


class PossibleRelationship(BaseModel):
    """Evidence-backed relationship with another government support scheme."""
    target_scheme_id: str = Field(..., description="Identifier of related scheme e.g. CGTMSE-CENTRAL")
    target_scheme_name: str = Field(...)
    relationship_type: RelationshipType = Field(...)
    description: str = Field(..., description="Plain-English explanation of interaction")
    statutory_non_duplication_clause: Optional[str] = Field(None, description="Legal non-duplication rule reference")
    evidence: EvidencePointer


# ─── Root Canonical Scheme Model ──────────────────────────────────────────────

class CanonicalScheme(BaseModel):
    """
    The canonical structured schema representing an official government support program.
    """
    scheme_id: str = Field(..., description="Unique immutable scheme identifier e.g. GJ-MSME-CAPITAL-2020")
    scheme_name: str = Field(..., description="Full official title of scheme")
    short_name: str = Field(..., description="Abbreviated common title")
    authority: str = Field(..., description="Nodal Ministry or State Department administering program")
    central_or_state: str = Field(..., description="'central' or 'state'")
    applicable_state: Optional[str] = Field(None, description="State name if state-level scheme (e.g. Gujarat)")
    version: int = Field(default=1, description="Sequential policy iteration number")
    status: str = Field(default="active", description="'active', 'suspended', 'expired', 'draft'")

    objective: str = Field(..., description="Stated socio-economic policy objective")
    support_categories: List[str] = Field(..., description="Tags: capital_subsidy, interest_subvention, credit_guarantee, etc.")
    benefit_type: str = Field(..., description="Primary assistance mechanism")
    
    target_enterprise_types: List[str] = Field(..., description="['micro', 'small', 'medium']")
    target_sectors: List[str] = Field(..., description="['Manufacturing', 'Engineering', 'Textiles', 'All']")
    exclusions: List[str] = Field(default_factory=list, description="Explicit statutory negative list / ineligible activities")

    eligibility_rules: List[DeterministicRule] = Field(..., description="List of deterministic conditions")
    financial_conditions: List[FinancialCondition] = Field(default_factory=list)
    registration_requirements: List[RegistrationRequirement] = Field(default_factory=list)
    prerequisites: List[str] = Field(default_factory=list, description="Pre-conditions before filing")
    required_documents: List[str] = Field(..., description="Checklist of required official verification documents")

    benefit_calculation: Optional[BenefitCalculationFormula] = Field(None, description="Deterministic calculation formula")
    possible_relationships: List[PossibleRelationship] = Field(default_factory=list)

    application_process: str = Field(..., description="Step-by-step statutory application workflow")
    official_application_url: str = Field(..., description="Verified direct portal link")
    source_documents: List[EvidencePointer] = Field(..., description="Gazette notifications and guidelines")

    effective_date: date = Field(..., description="Scheme launch or policy notification date")
    effective_until: Optional[date] = Field(None, description="Policy sunset date or validity deadline")
    last_verified_date: date = Field(..., description="Date knowledge engineer audited this record")
    is_synthetic_benchmark: bool = Field(default=False, description="True if synthetic benchmark for demo/testing")


def get_canonical_json_schema() -> Dict[str, Any]:
    """Generates the JSON Schema specification from the Pydantic model."""
    if hasattr(CanonicalScheme, "model_json_schema"):
        return CanonicalScheme.model_json_schema()
    return CanonicalScheme.schema()
