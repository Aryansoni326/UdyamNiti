"""
Opportunity Unlock Engine Service Layer.
Coordinates deterministic unlock evaluation, graph reachability, and atomic database persistence.
"""
from typing import List, Dict, Any
from dataclasses import asdict
from django.db import transaction
from .models import OpportunityUnlock
from .engine import OpportunityUnlockEngine, UnlockCandidateData
from apps.strategy.models import Strategy
from apps.policies.models import Scheme


class OpportunityUnlockService:
    """
    Coordinates unlock analysis and persists OpportunityUnlock records for a Strategy.
    """

    @classmethod
    @transaction.atomic
    def generate_unlocks_for_strategy(
        cls,
        strategy: Strategy,
        evaluations_data: List[Dict[str, Any]]
    ) -> List[OpportunityUnlock]:
        """
        Derives high-impact unlock recommendations using OpportunityUnlockEngine.
        """
        strategy.unlocks.all().delete()
        bp = strategy.business_profile

        business_facts = {
            "business_name": bp.business_name,
            "entity_type": bp.entity_type,
            "msme_category": bp.msme_category,
            "industry_sector": bp.industry_sector,
            "state": bp.state,
            "district": bp.district,
            "investment_in_plant_machinery_lakhs": float(bp.investment_in_plant_machinery_lakhs or 0),
            "annual_turnover_lakhs": float(bp.annual_turnover_lakhs or 0),
            "udyam_registration_number": bp.udyam_registration_number,
            "has_udyam": bool(bp.udyam_registration_number),
            "is_women_owned": bp.is_women_owned,
            "is_sc_st_owned": bp.is_sc_st_owned,
            "has_zed_certification": False
        }

        engine = OpportunityUnlockEngine()
        unlock_candidates: List[UnlockCandidateData] = engine.evaluate_unlocks(
            evaluations=evaluations_data,
            business_facts=business_facts
        )

        unlocks_to_create = []
        for cand in unlock_candidates:
            # Map primary scheme if affected opportunities exist
            primary_scheme = None
            if cand.affected_opportunities:
                primary_code = cand.affected_opportunities[0].scheme_code
                primary_scheme = Scheme.objects.filter(scheme_code=primary_code).first()

            unlocks_to_create.append(OpportunityUnlock(
                strategy=strategy,
                scheme=primary_scheme,
                unlock_action=cand.unlock_action,
                current_blocker=cand.current_blocker,
                affected_opportunities=[asdict(o) for o in cand.affected_opportunities],
                evidence_ids=cand.evidence_ids,
                required_user_confirmation=cand.required_user_confirmation,
                explanation=cand.explanation,
                prerequisite_type=cand.prerequisite_type,
                difficulty=cand.difficulty,
                estimated_days=cand.estimated_days,
                potential_benefit_lakhs=cand.potential_benefit_lakhs,
                is_resolvable=cand.is_resolvable,
                status='open'
            ))

        created = OpportunityUnlock.objects.bulk_create(unlocks_to_create)
        return created
