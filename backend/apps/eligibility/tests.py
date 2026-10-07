"""
Unit tests for the Deterministic Eligibility Rule Engine.
Validates zero-hallucination rule evaluation against official policy thresholds.
"""
from django.test import TestCase
from apps.policies.models import Scheme, SchemeRule
from apps.business_profiles.models import BusinessProfile, BusinessGoal
from apps.eligibility.engine import RuleEngine


class RuleEngineTestCase(TestCase):
    def setUp(self):
        self.engine = RuleEngine()

        # Create benchmark test profile (Ahmedabad Small MSME)
        self.profile = BusinessProfile.objects.create(
            business_name="ABC Precision Tooling LLP",
            msme_category="small",
            entity_type="llp",
            industry_sector="Manufacturing",
            state="Gujarat",
            district="Ahmedabad",
            investment_in_plant_machinery_lakhs=50.0,
            annual_turnover_lakhs=180.0,
            is_women_owned=False,
            is_sc_st_owned=False,
            is_npa=False,
            has_bank_account=True,
            has_existing_loan=False,
            years_in_operation=4,
            total_employees=18,
        )

        # Create Gujarat MSME Scheme
        self.scheme = Scheme.objects.create(
            scheme_code="GJ_MSME_CAP_TEST",
            name="Gujarat MSME Capital Subsidy Scheme 2020",
            short_name="Gujarat Capital Subsidy",
            ministry_department="Industries and Mines Department, Government of Gujarat",
            level="state_gujarat",
            support_type="capital_subsidy",
            max_benefit_amount_lakhs=25.0,
            benefit_percentage=25.0,
            benefit_description="25% capital subsidy on eligible plant and machinery.",
            description="Scheme incentivizing manufacturing enterprises in Gujarat.",
            status="active"
        )

        # Rule 1: Must be in Gujarat (Mandatory)
        self.rule_state = SchemeRule.objects.create(
            scheme=self.scheme,
            rule_name="State Jurisdiction",
            field_path="state",
            operator="eq",
            expected_value="Gujarat",
            importance="mandatory",
            source_clause="Clause 3.1: Eligible units must be registered in the State of Gujarat",
            display_label="Registered in Gujarat",
            order=1
        )

        # Rule 2: Plant & Machinery Investment <= 1000 Lakhs (Mandatory)
        self.rule_investment = SchemeRule.objects.create(
            scheme=self.scheme,
            rule_name="Investment Upper Cap",
            field_path="investment_in_plant_machinery_lakhs",
            operator="lte",
            expected_value=1000.0,
            importance="mandatory",
            source_clause="Clause 4.2: Maximum eligible plant investment capped at ₹10 Crores",
            display_label="Plant Investment <= ₹10 Cr",
            order=2
        )

        # Rule 3: Must not be NPA (Mandatory)
        self.rule_npa = SchemeRule.objects.create(
            scheme=self.scheme,
            rule_name="No NPA Overdues",
            field_path="is_npa",
            operator="bool_false",
            expected_value=False,
            importance="mandatory",
            source_clause="Clause 5.1: Unit must not be declared NPA by any lending institution",
            display_label="Clean Non-NPA Credit Record",
            order=3
        )

        # Rule 4: Priority Category (Bonus)
        self.rule_bonus = SchemeRule.objects.create(
            scheme=self.scheme,
            rule_name="Women / SC-ST Priority Bonus",
            field_path="is_women_owned",
            operator="bool_true",
            expected_value=True,
            importance="bonus",
            source_clause="Clause 6.3: Additional 5% subsidy for women-owned enterprises",
            display_label="Women Ownership Bonus",
            order=4
        )

    def test_full_match_evaluation(self):
        """Profile meeting all mandatory criteria should evaluate to MATCH."""
        result = self.engine.evaluate(self.scheme, self.profile)
        self.assertEqual(result.overall_status, "MATCH")
        self.assertEqual(len(result.mandatory_failures), 0)
        self.assertTrue(result.score > 0.7)

    def test_mandatory_failure_evaluation(self):
        """Profile violating a mandatory condition should strictly evaluate to DOES_NOT_MATCH."""
        self.profile.is_npa = True
        self.profile.save()

        result = self.engine.evaluate(self.scheme, self.profile)
        self.assertEqual(result.overall_status, "DOES_NOT_MATCH")
        self.assertIn("Clean Non-NPA Credit Record", result.mandatory_failures[0])

    def test_unknown_field_handling(self):
        """Missing profile fact should result in UNKNOWN status without raising an exception."""
        self.profile.investment_in_plant_machinery_lakhs = None
        self.profile.save()

        result = self.engine.evaluate(self.scheme, self.profile)
        self.assertIn(result.overall_status, ["POTENTIAL_MATCH", "UNKNOWN"])
        self.assertTrue(len(result.missing_info) > 0)
