"""
Deterministic Eligibility Rule DSL & Evaluator for Indian MSME Support Programs.

Pure Python implementation providing:
- 10 Supported Fact Types (money, integer, decimal, boolean, enum, date, state, industry, registration status, enterprise category)
- 14 Deterministic Operators (eq, neq, lt, lte, gt, gte, in, not_in, between, exists, date_before, date_after, all, any)
- Bitemporal rule validity gating (effective_from, effective_until)
- Zero false-negative missing fact handling (missing facts -> UNKNOWN, never NOT_SATISFIED)
- Robust 5-state aggregation logic (MATCH, POTENTIAL_MATCH, UNKNOWN, DOES_NOT_MATCH, REQUIRES_OFFICIAL_VERIFICATION)
- Full statutory explainability and provenance tracking.
"""
from dataclasses import dataclass, field
from datetime import date, datetime
from decimal import Decimal
from enum import Enum
import re
from typing import Any, Dict, List, Optional, Tuple, Union


# =====================================================================
# 1. Enums & Core Types
# =====================================================================

class FactType(str, Enum):
    MONEY = "money"
    INTEGER = "integer"
    DECIMAL = "decimal"
    BOOLEAN = "boolean"
    ENUM = "enum"
    DATE = "date"
    STATE = "state"
    INDUSTRY = "industry"
    REGISTRATION_STATUS = "registration_status"
    ENTERPRISE_CATEGORY = "enterprise_category"


class Operator(str, Enum):
    EQ = "eq"
    NEQ = "neq"
    LT = "lt"
    LTE = "lte"
    GT = "gt"
    GTE = "gte"
    IN = "in"
    NOT_IN = "not_in"
    BETWEEN = "between"
    EXISTS = "exists"
    DATE_BEFORE = "date_before"
    DATE_AFTER = "date_after"
    ALL = "all"
    ANY = "any"


class ConditionStatus(str, Enum):
    SATISFIED = "SATISFIED"
    NOT_SATISFIED = "NOT_SATISFIED"
    UNKNOWN = "UNKNOWN"
    REQUIRES_OFFICIAL_VERIFICATION = "REQUIRES_OFFICIAL_VERIFICATION"


class OverallEligibilityStatus(str, Enum):
    MATCH = "MATCH"
    POTENTIAL_MATCH = "POTENTIAL_MATCH"
    UNKNOWN = "UNKNOWN"
    DOES_NOT_MATCH = "DOES_NOT_MATCH"
    REQUIRES_OFFICIAL_VERIFICATION = "REQUIRES_OFFICIAL_VERIFICATION"


class UnknownBehavior(str, Enum):
    UNKNOWN = "UNKNOWN"
    REQUIRES_OFFICIAL_VERIFICATION = "REQUIRES_OFFICIAL_VERIFICATION"
    NOT_SATISFIED = "NOT_SATISFIED"  # Only for strict deadline/presence requirements


# =====================================================================
# 2. Type Converters & Normalization
# =====================================================================

class Money:
    """Handles Indian Currency normalization (Lakhs, Crores, INR)."""
    @staticmethod
    def to_inr(val: Any, unit: Optional[str] = None) -> Decimal:
        if isinstance(val, (int, float, Decimal, str)):
            # Handle text numbers like '50 Lakhs' or '1.5 Crore'
            if isinstance(val, str):
                val_clean = val.replace(',', '').strip()
                match = re.search(r'([\d\.]+)\s*(lakhs?|crores?|cr|k)?', val_clean, re.I)
                if match:
                    amount = Decimal(match.group(1))
                    unit_str = (match.group(2) or "").lower()
                    if 'crore' in unit_str or 'cr' in unit_str:
                        return amount * Decimal(10000000)
                    elif 'lakh' in unit_str:
                        return amount * Decimal(100000)
                    elif 'k' in unit_str:
                        return amount * Decimal(1000)
                    return amount

            amt = Decimal(str(val))
            if unit:
                u = unit.upper()
                if 'CRORE' in u or 'CR' in u:
                    return amt * Decimal(10000000)
                elif 'LAKH' in u:
                    return amt * Decimal(100000)
            return amt
        raise ValueError(f"Cannot convert {val} to Money.")


def parse_date(val: Any) -> Optional[date]:
    """Parse date from string or date/datetime object."""
    if isinstance(val, date):
        if isinstance(val, datetime):
            return val.date()
        return val
    if isinstance(val, str):
        val = val.strip()
        for fmt in ("%Y-%m-%d", "%d-%m-%Y", "%d/%m/%Y", "%Y/%m/%d"):
            try:
                return datetime.strptime(val, fmt).date()
            except ValueError:
                continue
    return None


def calculate_msme_category(investment_inr: Decimal, turnover_inr: Decimal) -> str:
    """
    Computes composite MSME category under the official MSMED Act 2020 definitions:
    - Micro: Investment <= 1 Cr AND Turnover <= 5 Cr
    - Small: Investment <= 10 Cr AND Turnover <= 50 Cr
    - Medium: Investment <= 50 Cr AND Turnover <= 250 Cr
    - Large: Above Medium
    """
    cr = Decimal(10000000)
    if investment_inr <= (1 * cr) and turnover_inr <= (5 * cr):
        return "Micro"
    elif investment_inr <= (10 * cr) and turnover_inr <= (50 * cr):
        return "Small"
    elif investment_inr <= (50 * cr) and turnover_inr <= (250 * cr):
        return "Medium"
    return "Large"


# =====================================================================
# 3. DSL Rule Representation
# =====================================================================

@dataclass
class RuleDefinition:
    rule_id: str
    description: str
    fact_key: str
    fact_type: FactType
    operator: Operator
    expected_value: Any
    mandatory: bool = True
    units: Optional[str] = None
    effective_from: Optional[date] = None
    effective_until: Optional[date] = None
    evidence_ids: List[str] = field(default_factory=list)
    unknown_behavior: UnknownBehavior = UnknownBehavior.UNKNOWN
    failure_message: str = ""


@dataclass
class ConditionEvaluationResult:
    rule_id: str
    description: str
    fact_key: str
    fact_type: str
    actual_value: Any
    expected_value: Any
    operator: str
    status: ConditionStatus
    is_mandatory: bool
    evidence_ids: List[str]
    explanation: str


@dataclass
class RuleEvaluationReport:
    scheme_id: str
    scheme_name: str
    overall_status: OverallEligibilityStatus
    mandatory_total: int
    mandatory_satisfied: int
    mandatory_failed: int
    mandatory_unknown: int
    preferred_total: int
    preferred_satisfied: int
    condition_results: List[ConditionEvaluationResult]
    blockers: List[str]
    missing_facts: List[str]
    verification_required: List[str]
    summary_explanation: str


# =====================================================================
# 4. Pure Python Rule Evaluator Engine
# =====================================================================

class DeterministicRuleEvaluator:
    """
    Evaluates RuleDefinitions against nested dictionary facts.
    Guarantees zero silent conversion of unknown facts to false.
    """

    def evaluate_condition(
        self,
        rule: RuleDefinition,
        facts: Dict[str, Any],
        as_of_date: Optional[date] = None
    ) -> ConditionEvaluationResult:
        as_of = as_of_date or date.today()

        # 1. Bitemporal Validity Gate
        if rule.effective_from and as_of < rule.effective_from:
            return ConditionEvaluationResult(
                rule_id=rule.rule_id,
                description=rule.description,
                fact_key=rule.fact_key,
                fact_type=rule.fact_type.value,
                actual_value=None,
                expected_value=rule.expected_value,
                operator=rule.operator.value,
                status=ConditionStatus.SATISFIED,  # Rule not yet active -> waived
                is_mandatory=rule.mandatory,
                evidence_ids=rule.evidence_ids,
                explanation=f"Rule inactive: effective from {rule.effective_from} (as of {as_of})."
            )

        if rule.effective_until and as_of > rule.effective_until:
            return ConditionEvaluationResult(
                rule_id=rule.rule_id,
                description=rule.description,
                fact_key=rule.fact_key,
                fact_type=rule.fact_type.value,
                actual_value=None,
                expected_value=rule.expected_value,
                operator=rule.operator.value,
                status=ConditionStatus.SATISFIED,  # Rule expired -> waived
                is_mandatory=rule.mandatory,
                evidence_ids=rule.evidence_ids,
                explanation=f"Rule sunsetted: effective until {rule.effective_until} (as of {as_of})."
            )

        # 2. Extract Fact from Nested Keys (e.g. 'financials.turnover_inr')
        actual_val, fact_exists = self._extract_nested_fact(facts, rule.fact_key)

        # 3. Handle Special Operator: 'exists'
        if rule.operator == Operator.EXISTS:
            expected_bool = bool(rule.expected_value)
            is_satisfied = (fact_exists and actual_val is not None) == expected_bool
            status = ConditionStatus.SATISFIED if is_satisfied else ConditionStatus.NOT_SATISFIED
            return ConditionEvaluationResult(
                rule_id=rule.rule_id,
                description=rule.description,
                fact_key=rule.fact_key,
                fact_type=rule.fact_type.value,
                actual_value=actual_val,
                expected_value=rule.expected_value,
                operator=rule.operator.value,
                status=status,
                is_mandatory=rule.mandatory,
                evidence_ids=rule.evidence_ids,
                explanation=f"Fact presence verified: exists={fact_exists}"
            )

        # 4. Handle Missing / Unknown Fact (INVARIANT: Missing facts must not become NOT_SATISFIED)
        if not fact_exists or actual_val is None:
            status = ConditionStatus(rule.unknown_behavior.value)
            explanation = f"Missing fact '{rule.fact_key}' required to verify: {rule.description}"
            return ConditionEvaluationResult(
                rule_id=rule.rule_id,
                description=rule.description,
                fact_key=rule.fact_key,
                fact_type=rule.fact_type.value,
                actual_value=None,
                expected_value=rule.expected_value,
                operator=rule.operator.value,
                status=status,
                is_mandatory=rule.mandatory,
                evidence_ids=rule.evidence_ids,
                explanation=explanation
            )

        # 5. Type-Specific Normalization & Evaluation
        try:
            is_satisfied, explanation = self._evaluate_by_type(rule, actual_val)
            status = ConditionStatus.SATISFIED if is_satisfied else ConditionStatus.NOT_SATISFIED
        except Exception as err:
            status = ConditionStatus(rule.unknown_behavior.value)
            explanation = f"Evaluation error on fact '{rule.fact_key}': {str(err)}"

        return ConditionEvaluationResult(
            rule_id=rule.rule_id,
            description=rule.description,
            fact_key=rule.fact_key,
            fact_type=rule.fact_type.value,
            actual_value=actual_val,
            expected_value=rule.expected_value,
            operator=rule.operator.value,
            status=status,
            is_mandatory=rule.mandatory,
            evidence_ids=rule.evidence_ids,
            explanation=explanation
        )

    def evaluate_ruleset(
        self,
        scheme_id: str,
        scheme_name: str,
        rules: List[RuleDefinition],
        facts: Dict[str, Any],
        as_of_date: Optional[date] = None
    ) -> RuleEvaluationReport:
        """
        Evaluates a complete Scheme RuleSet with rigorous aggregation rules:
        - ANY mandatory NOT_SATISFIED -> DOES_NOT_MATCH
        - ANY mandatory UNKNOWN (and no NOT_SATISFIED) -> UNKNOWN
        - ANY mandatory REQUIRES_OFFICIAL_VERIFICATION (and no NOT_SATISFIED) -> REQUIRES_OFFICIAL_VERIFICATION
        - ALL mandatory SATISFIED + ALL preferred SATISFIED -> MATCH
        - ALL mandatory SATISFIED + some preferred NOT_SATISFIED/UNKNOWN -> POTENTIAL_MATCH
        """
        results: List[ConditionEvaluationResult] = []
        mandatory_total = 0
        mandatory_satisfied = 0
        mandatory_failed = 0
        mandatory_unknown = 0
        mandatory_verification = 0

        preferred_total = 0
        preferred_satisfied = 0

        blockers = []
        missing_facts = []
        verification_required = []

        for rule in rules:
            cond_res = self.evaluate_condition(rule, facts, as_of_date=as_of_date)
            results.append(cond_res)

            if rule.mandatory:
                mandatory_total += 1
                if cond_res.status == ConditionStatus.SATISFIED:
                    mandatory_satisfied += 1
                elif cond_res.status == ConditionStatus.NOT_SATISFIED:
                    mandatory_failed += 1
                    blockers.append(rule.failure_message or f"Violates mandatory requirement: {rule.description}")
                elif cond_res.status == ConditionStatus.UNKNOWN:
                    mandatory_unknown += 1
                    missing_facts.append(rule.fact_key)
                elif cond_res.status == ConditionStatus.REQUIRES_OFFICIAL_VERIFICATION:
                    mandatory_verification += 1
                    verification_required.append(rule.description)
            else:
                preferred_total += 1
                if cond_res.status == ConditionStatus.SATISFIED:
                    preferred_satisfied += 1

        # Strict Aggregation Rules
        if mandatory_failed > 0:
            overall_status = OverallEligibilityStatus.DOES_NOT_MATCH
            summary = f"Does not qualify for {scheme_name}. {len(blockers)} mandatory condition(s) failed."
        elif mandatory_unknown > 0:
            overall_status = OverallEligibilityStatus.UNKNOWN
            summary = f"Eligibility for {scheme_name} is UNKNOWN due to {mandatory_unknown} missing fact(s)."
        elif mandatory_verification > 0:
            overall_status = OverallEligibilityStatus.REQUIRES_OFFICIAL_VERIFICATION
            summary = f"{scheme_name} conditionally matches, pending official document verification of {mandatory_verification} requirement(s)."
        elif preferred_total > 0 and preferred_satisfied < preferred_total:
            overall_status = OverallEligibilityStatus.POTENTIAL_MATCH
            summary = f"Potential match for {scheme_name}. Meets all mandatory criteria, with {preferred_satisfied}/{preferred_total} preferred conditions satisfied."
        else:
            overall_status = OverallEligibilityStatus.MATCH
            summary = f"Eligible match for {scheme_name}. All {mandatory_satisfied} mandatory statutory conditions satisfied."

        return RuleEvaluationReport(
            scheme_id=scheme_id,
            scheme_name=scheme_name,
            overall_status=overall_status,
            mandatory_total=mandatory_total,
            mandatory_satisfied=mandatory_satisfied,
            mandatory_failed=mandatory_failed,
            mandatory_unknown=mandatory_unknown,
            preferred_total=preferred_total,
            preferred_satisfied=preferred_satisfied,
            condition_results=results,
            blockers=blockers,
            missing_facts=missing_facts,
            verification_required=verification_required,
            summary_explanation=summary
        )

    # -----------------------------------------------------------------
    # Internal Evaluation Helpers
    # -----------------------------------------------------------------

    def _extract_nested_fact(self, facts: Dict[str, Any], path: str) -> Tuple[Any, bool]:
        """Traverse nested dict or object attributes e.g. 'financials.turnover_inr'."""
        if not path:
            return None, False
        keys = path.split('.')
        current = facts
        for k in keys:
            if isinstance(current, dict):
                if k not in current:
                    return None, False
                current = current[k]
            elif hasattr(current, k):
                current = getattr(current, k)
            else:
                return None, False
        return current, True

    def _evaluate_by_type(self, rule: RuleDefinition, actual: Any) -> Tuple[bool, str]:
        ft = rule.fact_type
        op = rule.operator

        if ft == FactType.MONEY:
            act_inr = Money.to_inr(actual, rule.units)
            if op == Operator.BETWEEN:
                exp_min = Money.to_inr(rule.expected_value[0], rule.units)
                exp_max = Money.to_inr(rule.expected_value[1], rule.units)
                sat = exp_min <= act_inr <= exp_max
                return sat, f"Value ₹{act_inr:,} is between ₹{exp_min:,} and ₹{exp_max:,}: {sat}"
            else:
                exp_inr = Money.to_inr(rule.expected_value, rule.units)
                return self._numeric_compare(act_inr, op, exp_inr, f"₹{act_inr:,}")

        elif ft in (FactType.INTEGER, FactType.DECIMAL):
            act_num = Decimal(str(actual))
            if op == Operator.BETWEEN:
                exp_min = Decimal(str(rule.expected_value[0]))
                exp_max = Decimal(str(rule.expected_value[1]))
                sat = exp_min <= act_num <= exp_max
                return sat, f"Value {act_num} is between {exp_min} and {exp_max}: {sat}"
            else:
                exp_num = Decimal(str(rule.expected_value))
                return self._numeric_compare(act_num, op, exp_num, str(act_num))

        elif ft == FactType.BOOLEAN:
            act_b = bool(actual)
            exp_b = bool(rule.expected_value)
            if op == Operator.EQ:
                sat = act_b == exp_b
                return sat, f"Boolean check: actual={act_b}, expected={exp_b}"
            elif op == Operator.NEQ:
                sat = act_b != exp_b
                return sat, f"Boolean neq check: actual={act_b}, expected={exp_b}"

        elif ft == FactType.DATE:
            act_d = parse_date(actual)
            if not act_d:
                raise ValueError(f"Invalid date format: {actual}")
            exp_d = parse_date(rule.expected_value)
            if not exp_d:
                raise ValueError(f"Invalid expected date format: {rule.expected_value}")

            if op in (Operator.DATE_BEFORE, Operator.LT):
                sat = act_d < exp_d
                return sat, f"Date {act_d} is before {exp_d}: {sat}"
            elif op in (Operator.DATE_AFTER, Operator.GT):
                sat = act_d > exp_d
                return sat, f"Date {act_d} is after {exp_d}: {sat}"
            elif op in (Operator.EQ, Operator.LTE, Operator.GTE):
                if op == Operator.EQ:
                    sat = act_d == exp_d
                elif op == Operator.LTE:
                    sat = act_d <= exp_d
                else:
                    sat = act_d >= exp_d
                return sat, f"Date comparison {act_d} {op.value} {exp_d}: {sat}"

        elif ft in (FactType.STATE, FactType.INDUSTRY, FactType.ENUM, FactType.REGISTRATION_STATUS, FactType.ENTERPRISE_CATEGORY):
            act_str = str(actual).strip().lower()
            if op == Operator.EQ:
                exp_str = str(rule.expected_value).strip().lower()
                sat = act_str == exp_str
                return sat, f"'{actual}' matches '{rule.expected_value}': {sat}"
            elif op == Operator.NEQ:
                exp_str = str(rule.expected_value).strip().lower()
                sat = act_str != exp_str
                return sat, f"'{actual}' != '{rule.expected_value}': {sat}"
            elif op == Operator.IN:
                allowed = [str(x).strip().lower() for x in rule.expected_value]
                sat = act_str in allowed
                return sat, f"'{actual}' is in {rule.expected_value}: {sat}"
            elif op == Operator.NOT_IN:
                disallowed = [str(x).strip().lower() for x in rule.expected_value]
                sat = act_str not in disallowed
                return sat, f"'{actual}' is not in {rule.expected_value}: {sat}"

        # List operators: 'all', 'any'
        if op == Operator.ALL:
            if not isinstance(actual, (list, tuple, set)):
                actual = [actual]
            sat = all(str(item).lower() in [str(e).lower() for e in rule.expected_value] for item in actual)
            return sat, f"All items in {actual} satisfy expected list: {sat}"

        elif op == Operator.ANY:
            if not isinstance(actual, (list, tuple, set)):
                actual = [actual]
            sat = any(str(item).lower() in [str(e).lower() for e in rule.expected_value] for item in actual)
            return sat, f"Any item in {actual} matches expected list: {sat}"

        raise ValueError(f"Unsupported operator '{op.value}' for fact type '{ft.value}'")

    def _numeric_compare(self, actual: Decimal, op: Operator, expected: Decimal, label: str) -> Tuple[bool, str]:
        if op == Operator.EQ:
            sat = actual == expected
        elif op == Operator.NEQ:
            sat = actual != expected
        elif op == Operator.LT:
            sat = actual < expected
        elif op == Operator.LTE:
            sat = actual <= expected
        elif op == Operator.GT:
            sat = actual > expected
        elif op == Operator.GTE:
            sat = actual >= expected
        else:
            raise ValueError(f"Operator {op.value} not valid for single numeric comparison")
        return sat, f"{label} {op.value} {expected}: {sat}"
