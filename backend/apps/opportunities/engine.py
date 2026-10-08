"""
Opportunity Unlock Engine.
Transforms eligibility gaps and missing prerequisites into actionable opportunity expansion.

Core Guarantees:
1. Distinguishes changeable prerequisites (certifications, registrations, documentation) from hard disqualifiers.
2. Never advises falsifying or manipulating business facts.
3. Never guarantees future eligibility; frames unlocks as statutory enablement pathways.
4. Only proposes unlocks supported by formal rules or official evidence.
5. Uses graph reachability across prerequisite and relationship edges to identify all affected opportunities.
6. Preserves UNKNOWN when causality is uncertain.
"""
import logging
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Any, Optional, Set

from apps.policies.models import Scheme
from apps.relationships.models import SchemeRelationship, RelationshipType
from apps.relationships.services import RelationshipEngine

logger = logging.getLogger(__name__)


# =====================================================================
# 1. Output Contract Dataclasses
# =====================================================================

@dataclass
class AffectedOpportunityData:
    scheme_code: str
    scheme_name: str
    benefit_type: str
    max_benefit_lakhs: Optional[float]
    expected_status_change: str  # e.g. "POTENTIAL_MATCH -> MATCH", "DOES_NOT_MATCH -> POTENTIAL_MATCH"


@dataclass
class UnlockCandidateData:
    unlock_action: str
    current_blocker: str
    affected_opportunities: List[AffectedOpportunityData]
    evidence_ids: List[str]
    required_user_confirmation: str
    explanation: str
    prerequisite_type: str  # registration, certification, documentation, prerequisite_scheme, verification
    difficulty: str         # low, medium, high
    estimated_days: int
    potential_benefit_lakhs: float = 0.0
    is_resolvable: bool = True

    def to_dict(self) -> Dict[str, Any]:
        return {
            "unlock_action": self.unlock_action,
            "current_blocker": self.current_blocker,
            "affected_opportunities": [asdict(o) for o in self.affected_opportunities],
            "evidence_ids": self.evidence_ids,
            "required_user_confirmation": self.required_user_confirmation,
            "explanation": self.explanation,
            "prerequisite_type": self.prerequisite_type,
            "difficulty": self.difficulty,
            "estimated_days": self.estimated_days,
            "potential_benefit_lakhs": self.potential_benefit_lakhs,
            "is_resolvable": self.is_resolvable
        }


# =====================================================================
# 2. Changeable Prerequisites vs Hard Disqualifiers Knowledge Base
# =====================================================================

CHANGEABLE_PREREQUISITES_REGISTRY = {
    "udyam_registration": {
        "action_title": "Complete Free Udyam Registration",
        "prerequisite_type": "registration",
        "fact_triggers": ["udyam", "has_udyam", "udyam_registration_number", "rule_udyam_active"],
        "blocker": "Udyam Registration Number is absent or unverified, which blocks statutory access across government programs.",
        "confirmation": "Upload official Udyam Registration Certificate PDF (matching current PAN and NIC-2008 5-digit code).",
        "explanation": "Udyam Registration is the single statutory prerequisite for MSME classification under the MSMED Act 2020. It is completely free, instant, and self-declared with Aadhaar.",
        "evidence_ids": ["statutory-msmed-act-2020-notif-2119e", "chunk-udyam-portal-faq-1"],
        "difficulty": "low",
        "estimated_days": 2
    },
    "zed_certification": {
        "action_title": "Attain ZED (Zero Defect Zero Effect) Bronze Certification",
        "prerequisite_type": "certification",
        "fact_triggers": ["zed", "has_zed_certification", "zed_bronze", "rule_zed_level"],
        "blocker": "Enterprise does not hold active ZED Bronze/Silver/Gold quality certification.",
        "confirmation": "Submit official ZED Bronze assessment certificate issued by Quality Council of India (QCI).",
        "explanation": "Completing the free online ZED Bronze desktop self-assessment unlocks an additional 1% interest subvention bonus under State policies and fast-tracks bank processing.",
        "evidence_ids": ["chunk-zed-guidelines-para-8", "chunk-gj-gr-interest-sec2"],
        "difficulty": "low",
        "estimated_days": 7
    },
    "bank_sanction_letter": {
        "action_title": "Upload Term Loan Sanction Letter from Lending Bank",
        "prerequisite_type": "documentation",
        "fact_triggers": ["sanction_letter", "term_loan_sanction", "bank_sanction_letter", "rule_loan_sanction"],
        "blocker": "Disbursement of capital subsidy and interest relief requires formal sanction from an approved commercial bank.",
        "confirmation": "Upload credit sanction letter showing term loan account number, sanctioned amount, and purpose.",
        "explanation": "Government capital subsidies reimburse investments funded through formal banking channels. A term loan sanction letter confirms banking channel compliance.",
        "evidence_ids": ["chunk-gj-ind-pol-2025-sec4", "chunk-cgtmse-brochure-cl4"],
        "difficulty": "medium",
        "estimated_days": 14
    },
    "ca_gfci_certificate": {
        "action_title": "Obtain Chartered Accountant Gross Fixed Capital Investment (GFCI) Certificate",
        "prerequisite_type": "documentation",
        "fact_triggers": ["ca_certificate", "gfci_audit", "rule_ca_certified"],
        "blocker": "Machinery invoice expenditures must be independently audited to establish eligible capital subsidy base.",
        "confirmation": "Upload CA certificate with valid Unique Document Identification Number (UDIN) and itemized invoice schedule.",
        "explanation": "Statutory rules require a CA certificate confirming the machinery is new, installed at the registered factory site, and not previously depreciated.",
        "evidence_ids": ["chunk-gj-capital-procedural-manual", "chunk-ca-guidance-udin"],
        "difficulty": "medium",
        "estimated_days": 5
    },
    "taluka_category": {
        "action_title": "Specify Factory Taluka / Industrial Category",
        "prerequisite_type": "verification",
        "fact_triggers": ["location.taluka_category", "taluka", "category_1_2_3"],
        "blocker": "Subsidy ceiling remains UNKNOWN because Gujarat Industrial Policy categorizes talukas into Category 1 (most backward, highest subsidy), Category 2, and Category 3.",
        "confirmation": "Select the factory location taluka from the official District Industries Centre (DIC) classification list.",
        "explanation": "Clarifying whether the factory is situated in Category 1, 2, or 3 determines whether the capital subsidy ceiling is ₹10 Lakhs, ₹25 Lakhs, or ₹35 Lakhs.",
        "evidence_ids": ["chunk-gj-resolution-rule-7", "chunk-gj-taluka-classification-list"],
        "difficulty": "low",
        "estimated_days": 1
    },
    "cgtmse_coverage": {
        "action_title": "Enroll Term Loan under CGTMSE Collateral-Free Guarantee",
        "prerequisite_type": "prerequisite_scheme",
        "fact_triggers": ["cgtmse", "collateral_free", "rule_guarantee_cover"],
        "blocker": "Enterprise lacks collateral security, preventing standalone bank loan approval for machinery procurement.",
        "confirmation": "Bank confirmation that the term loan facility is enrolled under CGTMSE trust cover up to ₹500 Lakhs.",
        "explanation": "CGTMSE guarantees up to 85% of credit facility, enabling the business to procure machinery without pledging immovable property, subsequently qualifying for state capital subsidy.",
        "evidence_ids": ["chunk-cgtmse-brochure-cl4", "statutory-cgtmse-circular-2024"],
        "difficulty": "medium",
        "estimated_days": 10
    }
}

# Hard Disqualifiers: Under NO circumstances should these be suggested as unlocks
HARD_DISQUALIFIERS_TRIGGERS = {
    "turnover_limit_exceeded": "Annual turnover strictly exceeds statutory MSMED Act threshold (₹250 Crores).",
    "investment_limit_exceeded": "Investment in plant and machinery strictly exceeds statutory MSMED Act threshold (₹50 Crores).",
    "greenfield_only_violation": "PMEGP strictly excludes existing enterprises undertaking substantial expansion; greenfield criteria cannot be retroactively met.",
    "state_jurisdiction_exclusion": "Physical factory situated outside Gujarat; cannot qualify for Gujarat state industrial subsidies.",
    "negative_list_sector": "Sector (e.g. tobacco, liquor, speculative trading) is on statutory negative exclusion list."
}


# =====================================================================
# 3. Opportunity Unlock Engine Implementation
# =====================================================================

class OpportunityUnlockEngine:
    """
    Identifies statutory actions and graph traversals that turn eligibility gaps into expanded opportunities.
    """

    def __init__(self):
        self.relationship_engine = RelationshipEngine()

    def discover_unlocks(
        self,
        evaluations: List[Dict[str, Any]],
        business_facts: Dict[str, Any],
        relationships: Optional[Any] = None,
        candidate_schemes: Optional[List[Scheme]] = None
    ) -> List[Dict[str, Any]]:
        """
        Discovers actionable unlock candidates and returns list of serializable dictionaries.
        """
        unlock_candidates = self.evaluate_unlocks(
            evaluations=evaluations,
            business_facts=business_facts,
            candidate_schemes=candidate_schemes
        )
        return [cand.to_dict() for cand in unlock_candidates]

    def evaluate_unlocks(
        self,
        evaluations: List[Dict[str, Any]],
        business_facts: Dict[str, Any],
        candidate_schemes: Optional[List[Scheme]] = None
    ) -> List[UnlockCandidateData]:
        """
        Main entry point for unlock derivation.
        1. Analyzes evaluations for non-matches, potential matches, and unknowns.
        2. Filters out hard disqualifiers.
        3. Identifies changeable prerequisites.
        4. Performs graph reachability traversal to find ALL affected opportunities.
        5. Formulates actionable unlock candidates with zero false promises.
        """
        all_schemes = candidate_schemes or list(Scheme.objects.filter(status='active'))
        scheme_map = {s.scheme_code: s for s in all_schemes}

        detected_prereq_keys: Set[str] = set()

        # Step 1: Detect missing prerequisites across evaluations
        for ev in evaluations:
            status = ev.get('status') or ev.get('overall_status')
            code = ev.get('scheme_code') or (ev.get('scheme').scheme_code if ev.get('scheme') else None)
            scheme_obj = scheme_map.get(code)

            # Check for hard disqualifiers: if triggered, DO NOT attempt to unlock this scheme
            if self._is_hard_disqualified(ev):
                logger.info(f"Scheme {code} rejected for unlock generation due to hard statutory disqualification.")
                continue

            # Check condition failures & unknowns
            conditions = ev.get('condition_results', [])
            for c in conditions:
                c_status = c.get('status', '').upper()
                if c_status in ('FAIL', 'NOT_SATISFIED', 'UNKNOWN'):
                    matched_key = self._match_prerequisite_key(c)
                    if matched_key:
                        detected_prereq_keys.add(matched_key)

            # Check missing_info strings
            missing_info = ev.get('missing_info', [])
            for m in missing_info:
                matched_key = self._match_prerequisite_key({'display_label': m, 'rule_id': m})
                if matched_key:
                    detected_prereq_keys.add(matched_key)

        # Step 2: Check profile facts directly for universal gateway prerequisites
        if not business_facts.get('udyam_registration_number') and not business_facts.get('has_udyam'):
            detected_prereq_keys.add("udyam_registration")
        if not business_facts.get('has_zed_certification'):
            # Only recommend ZED if manufacturing enterprise
            if "manufactur" in str(business_facts.get('industry_sector', '')).lower() or business_facts.get('entity_type'):
                detected_prereq_keys.add("zed_certification")

        # Step 3: Build Unlock Candidates via Graph Reachability
        unlock_candidates: List[UnlockCandidateData] = []

        for p_key in detected_prereq_keys:
            p_config = CHANGEABLE_PREREQUISITES_REGISTRY.get(p_key)
            if not p_config:
                continue

            # Graph reachability: find which schemes become relevant once this prerequisite is met
            affected_opps = self._find_affected_opportunities(p_key, evaluations, all_schemes)
            if not affected_opps:
                continue

            # Compute cumulative potential benefit
            total_potential_benefit = sum(
                float(o.max_benefit_lakhs or 0) for o in affected_opps
            )

            # Formulate grounded explanation
            opp_names = ", ".join([f"'{o.scheme_name}'" for o in affected_opps[:3]])
            explanation = (
                f"Satisfying the prerequisite '{p_config['action_title']}' addresses the active statutory blocker "
                f"({p_config['blocker']}). Based on policy rules and cross-scheme dependencies, completing this action "
                f"may enable formal evaluation for {len(affected_opps)} opportunity(ies), including {opp_names}. "
                f"Note: Final statutory sanction remains subject to departmental verification."
            )

            unlock_candidates.append(UnlockCandidateData(
                unlock_action=p_config['action_title'],
                current_blocker=p_config['blocker'],
                affected_opportunities=affected_opps,
                evidence_ids=p_config['evidence_ids'],
                required_user_confirmation=p_config['confirmation'],
                explanation=explanation,
                prerequisite_type=p_config['prerequisite_type'],
                difficulty=p_config['difficulty'],
                estimated_days=p_config['estimated_days'],
                potential_benefit_lakhs=total_potential_benefit,
                is_resolvable=True
            ))

        # Sort by total potential benefit descending
        unlock_candidates.sort(key=lambda x: x.potential_benefit_lakhs, reverse=True)
        return unlock_candidates

    def _is_hard_disqualified(self, ev: Dict[str, Any]) -> bool:
        """
        Determines whether a scheme failure is a permanent, non-changeable disqualification.
        """
        mandatory_failures = ev.get('mandatory_failures', [])
        for fail in mandatory_failures:
            fail_lower = str(fail).lower()
            for trigger in HARD_DISQUALIFIERS_TRIGGERS:
                if trigger in fail_lower:
                    return True
            if "greenfield" in fail_lower or "turnover exceeds" in fail_lower or "investment exceeds" in fail_lower:
                return True
        return False

    def _match_prerequisite_key(self, condition: Dict[str, Any]) -> Optional[str]:
        """
        Maps a failed or unknown condition to a changeable prerequisite.
        """
        text = f"{condition.get('rule_id', '')} {condition.get('display_label', '')} {condition.get('source_clause', '')}".lower()

        for key, config in CHANGEABLE_PREREQUISITES_REGISTRY.items():
            for trigger in config['fact_triggers']:
                if trigger.lower() in text:
                    return key
        return None

    def _find_affected_opportunities(
        self,
        prerequisite_key: str,
        evaluations: List[Dict[str, Any]],
        all_schemes: List[Scheme]
    ) -> List[AffectedOpportunityData]:
        """
        Performs graph reachability across evaluations and SchemeRelationship edges.
        Finds all schemes where this prerequisite unlocks or enhances eligibility.
        """
        affected = []
        seen_codes: Set[str] = set()

        scheme_eval_map = {
            (ev.get('scheme_code') or (ev.get('scheme').scheme_code if ev.get('scheme') else '')): ev
            for ev in evaluations
        }

        # 1. Direct Evaluation Matches
        for s in all_schemes:
            ev = scheme_eval_map.get(s.scheme_code)
            current_status = ev.get('status') if ev else "UNKNOWN"

            is_directly_affected = False
            expected_change = "UNKNOWN -> MATCH"

            if prerequisite_key == "udyam_registration":
                # Udyam is universal gateway for state capital subsidies & MSME schemes
                if s.level in ('state_gujarat', 'central'):
                    is_directly_affected = True
                    expected_change = "POTENTIAL_MATCH -> MATCH" if current_status == "POTENTIAL_MATCH" else "UNKNOWN -> POTENTIAL_MATCH"

            elif prerequisite_key == "zed_certification":
                # ZED enhances interest subvention schemes and technology grants
                if s.support_type in ('interest_subvention', 'technology_grant', 'quality_certification'):
                    is_directly_affected = True
                    expected_change = "MATCH -> ENHANCED_RATE (+1% Subvention)"

            elif prerequisite_key == "bank_sanction_letter":
                # Capital subsidies & debt subventions require bank term loan sanction
                if s.support_type in ('capital_subsidy', 'interest_subvention'):
                    is_directly_affected = True
                    expected_change = "POTENTIAL_MATCH -> MATCH"

            elif prerequisite_key == "taluka_category":
                # Gujarat capital & interest schemes depend on taluka category
                if s.level == 'state_gujarat':
                    is_directly_affected = True
                    expected_change = "UNKNOWN -> DETERMINISTIC_CALCULATION"

            elif prerequisite_key == "cgtmse_coverage":
                if s.support_type in ('credit_guarantee', 'collateral_free_loan', 'capital_subsidy'):
                    is_directly_affected = True
                    expected_change = "POTENTIAL_MATCH -> MATCH"

            if is_directly_affected and s.scheme_code not in seen_codes:
                seen_codes.add(s.scheme_code)
                affected.append(AffectedOpportunityData(
                    scheme_code=s.scheme_code,
                    scheme_name=s.name,
                    benefit_type=s.support_type,
                    max_benefit_lakhs=float(s.max_benefit_amount_lakhs or 0) if s.max_benefit_amount_lakhs else None,
                    expected_status_change=expected_change
                ))

        # 2. Graph Expansion: Check SchemeRelationship PREREQUISITE edges
        relationships = SchemeRelationship.objects.filter(
            relationship_type=RelationshipType.PREREQUISITE
        ).select_related('scheme_a', 'scheme_b')

        for rel in relationships:
            # If scheme_a is affected, scheme_b may subsequently become reachable
            if rel.scheme_a.scheme_code in seen_codes and rel.scheme_b.scheme_code not in seen_codes:
                seen_codes.add(rel.scheme_b.scheme_code)
                affected.append(AffectedOpportunityData(
                    scheme_code=rel.scheme_b.scheme_code,
                    scheme_name=rel.scheme_b.name,
                    benefit_type=rel.scheme_b.support_type,
                    max_benefit_lakhs=float(rel.scheme_b.max_benefit_amount_lakhs or 0) if rel.scheme_b.max_benefit_amount_lakhs else None,
                    expected_status_change="POST_PREREQUISITE_UNLOCK"
                ))

        return affected
