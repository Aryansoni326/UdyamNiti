"""
Personalized Policy Impact Service.
Evaluates the downstream impact of approved statutory changes on stored MSME profiles.
Performs candidate filtering, re-evaluates deterministic rules, detects before/after transitions,
and produces grounded explanations without false guarantees.
"""
import logging
import datetime
from typing import Dict, Any, List, Optional, Tuple
from django.db import transaction
from django.utils import timezone
from django.db.models import Q

from apps.business_profiles.models import BusinessProfile
from apps.policies.models import Scheme, SchemeRule
from apps.eligibility.models import EligibilityEvaluation
from apps.eligibility.engine import RuleEngine
from .models import PolicyChange, ImpactEvaluation, ReviewStatus

logger = logging.getLogger(__name__)


class PersonalizedImpactService:
    """
    Evaluates and persists personalized policy impact records for approved policy changes.
    """

    @classmethod
    @transaction.atomic
    def process_policy_change_impact(
        cls,
        policy_change: PolicyChange,
        persist: bool = True
    ) -> List[ImpactEvaluation]:
        """
        Processes an approved PolicyChange against all potentially affected stored business profiles.
        Returns the list of generated ImpactEvaluation records.
        """
        scheme = policy_change.scheme
        candidate_profiles = cls.filter_candidate_profiles(policy_change)

        logger.info(
            f"Evaluating policy change impact for {scheme.scheme_code} across {len(candidate_profiles)} candidate profiles."
        )

        impact_evaluations: List[ImpactEvaluation] = []
        rule_engine = RuleEngine()

        for profile in candidate_profiles:
            # 1. Fetch previous evaluation status if available
            prev_eval = EligibilityEvaluation.objects.filter(
                business_profile=profile,
                scheme=scheme
            ).order_by('-created_at').first()

            previous_status = prev_eval.overall_status if prev_eval else "DOES_NOT_MATCH"
            prev_benefit = float(prev_eval.scheme.max_benefit_amount_lakhs or 0) if prev_eval and prev_eval.scheme else 0.0

            # 2. Re-evaluate deterministic eligibility with current active rules
            eval_result = rule_engine.evaluate(scheme, profile)
            new_status = eval_result.overall_status
            new_benefit = float(scheme.max_benefit_amount_lakhs or 0)

            # 3. Detect Material Transition
            has_transition = False
            impact_type = ""
            status_transition = ""
            delta_benefit = 0.0

            if previous_status != new_status:
                has_transition = True
                status_transition = f"{previous_status} -> {new_status}"
                if previous_status in ("DOES_NOT_MATCH", "UNKNOWN") and new_status in ("MATCH", "POTENTIAL_MATCH"):
                    impact_type = "unlocked_new_match"
                elif previous_status in ("MATCH", "POTENTIAL_MATCH") and new_status == "DOES_NOT_MATCH":
                    impact_type = "disqualified"
                elif previous_status == "POTENTIAL_MATCH" and new_status == "MATCH":
                    impact_type = "transitioned_to_full_match"
                else:
                    impact_type = "status_updated"
            elif policy_change.change_type == "benefit_details" and new_status in ("MATCH", "POTENTIAL_MATCH"):
                old_val = float(policy_change.old_value or 0) if isinstance(policy_change.old_value, (int, float)) else 0.0
                new_val = float(policy_change.new_value or 0) if isinstance(policy_change.new_value, (int, float)) else 0.0
                delta_benefit = new_val - old_val
                if delta_benefit != 0:
                    has_transition = True
                    impact_type = "benefit_increased" if delta_benefit > 0 else "benefit_decreased"
                    status_transition = f"{previous_status} (Cap revised: ₹{old_val}L -> ₹{new_val}L)"

            # If no meaningful transition occurred for this profile, skip
            if not has_transition:
                continue

            # 4. Formulate User-Facing Explanation Grounded in Official Evidence
            explanation = cls._generate_impact_explanation(
                scheme=scheme,
                profile=profile,
                policy_change=policy_change,
                previous_status=previous_status,
                new_status=new_status,
                impact_type=impact_type,
                delta_benefit=delta_benefit
            )

            # 5. Build ImpactEvaluation Record
            impact_rec = ImpactEvaluation(
                policy_change=policy_change,
                business_profile=profile,
                impact_type=impact_type,
                status_transition=status_transition,
                previous_status=previous_status,
                new_status=new_status,
                previous_benefit_lakhs=prev_benefit if prev_benefit > 0 else None,
                new_benefit_lakhs=new_benefit if new_benefit > 0 else None,
                delta_benefit_lakhs=delta_benefit if delta_benefit != 0 else None,
                evidence_ids=[str(policy_change.id)],
                official_citation=policy_change.evidence_source,
                user_facing_explanation=explanation,
                impact_summary=explanation[:250],
                re_evaluated_at=timezone.now()
            )

            if persist:
                impact_rec.save()

            impact_evaluations.append(impact_rec)

        if persist:
            policy_change.processed = True
            policy_change.save(update_fields=['processed'])

        return impact_evaluations

    @classmethod
    def filter_candidate_profiles(cls, policy_change: PolicyChange) -> List[BusinessProfile]:
        """
        Uses indexed profile fact filters to efficiently identify profiles that could be affected.
        """
        scheme = policy_change.scheme
        qs = BusinessProfile.objects.all()

        # 1. State / Jurisdiction Filtering
        if scheme.level in ('state', 'state_gujarat'):
            qs = qs.filter(state__iexact='Gujarat')
        elif scheme.target_states:
            qs = qs.filter(state__in=scheme.target_states)

        # 2. Sector Filtering
        if scheme.target_sectors:
            sector_q = Q()
            for s in scheme.target_sectors:
                sector_q |= Q(industry_sector__icontains=s)
            qs = qs.filter(sector_q)

        # 3. Threshold Window Filtering (if threshold changed)
        if policy_change.change_type == 'thresholds' and isinstance(policy_change.old_value, dict) and isinstance(policy_change.new_value, dict):
            old_exp = policy_change.old_value.get('expected_value')
            new_exp = policy_change.new_value.get('expected_value')
            rule_id = policy_change.affected_rule_ids[0] if policy_change.affected_rule_ids else ""

            if isinstance(old_exp, (int, float)) and isinstance(new_exp, (int, float)) and new_exp > old_exp:
                # If threshold was relaxed (e.g. investment ceiling increased from 500L to 1000L)
                if "investment" in rule_id.lower() or "machinery" in rule_id.lower():
                    # Focus on profiles in the newly opened window or near it
                    qs = qs.filter(investment_in_plant_machinery_lakhs__lte=new_exp)
                elif "turnover" in rule_id.lower():
                    qs = qs.filter(annual_turnover_lakhs__lte=new_exp)

        return list(qs[:100])  # Batch limit for performance

    @classmethod
    def simulate_demo_impact(
        cls,
        scheme_code: str,
        simulated_change: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Demo simulation mode: evaluates a hypothetical policy change (e.g. turnover threshold ₹5 Cr -> ₹10 Cr)
        across stored profiles in memory without persisting permanent records.
        """
        scheme = Scheme.objects.get(scheme_code=scheme_code)

        # Build mock PolicyChange in-memory
        mock_change = PolicyChange(
            scheme=scheme,
            change_type=simulated_change.get('change_type', 'thresholds'),
            materiality='material',
            change_summary=simulated_change.get('change_summary', 'Simulated statutory threshold revision'),
            old_value=simulated_change.get('old_value'),
            new_value=simulated_change.get('new_value'),
            affected_rule_ids=simulated_change.get('affected_rule_ids', ['simulated_rule']),
            evidence_source=simulated_change.get('evidence_source', 'Draft Gazette Resolution 2026')
        )

        impacts = cls.process_policy_change_impact(mock_change, persist=False)

        results = [
            {
                "business_name": imp.business_profile.business_name,
                "msme_category": imp.business_profile.msme_category,
                "turnover_lakhs": float(imp.business_profile.annual_turnover_lakhs or 0),
                "investment_lakhs": float(imp.business_profile.investment_in_plant_machinery_lakhs or 0),
                "previous_status": imp.previous_status,
                "new_status": imp.new_status,
                "status_transition": imp.status_transition,
                "impact_type": imp.impact_type,
                "explanation": imp.user_facing_explanation
            }
            for imp in impacts
        ]

        return {
            "scheme_code": scheme_code,
            "scheme_name": scheme.name,
            "simulated_change": simulated_change,
            "total_profiles_analyzed": len(results),
            "affected_profiles": results
        }

    @classmethod
    def _generate_impact_explanation(
        cls,
        scheme: Scheme,
        profile: BusinessProfile,
        policy_change: PolicyChange,
        previous_status: str,
        new_status: str,
        impact_type: str,
        delta_benefit: float
    ) -> str:
        """
        Creates an explainable narrative grounded in evidence with zero false guarantees.
        """
        citation = policy_change.evidence_source or "Official Gazette Notification"

        if impact_type == "unlocked_new_match":
            return (
                f"Statutory Policy Update: Following the recent amendment under {citation}, "
                f"{policy_change.change_summary.lower()} Based on your recorded business facts "
                f"(Investment: ₹{profile.investment_in_plant_machinery_lakhs}L, Turnover: ₹{profile.annual_turnover_lakhs}L), "
                f"your eligibility for '{scheme.name}' has updated from {previous_status} to {new_status}. "
                "Notice: Final financial assistance remains subject to formal application, official departmental audit, and bank disbursement."
            )
        elif impact_type == "benefit_increased":
            return (
                f"Benefit Ceiling Enhancement: Under {citation}, the maximum financial assistance under "
                f"'{scheme.name}' has been enhanced by +₹{delta_benefit} Lakhs. Your enterprise maintains "
                f"{new_status} status and is eligible to claim the higher ceiling, subject to valid invoice verification."
            )
        elif impact_type == "disqualified":
            return (
                f"Statutory Restriction Notice: Recent policy revision under {citation} has modified eligibility criteria. "
                f"Your enterprise status for '{scheme.name}' has transitioned to DOES NOT MATCH. "
                "Review the updated criteria to explore alternative support programs in this category."
            )
        else:
            return (
                f"Policy Adjustment Notice: Criteria under '{scheme.name}' were updated per {citation}. "
                f"Your status has adjusted to {new_status}. Official verification is recommended before filing."
            )
