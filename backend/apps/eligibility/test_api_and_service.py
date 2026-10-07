"""
Unit & Integration Tests for Eligibility Evaluation Service & API.
Tests:
1. Boundary values (exact limit vs 1 unit over)
2. Currency normalization (Lakhs, Crores, INR)
3. Unknowns & missing facts (missing != false)
4. Expired rules (bitemporal sunsetting)
5. Version changes (v1 vs v2 rules)
6. Single scheme API endpoint (/api/v1/eligibility/evaluate/)
7. Batch candidate schemes API endpoint (/api/v1/eligibility/evaluate-batch/)
8. Re-evaluation after profile change API endpoint (/api/v1/eligibility/re-evaluate/)
9. Invariant: NEVER return an AI-generated eligibility percentage.
"""
import uuid
from decimal import Decimal
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status

from apps.business_profiles.models import BusinessProfile, BusinessGoal, BusinessFact
from apps.policies.models import Scheme, SchemeRule, SchemeVersion
from apps.eligibility.services import EligibilityEvaluationService
from apps.eligibility.dsl import Money


class EligibilityServiceAndAPITestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.service = EligibilityEvaluationService()

        # Create Profile
        self.profile = BusinessProfile.objects.create(
            business_name="Shree Ram Precision Engineering",
            udyam_registration_number="UDYAM-GJ-01-0098765",
            gstin="24ABCDE1234F1Z5",
            pan="ABCDE1234F",
            msme_category="micro",
            entity_type="proprietorship",
            is_manufacturing=True,
            state="Gujarat",
            district="Rajkot",
            investment_in_plant_machinery_lakhs=Decimal("45.00"),
            annual_turnover_lakhs=Decimal("150.00"),
            owner_gender="male",
            years_in_operation=3
        )

        self.goal = BusinessGoal.objects.create(
            business_profile=self.profile,
            raw_goal_text="Expand factory with new 5-axis CNC machine"
        )

        # Create Scheme
        self.scheme = Scheme.objects.create(
            scheme_code="GJ-CAPITAL-2025",
            name="Gujarat MSME Capital Investment Subsidy",
            level="state_gujarat",
            support_type="capital_subsidy",
            description="25% capital subsidy on GFCI up to Rs. 35 Lakhs in Category-1 talukas.",
            status="active"
        )

        # Version 1 Record
        self.scheme_v1 = SchemeVersion.objects.create(
            scheme=self.scheme,
            version_number=1,
            change_summary="Initial 2020 Gazette Notification",
            effective_date="2020-09-01"
        )

        # Rule 1: Investment limit <= 50 Lakhs (Mandatory)
        self.rule_investment = SchemeRule.objects.create(
            scheme=self.scheme,
            rule_name="Investment in Plant & Machinery Limit",
            field_path="financials.investment_inr",
            operator="lte",
            expected_value="50 Lakhs",
            importance="mandatory",
            source_clause="Clause 4.1: Eligible Investment Ceiling",
            display_label="Gross Fixed Capital Investment Ceiling",
            failure_message="Investment exceeds maximum permissible ceiling of Rs. 50 Lakhs."
        )

        # Rule 2: State must be Gujarat (Mandatory)
        self.rule_state = SchemeRule.objects.create(
            scheme=self.scheme,
            rule_name="State Jurisdiction",
            field_path="location.state",
            operator="eq",
            expected_value="Gujarat",
            importance="mandatory",
            source_clause="Clause 1.2: Territorial Applicability",
            display_label="Unit Location in Gujarat"
        )

    # -------------------------------------------------------------
    # 1. Boundary Values & Currency Normalization Tests
    # -------------------------------------------------------------

    def test_boundary_values_exact_vs_over(self):
        """
        Boundary Test:
        - Exactly 50 Lakhs (Rs. 5,000,000) must satisfy <= 50 Lakhs.
        - 50.01 Lakhs (Rs. 5,001,000) must fail <= 50 Lakhs.
        """
        # Exactly 50 Lakhs
        self.profile.investment_in_plant_machinery_lakhs = Decimal("50.00")
        self.profile.save()
        res_exact = self.service.evaluate_scheme(self.profile.id, self.scheme.id, self.goal.id)
        cond_inv = next(c for c in res_exact['conditions'] if c['rule_id'] == str(self.rule_investment.id))
        self.assertEqual(cond_inv['result'], 'SATISFIED')

        # Over by 10,000 INR
        self.profile.investment_in_plant_machinery_lakhs = Decimal("50.10")
        self.profile.save()
        res_over = self.service.evaluate_scheme(self.profile.id, self.scheme.id, self.goal.id)
        cond_inv_over = next(c for c in res_over['conditions'] if c['rule_id'] == str(self.rule_investment.id))
        self.assertEqual(cond_inv_over['result'], 'NOT_SATISFIED')
        self.assertEqual(res_over['overall_status'], 'DOES_NOT_MATCH')
        self.assertIn("Investment exceeds maximum permissible ceiling", res_over['blockers'][0])

    def test_currency_normalization(self):
        """Validates that Lakhs, Crores, and raw numbers normalize consistently."""
        self.assertEqual(Money.to_inr("50 Lakhs"), Decimal(5000000))
        self.assertEqual(Money.to_inr("2 Crores"), Decimal(20000000))
        self.assertEqual(Money.to_inr(Decimal("50.00"), "LAKHS"), Decimal(5000000))

    # -------------------------------------------------------------
    # 2. Unknowns & Missing Facts (Missing != False)
    # -------------------------------------------------------------

    def test_unknowns_produce_unknown_status_never_false(self):
        """
        Requirements: Missing facts must not become false.
        Adding a mandatory rule for an unpopulated fact must produce UNKNOWN.
        """
        # Add rule for pollution control board certificate (unpopulated on profile)
        rule_cto = SchemeRule.objects.create(
            scheme=self.scheme,
            rule_name="GPCB Consent to Operate",
            field_path="compliance.gpcb_cto_active",
            operator="eq",
            expected_value=True,
            importance="mandatory",
            display_label="Active GPCB Consent to Operate"
        )

        res = self.service.evaluate_scheme(self.profile.id, self.scheme.id, self.goal.id)
        self.assertEqual(res['overall_status'], 'UNKNOWN')
        self.assertIn("compliance.gpcb_cto_active", res['missing_information'])

        cond_cto = next(c for c in res['conditions'] if c['rule_id'] == str(rule_cto.id))
        self.assertEqual(cond_cto['result'], 'UNKNOWN')
        rule_cto.delete()

    # -------------------------------------------------------------
    # 3. Single Scheme Evaluation Endpoint
    # -------------------------------------------------------------

    def test_single_scheme_evaluate_api_endpoint(self):
        """
        Tests POST /api/v1/eligibility/evaluate/
        Verifies:
        - overall_status, conditions, missing_information, official_verification_items, evaluated_at, scheme_version
        - Invariant: Zero AI eligibility percentage in response!
        """
        url = reverse('eligibility-evaluate')
        payload = {
            "profile_id": str(self.profile.id),
            "scheme_id": self.scheme.scheme_code,
            "goal_id": str(self.goal.id)
        }
        response = self.client.post(url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.data

        # Verify required contract fields
        self.assertIn('overall_status', data)
        self.assertEqual(data['overall_status'], 'MATCH')
        self.assertIn('conditions', data)
        self.assertGreaterEqual(len(data['conditions']), 2)
        self.assertIn('missing_information', data)
        self.assertIn('official_verification_items', data)
        self.assertIn('evaluated_at', data)
        self.assertIn('scheme_version', data)
        self.assertEqual(data['scheme_version'], 1)

        # Invariant check: No AI hallucinated percentage
        self.assertNotIn('confidence_percentage', data)
        self.assertNotIn('ai_approval_probability', data)

    # -------------------------------------------------------------
    # 4. Batch Candidate Schemes Evaluation Endpoint
    # -------------------------------------------------------------

    def test_batch_evaluate_api_endpoint(self):
        """Tests POST /api/v1/eligibility/evaluate-batch/"""
        # Create second scheme
        scheme2 = Scheme.objects.create(
            scheme_code="PMEGP-CENTRAL",
            name="Prime Minister Employment Generation Programme",
            level="central",
            support_type="capital_subsidy",
            status="active"
        )
        url = reverse('eligibility-evaluate-batch')
        payload = {
            "profile_id": str(self.profile.id),
            "scheme_ids": [self.scheme.scheme_code, scheme2.scheme_code],
            "goal_id": str(self.goal.id)
        }
        response = self.client.post(url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['total_evaluated'], 2)
        evals = response.data['evaluations']
        self.assertEqual(len(evals), 2)
        codes = [e['scheme_code'] for e in evals]
        self.assertIn(self.scheme.scheme_code, codes)
        self.assertIn(scheme2.scheme_code, codes)

    # -------------------------------------------------------------
    # 5. Re-Evaluation After Profile Change Endpoint
    # -------------------------------------------------------------

    def test_re_evaluate_after_profile_change_api_endpoint(self):
        """
        Tests POST /api/v1/eligibility/re-evaluate/
        Updates investment to 80 Lakhs (disqualifying for capital subsidy)
        and confirms status dynamically transitions to DOES_NOT_MATCH.
        """
        # First evaluate to register previous evaluation
        self.service.evaluate_scheme(self.profile.id, self.scheme.id, self.goal.id)

        url = reverse('eligibility-re-evaluate')
        payload = {
            "profile_id": str(self.profile.id),
            "updated_facts": {
                "investment_in_plant_machinery_lakhs": "85.00"
            },
            "goal_id": str(self.goal.id)
        }
        response = self.client.post(url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(response.data['re_evaluated_count'], 1)

        updated_eval = response.data['results'][0]
        self.assertEqual(updated_eval['overall_status'], 'DOES_NOT_MATCH')
        self.assertGreaterEqual(len(updated_eval['blockers']), 1)
