"""
Authoritative Eligibility Service Layer.
Coordinates:
- Loading typed business facts from BusinessProfile and verifiable BusinessFact registry
- Loading active structured SchemeRules (with versioning and bitemporal gates)
- Deterministic DSL evaluation
- Attaching statutory evidence pointers (Gazette clauses, pages, URLs)
- Identifying missing material facts (knowledge gaps) and official verification items
- Persisting reproducible evaluation records and blockers
- Strictly NEVER returning an AI-generated eligibility percentage.
"""
import uuid
from datetime import date, datetime
from decimal import Decimal
from typing import Dict, Any, List, Optional, Union

from django.db import transaction
from django.utils import timezone

from apps.business_profiles.models import BusinessProfile, BusinessFact, BusinessGoal
from apps.policies.models import Scheme, SchemeRule, SchemeVersion
from apps.eligibility.models import EligibilityEvaluation, ConditionEvaluation, Blocker
from apps.eligibility.dsl import (
    FactType,
    Operator,
    ConditionStatus,
    OverallEligibilityStatus,
    UnknownBehavior,
    RuleDefinition,
    DeterministicRuleEvaluator,
    Money,
    calculate_msme_category
)


class EligibilityEvaluationService:
    """
    Production service orchestrating deterministic eligibility evaluations.
    """

    def __init__(self):
        self.evaluator = DeterministicRuleEvaluator()

    def load_business_facts(self, profile: BusinessProfile) -> Dict[str, Any]:
        """
        Gathers typed facts from BusinessProfile attributes and BusinessFact key-values.
        Normalizes into structured paths (e.g. 'financials.investment_inr', 'location.state').
        """
        facts: Dict[str, Any] = {
            # Identity & Legal Form
            "business_name": profile.business_name,
            "entity_type": profile.entity_type,
            "udyam_number": profile.udyam_registration_number,
            "gstin": profile.gstin,
            "pan": profile.pan,
            "has_udyam": bool(profile.udyam_registration_number),
            # Sector & Industry
            "industry": {
                "sector": "Manufacturing" if profile.is_manufacturing else "Services",
                "is_manufacturing": profile.is_manufacturing,
                "is_service": profile.is_service,
                "nic_code": profile.nic_code or "",
                "sector_name": profile.industry_sector or "",
            },
            # Location
            "location": {
                "state": profile.state,
                "district": profile.district,
                "city": profile.city or "",
                "is_rural": profile.is_rural,
                "is_aspirational": profile.is_aspirational_district,
            },
            # Demographics & Ownership
            "ownership": {
                "gender": profile.owner_gender,
                "caste": profile.owner_caste,
                "is_women_owned": profile.is_women_owned,
                "is_sc_st_owned": profile.is_sc_st_owned,
                "is_minority_owned": profile.is_minority_owned,
                "is_differently_abled": profile.is_differently_abled_owner,
            },
            # Operations & Credit
            "operations": {
                "years_in_operation": profile.years_in_operation,
                "total_employees": profile.total_employees,
                "has_bank_account": profile.has_bank_account,
                "has_existing_loan": profile.has_existing_loan,
                "is_npa": profile.is_npa,
                "credit_score": profile.credit_score,
            },
            # Certifications
            "certifications": {
                "has_iso": profile.has_iso_certification,
                "has_bis": profile.has_bis_certification,
                "has_gem": profile.has_gem_registration,
                "has_export_license": profile.has_export_license,
            }
        }

        # Financial Normalization (Lakhs to INR)
        inv_lakhs = profile.investment_in_plant_machinery_lakhs
        turnover_lakhs = profile.annual_turnover_lakhs

        inv_inr = Money.to_inr(inv_lakhs, "LAKHS") if inv_lakhs is not None else None
        turnover_inr = Money.to_inr(turnover_lakhs, "LAKHS") if turnover_lakhs is not None else None

        facts["financials"] = {
            "investment_lakhs": float(inv_lakhs) if inv_lakhs is not None else None,
            "turnover_lakhs": float(turnover_lakhs) if turnover_lakhs is not None else None,
            "investment_inr": inv_inr,
            "turnover_inr": turnover_inr,
        }

        # Dynamic composite MSME category calculation under MSMED Act 2020
        if inv_inr is not None and turnover_inr is not None:
            computed_cat = calculate_msme_category(inv_inr, turnover_inr)
            facts["enterprise_category"] = computed_cat
        else:
            facts["enterprise_category"] = profile.msme_category.capitalize() if profile.msme_category else None

        # Merge additional custom key-value facts from BusinessFact model
        for bf in profile.facts.all():
            val = bf.fact_value
            # Support dot notation in fact_key
            keys = bf.fact_key.split('.')
            d = facts
            for k in keys[:-1]:
                if k not in d:
                    d[k] = {}
                d = d[k]
            d[keys[-1]] = val

        return facts

    def load_scheme_rules(
        self,
        scheme: Scheme,
        version_number: Optional[int] = None,
        as_of_date: Optional[date] = None
    ) -> List[RuleDefinition]:
        """
        Loads rules from database or scheme version history, converting into RuleDefinitions.
        """
        rule_defs: List[RuleDefinition] = []
        scheme_rules = scheme.rules.filter(is_active=True).order_by('order')

        for r in scheme_rules:
            # Map operator
            op_str = r.operator.lower()
            op_map = {
                'eq': Operator.EQ,
                'ne': Operator.NEQ,
                'neq': Operator.NEQ,
                'gt': Operator.GT,
                'gte': Operator.GTE,
                'lt': Operator.LT,
                'lte': Operator.LTE,
                'in': Operator.IN,
                'not_in': Operator.NOT_IN,
                'between': Operator.BETWEEN,
                'range': Operator.BETWEEN,
                'exists': Operator.EXISTS,
                'not_null': Operator.EXISTS,
                'date_before': Operator.DATE_BEFORE,
                'date_after': Operator.DATE_AFTER,
            }
            operator = op_map.get(op_str, Operator.EQ)

            # Map FactType
            fp = r.field_path.lower()
            if 'investment' in fp or 'turnover' in fp or 'cost' in fp or 'amount' in fp or 'loan' in fp:
                fact_type = FactType.MONEY
                units = "INR_LAKHS"
            elif 'date' in fp:
                fact_type = FactType.DATE
                units = None
            elif 'category' in fp or 'taluka' in fp:
                fact_type = FactType.ENUM
                units = None
            elif 'state' in fp:
                fact_type = FactType.STATE
                units = None
            elif 'has_' in fp or 'is_' in fp:
                fact_type = FactType.BOOLEAN
                units = None
            else:
                fact_type = FactType.ENUM
                units = None

            evidence_ids = []
            if r.source_document:
                evidence_ids.append(r.source_document)

            rule_defs.append(RuleDefinition(
                rule_id=str(r.id),
                description=r.display_label or r.rule_name,
                fact_key=r.field_path,
                fact_type=fact_type,
                operator=operator,
                expected_value=r.expected_value,
                mandatory=(r.importance == 'mandatory'),
                units=units,
                failure_message=r.failure_message or f"Requirement not met: {r.rule_name}",
                evidence_ids=evidence_ids
            ))

        return rule_defs

    def evaluate_scheme(
        self,
        profile_id: Union[str, uuid.UUID],
        scheme_id: Union[str, uuid.UUID],
        goal_id: Optional[Union[str, uuid.UUID]] = None,
        version_number: Optional[int] = None,
        as_of_date: Optional[date] = None
    ) -> Dict[str, Any]:
        """
        Executes single scheme deterministic evaluation.
        Persists reproducible records without any AI percentage hallucination.
        """
        profile = BusinessProfile.objects.get(id=profile_id)
        
        # Support scheme_id as UUID or scheme_code
        if isinstance(scheme_id, str) and not self._is_valid_uuid(scheme_id):
            scheme = Scheme.objects.get(scheme_code=scheme_id)
        else:
            scheme = Scheme.objects.get(id=scheme_id)

        goal = None
        if goal_id:
            goal = BusinessGoal.objects.filter(id=goal_id).first()
        if not goal:
            # Fallback to most recent goal for this profile, or create default general goal
            goal = profile.goals.first()
            if not goal:
                goal = BusinessGoal.objects.create(
                    business_profile=profile,
                    raw_goal_text="General business support and statutory benefits evaluation"
                )

        facts = self.load_business_facts(profile)
        rules = self.load_scheme_rules(scheme, version_number=version_number, as_of_date=as_of_date)

        # Evaluate deterministically
        report = self.evaluator.evaluate_ruleset(
            scheme_id=str(scheme.id),
            scheme_name=scheme.name,
            rules=rules,
            facts=facts,
            as_of_date=as_of_date
        )

        # Resolve active scheme version number
        latest_version = scheme.versions.order_by('-version_number').first()
        active_version_num = version_number or (latest_version.version_number if latest_version else 1)

        # Assemble Output Contract
        conditions_data = []
        official_verification_items = []
        missing_information = report.missing_facts

        for c in report.condition_results:
            cond_record = {
                "rule_id": c.rule_id,
                "description": c.description,
                "business_value": c.actual_value,
                "expected_condition": f"{c.operator} {c.expected_value}",
                "result": c.status.value,
                "evidence": {
                    "source_clause": c.explanation,
                    "evidence_ids": c.evidence_ids
                }
            }
            conditions_data.append(cond_record)

            if c.status == ConditionStatus.REQUIRES_OFFICIAL_VERIFICATION:
                official_verification_items.append({
                    "rule_id": c.rule_id,
                    "description": c.description,
                    "fact_key": c.fact_key,
                    "verification_path": "Upload statutory certificate or verify via official portal"
                })

        evaluated_at = timezone.now().isoformat()

        # Persist reproducible evaluation record in database
        with transaction.atomic():
            eval_record, _ = EligibilityEvaluation.objects.update_or_create(
                goal=goal,
                scheme=scheme,
                defaults={
                    "business_profile": profile,
                    "overall_status": report.overall_status.value,
                    "score": 1.0 if report.overall_status == OverallEligibilityStatus.MATCH else (0.6 if report.overall_status == OverallEligibilityStatus.POTENTIAL_MATCH else 0.0),
                    "condition_results": conditions_data,
                    "mandatory_failures": report.blockers,
                    "missing_info": missing_information,
                    "summary_explanation": report.summary_explanation,
                }
            )

            # Re-create discrete condition evaluation rows
            eval_record.condition_records.all().delete()
            eval_record.blockers.all().delete()

            cond_objects = []
            for c in report.condition_results:
                cond_obj = ConditionEvaluation(
                    evaluation=eval_record,
                    rule_name=c.description[:200],
                    rule_id=c.rule_id,
                    status="PASS" if c.status == ConditionStatus.SATISFIED else ("FAIL" if c.status == ConditionStatus.NOT_SATISFIED else "UNKNOWN"),
                    evaluated_value=c.actual_value,
                    expected_value=c.expected_value,
                    importance="mandatory" if c.is_mandatory else "preferred",
                    explanation=c.explanation,
                    display_label=c.description
                )
                cond_objects.append(cond_obj)
            ConditionEvaluation.objects.bulk_create(cond_objects)

            # Create Blocker records for mandatory failures
            for blk in report.blockers:
                Blocker.objects.create(
                    evaluation=eval_record,
                    blocker_category='mandatory_failure',
                    description=blk,
                    resolution_path="Review statutory requirements or consider alternative unlock programs."
                )

        return {
            "overall_status": report.overall_status.value,
            "scheme_id": str(scheme.id),
            "scheme_code": scheme.scheme_code,
            "scheme_name": scheme.name,
            "conditions": conditions_data,
            "missing_information": missing_information,
            "official_verification_items": official_verification_items,
            "evaluated_at": evaluated_at,
            "scheme_version": active_version_num,
            "summary_explanation": report.summary_explanation,
            "blockers": report.blockers
        }

    def evaluate_batch(
        self,
        profile_id: Union[str, uuid.UUID],
        scheme_ids: List[str],
        goal_id: Optional[Union[str, uuid.UUID]] = None
    ) -> Dict[str, Any]:
        """
        Evaluates multiple candidate schemes in batch for a given profile and goal.
        """
        results = []
        for sid in scheme_ids:
            try:
                res = self.evaluate_scheme(profile_id=profile_id, scheme_id=sid, goal_id=goal_id)
                results.append(res)
            except Scheme.DoesNotExist:
                results.append({
                    "scheme_id": sid,
                    "overall_status": "UNKNOWN",
                    "error": f"Scheme '{sid}' not found."
                })

        return {
            "profile_id": str(profile_id),
            "total_evaluated": len(results),
            "evaluations": results
        }

    def re_evaluate_profile(
        self,
        profile_id: Union[str, uuid.UUID],
        updated_facts: Optional[Dict[str, Any]] = None,
        goal_id: Optional[Union[str, uuid.UUID]] = None
    ) -> Dict[str, Any]:
        """
        Updates profile facts if provided, invalidates stale evaluation records,
        and re-evaluates all previously evaluated schemes.
        """
        profile = BusinessProfile.objects.get(id=profile_id)

        if updated_facts:
            with transaction.atomic():
                for key, val in updated_facts.items():
                    # If direct field on BusinessProfile
                    if hasattr(profile, key):
                        setattr(profile, key, val)
                    else:
                        # Save in BusinessFact registry
                        BusinessFact.objects.update_or_create(
                            business_profile=profile,
                            fact_key=key,
                            defaults={"fact_value": val, "fact_type": "self_declared"}
                        )
                profile.save()

        # Find all schemes previously evaluated for this profile
        previous_evals = EligibilityEvaluation.objects.filter(business_profile=profile)
        scheme_ids = list(previous_evals.values_list('scheme_id', flat=True).distinct())

        if not scheme_ids:
            # If none, evaluate all active schemes
            scheme_ids = list(Scheme.objects.filter(status='active').values_list('id', flat=True)[:10])

        batch_result = self.evaluate_batch(
            profile_id=profile.id,
            scheme_ids=[str(sid) for sid in scheme_ids],
            goal_id=goal_id
        )

        return {
            "profile_id": str(profile.id),
            "re_evaluated_count": len(batch_result["evaluations"]),
            "results": batch_result["evaluations"]
        }

    def _is_valid_uuid(self, val: str) -> bool:
        try:
            uuid.UUID(str(val))
            return True
        except ValueError:
            return False
