"""
Deterministic Eligibility Rule Engine.

Evaluates structured SchemeRules against BusinessProfile facts.
This is the authoritative eligibility decision layer — NOT the LLM.
"""
from dataclasses import dataclass, field
from typing import Any, Optional
from apps.policies.models import SchemeRule, Scheme
from apps.business_profiles.models import BusinessProfile


ELIGIBILITY_STATUS = {
    'MATCH': 'MATCH',
    'POTENTIAL_MATCH': 'POTENTIAL_MATCH',
    'DOES_NOT_MATCH': 'DOES_NOT_MATCH',
    'UNKNOWN': 'UNKNOWN',
    'REQUIRES_OFFICIAL_VERIFICATION': 'REQUIRES_OFFICIAL_VERIFICATION',
}


@dataclass
class ConditionResult:
    rule_id: str
    rule_name: str
    field_path: str
    status: str  # PASS, FAIL, UNKNOWN
    actual_value: Any
    expected_value: Any
    operator: str
    importance: str
    source_clause: str
    explanation: str
    display_label: str


@dataclass
class EligibilityResult:
    scheme_id: str
    scheme_name: str
    scheme_code: str
    overall_status: str  # MATCH, POTENTIAL_MATCH, DOES_NOT_MATCH, UNKNOWN
    score: float  # 0.0 to 1.0
    conditions: list[ConditionResult] = field(default_factory=list)
    mandatory_failures: list[str] = field(default_factory=list)
    missing_info: list[str] = field(default_factory=list)
    summary_explanation: str = ''
    max_benefit_lakhs: Optional[float] = None
    support_type: str = ''


def _get_field_value(profile: BusinessProfile, field_path: str) -> tuple[Any, bool]:
    """
    Get a field value from BusinessProfile.
    Returns (value, is_known) — is_known=False means data is missing/unknown.
    """
    # Handle nested paths like 'investment_in_plant_machinery_lakhs'
    try:
        value = getattr(profile, field_path, None)
        if value is None:
            return None, False
        return value, True
    except AttributeError:
        return None, False


def _evaluate_condition(actual: Any, operator: str, expected: Any) -> Optional[bool]:
    """
    Evaluate a single condition. Returns None if evaluation is impossible.
    """
    if actual is None:
        return None
    
    try:
        if operator == 'eq':
            return str(actual).lower() == str(expected).lower()
        elif operator == 'ne':
            return str(actual).lower() != str(expected).lower()
        elif operator == 'gt':
            return float(actual) > float(expected)
        elif operator == 'gte':
            return float(actual) >= float(expected)
        elif operator == 'lt':
            return float(actual) < float(expected)
        elif operator == 'lte':
            return float(actual) <= float(expected)
        elif operator == 'in':
            if isinstance(expected, list):
                return str(actual).lower() in [str(e).lower() for e in expected]
            return False
        elif operator == 'not_in':
            if isinstance(expected, list):
                return str(actual).lower() not in [str(e).lower() for e in expected]
            return True
        elif operator == 'contains':
            return str(expected).lower() in str(actual).lower()
        elif operator == 'bool_true':
            return bool(actual) is True
        elif operator == 'bool_false':
            return bool(actual) is False
        elif operator == 'not_null':
            return actual is not None
        elif operator in ('range', 'between'):
            if isinstance(expected, list) and len(expected) == 2:
                return float(expected[0]) <= float(actual) <= float(expected[1])
        return None
    except (TypeError, ValueError):
        return None


def evaluate_condition(actual: Any, operator: str, expected: Any) -> Optional[bool]:
    """
    Public API for deterministic condition evaluation.
    Evaluates operator comparisons against expected values without floating point drift.
    """
    return _evaluate_condition(actual, operator, expected)



class RuleEngine:
    """
    Evaluates all active rules for a scheme against a business profile.
    Produces a deterministic EligibilityResult.
    """

    def evaluate(self, scheme: Scheme, profile: BusinessProfile) -> EligibilityResult:
        # Avoid N+1 query: Use prefetched rules if available in memory
        if hasattr(scheme, '_prefetched_objects_cache') and 'rules' in scheme._prefetched_objects_cache:
            rules = [r for r in scheme.rules.all() if r.is_active]
            rules.sort(key=lambda r: (r.order, 0 if r.importance == 'mandatory' else 1))
        else:
            rules = scheme.rules.filter(is_active=True).order_by('order', 'importance')
        
        conditions = []
        mandatory_failures = []
        missing_info = []
        mandatory_total = 0
        mandatory_pass = 0
        preferred_total = 0
        preferred_pass = 0

        for rule in rules:
            actual_value, is_known = _get_field_value(profile, rule.field_path)
            
            if not is_known:
                # Data unknown → can't evaluate
                condition_status = 'UNKNOWN'
                explanation = f"Missing data: {rule.display_label or rule.field_path}"
                result = ConditionResult(
                    rule_id=str(rule.id),
                    rule_name=rule.rule_name,
                    field_path=rule.field_path,
                    status='UNKNOWN',
                    actual_value=None,
                    expected_value=rule.expected_value,
                    operator=rule.operator,
                    importance=rule.importance,
                    source_clause=rule.source_clause,
                    explanation=explanation,
                    display_label=rule.display_label or rule.rule_name,
                )
                conditions.append(result)
                if rule.importance == 'mandatory':
                    missing_info.append(rule.display_label or rule.rule_name)
                continue

            passes = _evaluate_condition(actual_value, rule.operator, rule.expected_value)
            
            if passes is None:
                condition_status = 'UNKNOWN'
                explanation = f"Could not evaluate: {rule.rule_name}"
            elif passes:
                condition_status = 'PASS'
                explanation = self._pass_explanation(rule, actual_value)
            else:
                condition_status = 'FAIL'
                explanation = rule.failure_message or f"Requirement not met: {rule.rule_name}"

            result = ConditionResult(
                rule_id=str(rule.id),
                rule_name=rule.rule_name,
                field_path=rule.field_path,
                status=condition_status,
                actual_value=actual_value,
                expected_value=rule.expected_value,
                operator=rule.operator,
                importance=rule.importance,
                source_clause=rule.source_clause,
                explanation=explanation,
                display_label=rule.display_label or rule.rule_name,
            )
            conditions.append(result)

            if rule.importance == 'mandatory':
                mandatory_total += 1
                if condition_status == 'PASS':
                    mandatory_pass += 1
                elif condition_status == 'FAIL':
                    mandatory_failures.append(rule.display_label or rule.rule_name)
            elif rule.importance == 'preferred':
                preferred_total += 1
                if condition_status == 'PASS':
                    preferred_pass += 1

        # Determine overall status
        overall_status, score = self._compute_status(
            mandatory_total, mandatory_pass, mandatory_failures,
            preferred_total, preferred_pass, missing_info
        )

        summary = self._build_summary(overall_status, mandatory_failures, missing_info, scheme.name)

        return EligibilityResult(
            scheme_id=str(scheme.id),
            scheme_name=scheme.name,
            scheme_code=scheme.scheme_code,
            overall_status=overall_status,
            score=score,
            conditions=conditions,
            mandatory_failures=mandatory_failures,
            missing_info=missing_info,
            summary_explanation=summary,
            max_benefit_lakhs=float(scheme.max_benefit_amount_lakhs) if scheme.max_benefit_amount_lakhs else None,
            support_type=scheme.support_type,
        )

    def _compute_status(
        self, mandatory_total, mandatory_pass, mandatory_failures,
        preferred_total, preferred_pass, missing_info
    ) -> tuple[str, float]:
        if mandatory_failures:
            return ELIGIBILITY_STATUS['DOES_NOT_MATCH'], 0.0
        
        # Score = mandatory pass rate * 0.7 + preferred pass rate * 0.3
        m_score = (mandatory_pass / mandatory_total) if mandatory_total > 0 else 1.0
        p_score = (preferred_pass / preferred_total) if preferred_total > 0 else 1.0
        score = round(m_score * 0.7 + p_score * 0.3, 2)

        if missing_info:
            if mandatory_pass == mandatory_total and not mandatory_failures:
                return ELIGIBILITY_STATUS['POTENTIAL_MATCH'], score
            return ELIGIBILITY_STATUS['UNKNOWN'], score * 0.5
        
        if score >= 0.85:
            return ELIGIBILITY_STATUS['MATCH'], score
        elif score >= 0.60:
            return ELIGIBILITY_STATUS['POTENTIAL_MATCH'], score
        else:
            return ELIGIBILITY_STATUS['DOES_NOT_MATCH'], score

    def evaluate_batch(self, schemes: list[Scheme], profile: BusinessProfile) -> list[EligibilityResult]:
        """
        Batch evaluate multiple schemes against a profile with zero N+1 queries.
        Ensures all rules are loaded in a single prefetch query if not already cached.
        """
        if not schemes:
            return []

        # Check if any scheme lacks prefetched rules
        needs_prefetch = any(
            not hasattr(s, '_prefetched_objects_cache') or 'rules' not in s._prefetched_objects_cache
            for s in schemes
        )
        if needs_prefetch:
            from django.db.models import prefetch_related_objects
            prefetch_related_objects(schemes, 'rules')

        return [self.evaluate(s, profile) for s in schemes]

    def _pass_explanation(self, rule: SchemeRule, actual_value: Any) -> str:
        label = rule.display_label or rule.rule_name
        if rule.operator == 'bool_true':
            return f"✓ {label} - confirmed"
        elif rule.operator in ('gte', 'gt', 'lte', 'lt'):
            return f"✓ {label}: {actual_value} meets requirement {rule.operator} {rule.expected_value}"
        elif rule.operator == 'in':
            return f"✓ {label}: '{actual_value}' is eligible"
        return f"✓ {label} - requirement met"

    def _build_summary(self, status, failures, missing, scheme_name):
        if status == 'MATCH':
            return f"Your business meets all eligibility criteria for {scheme_name}."
        elif status == 'POTENTIAL_MATCH':
            parts = []
            if failures:
                parts.append(f"Some conditions not met: {', '.join(failures[:2])}")
            if missing:
                parts.append(f"Provide more information: {', '.join(missing[:2])}")
            return f"Likely eligible for {scheme_name}. " + ". ".join(parts)
        elif status == 'DOES_NOT_MATCH':
            return f"Does not meet mandatory conditions for {scheme_name}: {', '.join(failures[:3])}."
        return f"Insufficient information to determine eligibility for {scheme_name}."


# Clean re-exports of advanced Deterministic Eligibility DSL
from apps.eligibility.dsl import (
    FactType,
    Operator,
    ConditionStatus,
    OverallEligibilityStatus,
    UnknownBehavior,
    RuleDefinition,
    ConditionEvaluationResult,
    RuleEvaluationReport,
    DeterministicRuleEvaluator,
    Money,
    calculate_msme_category
)
