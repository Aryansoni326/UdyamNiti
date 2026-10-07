"""
Unit and Integration Tests for Personalized Policy Impact Pipeline.
Verifies:
1. Candidate profile filtering using indexed fact filters.
2. Re-evaluation of deterministic eligibility only for affected schemes/profiles.
3. Before vs after status transition detection (e.g. DOES_NOT_MATCH -> MATCH / POTENTIAL_MATCH).
4. Prompt example: threshold relaxed from 5 Cr to 10 Cr, business turnover 7 Cr.
5. User-facing explanation with official evidence and zero false guarantees.
6. Demo simulation mode.
7. REST API endpoints.
"""
from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status

from apps.business_profiles.models import BusinessProfile, BusinessGoal
from apps.policies.models import Scheme, SchemeRule
from apps.eligibility.models import EligibilityEvaluation
from apps.policy_monitoring.models import (
    PolicyChange,
    ImpactEvaluation,
    ChangeType,
    ReviewStatus
)
from apps.policy_monitoring.impact_service import PersonalizedImpactService


class PersonalizedImpactPipelineTests(TestCase):
    def setUp(self):
        # 1. Scheme Setup
        self.scheme = Scheme.objects.create(
            scheme_code="GJ-CAPITAL-2025",
            name="Gujarat MSME Capital Subsidy Scheme",
            level="state_gujarat",
            support_type="capital_subsidy",
            max_benefit_amount_lakhs=35.0,
            status="active",
            target_states=["Gujarat"]
        )

        # Active Scheme Rule: Turnover <= 1000.0 Lakhs (Relaxed threshold)
        self.rule = SchemeRule.objects.create(
            scheme=self.scheme,
            rule_name="Turnover Ceiling Rule",
            field_path="annual_turnover_lakhs",
            operator="lte",
            expected_value=1000.0,  # ₹10 Cr
            importance="mandatory",
            source_clause="Clause 4.1 Turnover Cap",
            is_active=True
        )

        # 2. Stored Business Profile (Turnover ₹7 Cr = 700 Lakhs)
        self.profile = BusinessProfile.objects.create(
            business_name="Apex Precision Tools Pvt Ltd",
            entity_type="private_limited",
            msme_category="small",
            industry_sector="Manufacturing",
            state="Gujarat",
            district="Ahmedabad",
            investment_in_plant_machinery_lakhs=45.0,
            annual_turnover_lakhs=700.0,  # ₹7 Cr
            udyam_registration_number="UDYAM-GJ-01-0099881",
            is_npa=False
        )

        # Profile in Maharashtra (should be filtered out by state filter)
        self.mh_profile = BusinessProfile.objects.create(
            business_name="Bombay Engineering Works",
            msme_category="small",
            state="Maharashtra",
            annual_turnover_lakhs=700.0
        )

        # 3. Policy Change: Threshold revised from 500L (5 Cr) to 1000L (10 Cr)
        self.policy_change = PolicyChange.objects.create(
            scheme=self.scheme,
            change_type=ChangeType.THRESHOLDS,
            change_summary="Turnover threshold relaxed from ₹5 Cr to ₹10 Cr",
            old_value={"expected_value": 500.0},
            new_value={"expected_value": 1000.0},
            affected_rule_ids=["rule_turnover_cap"],
            evidence_source="Gujarat Gazette Notification No. SSI/102020/MSME-Incentive/W, Clause 4.1",
            requires_human_review=False,
            review_status=ReviewStatus.APPROVED_ACTIVE
        )

        # 4. Historical Evaluation before change (was DOES_NOT_MATCH because turnover 700L > 500L)
        self.prev_eval = EligibilityEvaluation.objects.create(
            business_profile=self.profile,
            scheme=self.scheme,
            overall_status="DOES_NOT_MATCH",
            score=0.0,
            mandatory_failures=["Turnover exceeds ₹5 Cr ceiling."]
        )

    def test_candidate_filtering(self):
        """Indexed filters must include Gujarat profile and exclude Maharashtra profile."""
        candidates = PersonalizedImpactService.filter_candidate_profiles(self.policy_change)
        candidate_ids = [p.id for p in candidates]
        self.assertIn(self.profile.id, candidate_ids)
        self.assertNotIn(self.mh_profile.id, candidate_ids)

    def test_process_policy_change_impact_transition_detection(self):
        """Pipeline must detect DOES_NOT_MATCH -> MATCH transition for 7 Cr turnover business."""
        impacts = PersonalizedImpactService.process_policy_change_impact(self.policy_change, persist=True)

        self.assertEqual(len(impacts), 1)
        impact = impacts[0]

        # Check before/after comparison
        self.assertEqual(impact.business_profile.id, self.profile.id)
        self.assertEqual(impact.previous_status, "DOES_NOT_MATCH")
        self.assertEqual(impact.new_status, "MATCH")
        self.assertEqual(impact.impact_type, "unlocked_new_match")
        self.assertEqual(impact.status_transition, "DOES_NOT_MATCH -> MATCH")

        # Invariant: Never claim a new benefit is guaranteed
        self.assertNotIn("guaranteed", impact.user_facing_explanation.lower())
        self.assertIn("subject to formal application", impact.user_facing_explanation.lower())
        self.assertIn("Clause 4.1", impact.user_facing_explanation)

        # Check DB persistence
        self.assertTrue(self.policy_change.processed)
        saved = ImpactEvaluation.objects.filter(policy_change=self.policy_change).first()
        self.assertIsNotNone(saved)
        self.assertEqual(saved.status_transition, "DOES_NOT_MATCH -> MATCH")

    def test_simulate_demo_impact(self):
        """simulate_demo_impact evaluates impact in memory without permanent DB persistence."""
        simulated_change = {
            "change_type": "thresholds",
            "change_summary": "Simulated relaxation of turnover cap to 10 Cr",
            "old_value": {"expected_value": 500.0},
            "new_value": {"expected_value": 1000.0},
            "affected_rule_ids": ["turnover_cap"],
            "evidence_source": "Budget Announcement 2026"
        }

        # Initial count of ImpactEvaluation
        init_count = ImpactEvaluation.objects.count()

        res = PersonalizedImpactService.simulate_demo_impact(
            scheme_code="GJ-CAPITAL-2025",
            simulated_change=simulated_change
        )

        # Verify response structure
        self.assertEqual(res["scheme_code"], "GJ-CAPITAL-2025")
        self.assertTrue(res["total_profiles_analyzed"] > 0)
        self.assertEqual(res["affected_profiles"][0]["status_transition"], "DOES_NOT_MATCH -> MATCH")

        # Invariant: Dry run should NOT create permanent DB records
        self.assertEqual(ImpactEvaluation.objects.count(), init_count)


class PersonalizedImpactAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()

        self.scheme = Scheme.objects.create(
            scheme_code="GJ-CAPITAL-2025",
            name="Gujarat MSME Capital Subsidy",
            level="state_gujarat",
            support_type="capital_subsidy"
        )
        self.profile = BusinessProfile.objects.create(
            business_name="Krishna Engineering Works",
            msme_category="small",
            state="Gujarat",
            annual_turnover_lakhs=700.0
        )
        self.policy_change = PolicyChange.objects.create(
            scheme=self.scheme,
            change_type=ChangeType.THRESHOLDS,
            change_summary="Turnover limit relaxed to 10 Cr",
            old_value={"expected_value": 500.0},
            new_value={"expected_value": 1000.0},
            evidence_source="Gazette 2025",
            review_status=ReviewStatus.APPROVED_ACTIVE
        )

    def test_api_evaluate_impact(self):
        """POST /api/v1/policy-monitoring/impact/evaluate/ runs re-evaluation."""
        payload = {"policy_change_id": str(self.policy_change.id)}
        res = self.client.post('/api/v1/policy-monitoring/impact/evaluate/', payload, format='json')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn("total_impacted_profiles", res.data)

    def test_api_profile_impact_list(self):
        """GET /api/v1/policy-monitoring/impact/profile/<id>/ returns impact list."""
        ImpactEvaluation.objects.create(
            policy_change=self.policy_change,
            business_profile=self.profile,
            impact_type="unlocked_new_match",
            status_transition="DOES_NOT_MATCH -> MATCH",
            user_facing_explanation="Notice: Eligible for subsidy."
        )

        res = self.client.get(f'/api/v1/policy-monitoring/impact/profile/{self.profile.id}/')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["count"], 1)
        self.assertEqual(res.data["impact_notices"][0]["status_transition"], "DOES_NOT_MATCH -> MATCH")

    def test_api_demo_simulate(self):
        """POST /api/v1/policy-monitoring/impact/demo-simulate/ returns dry-run diff."""
        payload = {
            "scheme_code": "GJ-CAPITAL-2025",
            "simulated_change": {
                "change_type": "thresholds",
                "old_value": {"expected_value": 500.0},
                "new_value": {"expected_value": 1000.0}
            }
        }
        res = self.client.post('/api/v1/policy-monitoring/impact/demo-simulate/', payload, format='json')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn("affected_profiles", res.data)
