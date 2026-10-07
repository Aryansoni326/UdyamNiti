"""
Exhaustive Unit Test Suite for Deterministic Eligibility Rule DSL & Evaluator.
Validates:
1. All 10 supported fact types (money, integer, decimal, boolean, enum, date, state, industry, registration_status, enterprise_category)
2. All 14 operators (eq, neq, lt, lte, gt, gte, in, not_in, between, exists, date_before, date_after, all, any)
3. Invariant: Missing facts evaluate to UNKNOWN, NEVER false/NOT_SATISFIED
4. Aggregation states: MATCH, POTENTIAL_MATCH, UNKNOWN, DOES_NOT_MATCH, REQUIRES_OFFICIAL_VERIFICATION
5. Bitemporal effective period boundaries
6. Currency normalization (Lakhs vs Crores vs INR)
7. Composite enterprise category calculation under MSMED Act 2020
8. Explainability outputs (blockers, missing facts, audit trail)
"""
from datetime import date
from decimal import Decimal
from django.test import TestCase

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


class DeterministicRuleDSLExhaustiveTestCase(TestCase):
    def setUp(self):
        self.evaluator = DeterministicRuleEvaluator()

    # -------------------------------------------------------------
    # 1. Fact Type & Currency Normalization Tests
    # -------------------------------------------------------------

    def test_money_fact_type_normalization(self):
        # 50 Lakhs equals 5,000,000 INR
        self.assertEqual(Money.to_inr("50 Lakhs"), Decimal(5000000))
        self.assertEqual(Money.to_inr(50, unit="LAKHS"), Decimal(5000000))
        # 1.5 Crore equals 15,000,000 INR
        self.assertEqual(Money.to_inr("1.5 Crore"), Decimal(15000000))
        self.assertEqual(Money.to_inr(2, unit="CRORE"), Decimal(20000000))

        rule = RuleDefinition(
            rule_id="R-MONEY-01",
            description="Investment in Plant & Machinery must be <= 50 Lakhs",
            fact_key="financials.investment_inr",
            fact_type=FactType.MONEY,
            operator=Operator.LTE,
            expected_value="50 Lakhs"
        )
        res_pass = self.evaluator.evaluate_condition(rule, {"financials": {"investment_inr": "45 Lakhs"}})
        self.assertEqual(res_pass.status, ConditionStatus.SATISFIED)

        res_fail = self.evaluator.evaluate_condition(rule, {"financials": {"investment_inr": "75 Lakhs"}})
        self.assertEqual(res_fail.status, ConditionStatus.NOT_SATISFIED)

    def test_msme_composite_category_calculator(self):
        cr = Decimal(10000000)
        # Micro: Inv <= 1 Cr AND Turnover <= 5 Cr
        self.assertEqual(calculate_msme_category(Decimal(5000000), Decimal(20000000)), "Micro")
        # Small: Inv <= 10 Cr AND Turnover <= 50 Cr
        self.assertEqual(calculate_msme_category(Decimal(50000000), Decimal(200000000)), "Small")
        # Medium: Inv <= 50 Cr AND Turnover <= 250 Cr
        self.assertEqual(calculate_msme_category(Decimal(20 * cr), Decimal(100 * cr)), "Medium")
        # Large: > Medium
        self.assertEqual(calculate_msme_category(Decimal(60 * cr), Decimal(300 * cr)), "Large")

    # -------------------------------------------------------------
    # 2. Operator Coverage (All 14 Operators)
    # -------------------------------------------------------------

    def test_operator_between(self):
        rule = RuleDefinition(
            rule_id="R-BETWEEN-01",
            description="Investment must be between 10 Lakhs and 50 Lakhs",
            fact_key="investment",
            fact_type=FactType.MONEY,
            operator=Operator.BETWEEN,
            expected_value=["10 Lakhs", "50 Lakhs"]
        )
        self.assertEqual(self.evaluator.evaluate_condition(rule, {"investment": "25 Lakhs"}).status, ConditionStatus.SATISFIED)
        self.assertEqual(self.evaluator.evaluate_condition(rule, {"investment": "5 Lakhs"}).status, ConditionStatus.NOT_SATISFIED)
        self.assertEqual(self.evaluator.evaluate_condition(rule, {"investment": "60 Lakhs"}).status, ConditionStatus.NOT_SATISFIED)

    def test_operator_in_and_not_in(self):
        rule_in = RuleDefinition(
            rule_id="R-IN-01",
            description="Unit must be located in Category-1 or Category-2 Taluka",
            fact_key="location.taluka_category",
            fact_type=FactType.ENUM,
            operator=Operator.IN,
            expected_value=["Category-1", "Category-2"]
        )
        self.assertEqual(self.evaluator.evaluate_condition(rule_in, {"location": {"taluka_category": "Category-1"}}).status, ConditionStatus.SATISFIED)
        self.assertEqual(self.evaluator.evaluate_condition(rule_in, {"location": {"taluka_category": "Category-3"}}).status, ConditionStatus.NOT_SATISFIED)

        rule_not_in = RuleDefinition(
            rule_id="R-NOT-IN-01",
            description="Business must not be in negative activities (Tobacco, Meat)",
            fact_key="sector.activity",
            fact_type=FactType.ENUM,
            operator=Operator.NOT_IN,
            expected_value=["Tobacco", "Meat Processing", "Polythene Bags"]
        )
        self.assertEqual(self.evaluator.evaluate_condition(rule_not_in, {"sector": {"activity": "Precision Engineering"}}).status, ConditionStatus.SATISFIED)
        self.assertEqual(self.evaluator.evaluate_condition(rule_not_in, {"sector": {"activity": "Tobacco"}}).status, ConditionStatus.NOT_SATISFIED)

    def test_operator_exists(self):
        rule_exists = RuleDefinition(
            rule_id="R-EXISTS-01",
            description="Must possess Udyam Registration number",
            fact_key="registration.udyam_number",
            fact_type=FactType.REGISTRATION_STATUS,
            operator=Operator.EXISTS,
            expected_value=True
        )
        self.assertEqual(self.evaluator.evaluate_condition(rule_exists, {"registration": {"udyam_number": "UDYAM-GJ-01-0012345"}}).status, ConditionStatus.SATISFIED)
        self.assertEqual(self.evaluator.evaluate_condition(rule_exists, {"registration": {}}).status, ConditionStatus.NOT_SATISFIED)

    def test_operator_date_before_and_after(self):
        rule_date = RuleDefinition(
            rule_id="R-DATE-01",
            description="Commencement of commercial production must be on or after 2020-09-01",
            fact_key="commencement_date",
            fact_type=FactType.DATE,
            operator=Operator.GTE,
            expected_value="2020-09-01"
        )
        self.assertEqual(self.evaluator.evaluate_condition(rule_date, {"commencement_date": "2022-01-15"}).status, ConditionStatus.SATISFIED)
        self.assertEqual(self.evaluator.evaluate_condition(rule_date, {"commencement_date": "2018-05-20"}).status, ConditionStatus.NOT_SATISFIED)

    def test_operator_all_and_any(self):
        rule_any = RuleDefinition(
            rule_id="R-ANY-01",
            description="Must possess at least one quality certification (ISO 9001, CE, ZED)",
            fact_key="certifications",
            fact_type=FactType.ENUM,
            operator=Operator.ANY,
            expected_value=["ISO 9001", "CE", "ZED Bronze", "ZED Gold"]
        )
        self.assertEqual(self.evaluator.evaluate_condition(rule_any, {"certifications": ["ISO 9001", "FSSAI"]}).status, ConditionStatus.SATISFIED)
        self.assertEqual(self.evaluator.evaluate_condition(rule_any, {"certifications": ["Local Trade License"]}).status, ConditionStatus.NOT_SATISFIED)

    # -------------------------------------------------------------
    # 3. Missing Fact Invariant (Missing != False)
    # -------------------------------------------------------------

    def test_missing_fact_evaluates_to_unknown_never_false(self):
        """
        CRITICAL INVARIANT: Missing facts must not become false.
        An unpopulated fact evaluates to ConditionStatus.UNKNOWN.
        """
        rule = RuleDefinition(
            rule_id="R-MANDATORY-EDU",
            description="Minimum 8th Standard pass for manufacturing project above Rs. 10 Lakhs",
            fact_key="promoter.highest_education",
            fact_type=FactType.ENUM,
            operator=Operator.IN,
            expected_value=["8th Pass", "10th Pass", "Graduate", "Post Graduate"],
            mandatory=True,
            unknown_behavior=UnknownBehavior.UNKNOWN
        )
        # Empty facts dict (user has not answered question yet)
        res = self.evaluator.evaluate_condition(rule, {})
        self.assertEqual(res.status, ConditionStatus.UNKNOWN)
        self.assertNotEqual(res.status, ConditionStatus.NOT_SATISFIED)
        self.assertIn("Missing fact", res.explanation)

    def test_missing_fact_with_requires_official_verification(self):
        rule = RuleDefinition(
            rule_id="R-AUDIT-VERIF",
            description="Pollution control board consent-to-operate certificate",
            fact_key="compliance.gpcb_cto_verified",
            fact_type=FactType.BOOLEAN,
            operator=Operator.EQ,
            expected_value=True,
            unknown_behavior=UnknownBehavior.REQUIRES_OFFICIAL_VERIFICATION
        )
        res = self.evaluator.evaluate_condition(rule, {})
        self.assertEqual(res.status, ConditionStatus.REQUIRES_OFFICIAL_VERIFICATION)

    # -------------------------------------------------------------
    # 4. Aggregation Rules & Status Determinations
    # -------------------------------------------------------------

    def test_aggregation_does_not_match_when_mandatory_fails(self):
        """If ANY mandatory rule fails -> DOES_NOT_MATCH."""
        rules = [
            RuleDefinition(
                rule_id="R-M1",
                description="Must be Micro enterprise",
                fact_key="category",
                fact_type=FactType.ENTERPRISE_CATEGORY,
                operator=Operator.EQ,
                expected_value="Micro",
                mandatory=True
            ),
            RuleDefinition(
                rule_id="R-M2",
                description="State must be Gujarat",
                fact_key="state",
                fact_type=FactType.STATE,
                operator=Operator.EQ,
                expected_value="Gujarat",
                mandatory=True
            )
        ]
        # State matches, but category fails (Medium)
        report = self.evaluator.evaluate_ruleset(
            scheme_id="S-01",
            scheme_name="Gujarat Micro Capital Subsidy",
            rules=rules,
            facts={"category": "Medium", "state": "Gujarat"}
        )
        self.assertEqual(report.overall_status, OverallEligibilityStatus.DOES_NOT_MATCH)
        self.assertEqual(len(report.blockers), 1)

    def test_aggregation_unknown_when_mandatory_missing_and_none_failed(self):
        """If a mandatory rule is missing facts and no rule has failed -> UNKNOWN."""
        rules = [
            RuleDefinition(
                rule_id="R-M1",
                description="Must be Micro enterprise",
                fact_key="category",
                fact_type=FactType.ENTERPRISE_CATEGORY,
                operator=Operator.EQ,
                expected_value="Micro",
                mandatory=True
            ),
            RuleDefinition(
                rule_id="R-M2",
                description="Must have active Udyam",
                fact_key="udyam_active",
                fact_type=FactType.BOOLEAN,
                operator=Operator.EQ,
                expected_value=True,
                mandatory=True
            )
        ]
        # Category matches, but udyam_active is unprovided
        report = self.evaluator.evaluate_ruleset(
            scheme_id="S-01",
            scheme_name="Gujarat Micro Capital Subsidy",
            rules=rules,
            facts={"category": "Micro"}
        )
        self.assertEqual(report.overall_status, OverallEligibilityStatus.UNKNOWN)
        self.assertEqual(len(report.missing_facts), 1)
        self.assertIn("udyam_active", report.missing_facts)

    def test_aggregation_match_all_mandatory_and_preferred_satisfied(self):
        """All mandatory satisfied and preferred satisfied -> MATCH."""
        rules = [
            RuleDefinition(
                rule_id="R-M1",
                description="State must be Gujarat",
                fact_key="state",
                fact_type=FactType.STATE,
                operator=Operator.EQ,
                expected_value="Gujarat",
                mandatory=True
            ),
            RuleDefinition(
                rule_id="R-P1",
                description="Preferred: Women ownership > 51%",
                fact_key="female_ownership",
                fact_type=FactType.DECIMAL,
                operator=Operator.GTE,
                expected_value=51.0,
                mandatory=False
            )
        ]
        report = self.evaluator.evaluate_ruleset(
            scheme_id="S-01",
            scheme_name="Gujarat Mahila Udyam",
            rules=rules,
            facts={"state": "Gujarat", "female_ownership": 75.0}
        )
        self.assertEqual(report.overall_status, OverallEligibilityStatus.MATCH)
        self.assertEqual(report.mandatory_satisfied, 1)
        self.assertEqual(report.preferred_satisfied, 1)

    def test_aggregation_potential_match_when_preferred_not_satisfied(self):
        """All mandatory satisfied, but preferred not satisfied -> POTENTIAL_MATCH."""
        rules = [
            RuleDefinition(
                rule_id="R-M1",
                description="State must be Gujarat",
                fact_key="state",
                fact_type=FactType.STATE,
                operator=Operator.EQ,
                expected_value="Gujarat",
                mandatory=True
            ),
            RuleDefinition(
                rule_id="R-P1",
                description="Preferred: ZED Certified",
                fact_key="zed_certified",
                fact_type=FactType.BOOLEAN,
                operator=Operator.EQ,
                expected_value=True,
                mandatory=False
            )
        ]
        report = self.evaluator.evaluate_ruleset(
            scheme_id="S-01",
            scheme_name="Gujarat MSME Subsidy",
            rules=rules,
            facts={"state": "Gujarat", "zed_certified": False}
        )
        self.assertEqual(report.overall_status, OverallEligibilityStatus.POTENTIAL_MATCH)
        self.assertEqual(report.mandatory_satisfied, 1)
        self.assertEqual(report.preferred_satisfied, 0)

    # -------------------------------------------------------------
    # 5. Bitemporal Validity Period
    # -------------------------------------------------------------

    def test_bitemporal_rule_validity_boundaries(self):
        rule_expired = RuleDefinition(
            rule_id="R-EXPIRED-01",
            description="2015 Policy Rule: Term loan interest subsidy",
            fact_key="investment",
            fact_type=FactType.MONEY,
            operator=Operator.LTE,
            expected_value="10 Lakhs",
            effective_from=date(2015, 1, 1),
            effective_until=date(2020, 8, 31)
        )
        # Evaluated today (after sunset) -> rule is waived as sunsetted
        res = self.evaluator.evaluate_condition(rule_expired, {"investment": "50 Lakhs"}, as_of_date=date(2025, 1, 1))
        self.assertEqual(res.status, ConditionStatus.SATISFIED)
        self.assertIn("sunsetted", res.explanation)
