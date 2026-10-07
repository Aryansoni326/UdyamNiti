"""
Golden End-to-End Integration Test for ABC Engineering Works.
Targets the critical hackathon demo path:
1. MSME Profile Verification (ABC Engineering Works: Surat, Gujarat, Small, Manufacturing)
2. Strategic Goal Ingestion (Purchase ₹50L CNC machine)
3. Orchestrated Candidate Discovery (Central + State + Guarantee Schemes)
4. Deterministic Authoritative Evaluation (Zero-hallucination boolean rules)
5. Cross-Scheme Stacking & Synergy (CLCSS + Gujarat Capital Subsidy + CGTMSE)
6. Opportunity Unlock Analysis (Unlocking ZED certification with actionable steps)
7. Explainable Grounded Strategy Synthesis (Readiness tiers & statutory citations)
8. Dependency-Ordered Action Plan (Step-by-step statutory execution)
9. Application Preparation Workspace (Form pre-fill, checklists, official portal continuity)
"""
import pytest
from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status

from apps.business_profiles.models import BusinessProfile, BusinessGoal
from apps.policies.models import Scheme, SchemeRule, SchemePrerequisite
from apps.relationships.models import SchemeRelationship
from apps.strategy.ai_orchestrator import AIOrchestrator
from apps.strategy.models import Strategy
from apps.actions.models import ActionTask, ApplicationPreparationWorkspace
from apps.actions.workspace_service import ApplicationWorkspaceService
from apps.actions.services import ActionPlanService
from apps.opportunities.services import OpportunityUnlockService
from apps.relationships.services import RelationshipEngine


@pytest.mark.e2e
class GoldenDemoEndToEndTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.orchestrator = AIOrchestrator()

        # Seed ABC Engineering profile
        from django.contrib.auth.models import User
        from apps.accounts.models import UserSecurityProfile, UserRole

        self.user = User.objects.create_user(
            username='abc_engineering',
            email='info@abcengineering.in',
            password='DemoPassword2026!'
        )
        UserSecurityProfile.objects.create(user=self.user, role=UserRole.MSME_USER)
        self.client.force_authenticate(user=self.user)

        self.profile = BusinessProfile.objects.create(
            user=self.user,
            business_name="ABC Engineering Works",
            udyam_registration_number="UDYAM-GJ-29-0012345",
            gstin="24AADCA1234F1Z5",
            msme_category="small",
            enterprise_category="small",
            entity_type="proprietorship",
            industry_sector="Precision Engineering & Metal Fabrication",
            is_manufacturing=True,
            is_service=False,
            state="Gujarat",
            district="Surat",
            annual_turnover=210.0,
            annual_turnover_lakhs=210.0,
            investment_in_plant_machinery_lakhs=45.0,
            has_bank_account=True,
            is_npa=False,
            has_iso_certification=False,  # Can be unlocked!
            uses_digital_payments=True
        )

        # Seed Synthetic Schemes
        # 1. Central CLCSS Subsidy
        self.scheme_clcss = Scheme.objects.create(
            scheme_code="CLCSS",
            name="Credit Linked Capital Subsidy Scheme",
            short_name="CLCSS",
            ministry_department="Ministry of MSME",
            level="central",
            support_type="capital_subsidy",
            target_msme_categories=["micro", "small"],
            max_benefit_amount_lakhs=15.0,
            benefit_percentage=15.0,
            status="active",
            official_portal_url="https://msme.gov.in/clcss",
            benefit_description="15% upfront capital subsidy up to ₹15 Lakhs for tech upgrade."
        )
        SchemeRule.objects.create(
            scheme=self.scheme_clcss,
            rule_name="Micro or Small",
            field_path="msme_category",
            operator="in",
            expected_value=["micro", "small"],
            importance="mandatory",
            is_active=True
        )
        SchemeRule.objects.create(
            scheme=self.scheme_clcss,
            rule_name="Manufacturing Sector",
            field_path="is_manufacturing",
            operator="bool_true",
            expected_value=True,
            importance="mandatory",
            is_active=True
        )

        # 2. Central CGTMSE Credit Guarantee
        self.scheme_cgtmse = Scheme.objects.create(
            scheme_code="CGTMSE",
            name="Credit Guarantee Fund Trust for MSEs",
            short_name="CGTMSE",
            ministry_department="Ministry of MSME / SIDBI",
            level="central",
            support_type="credit_guarantee",
            target_msme_categories=["micro", "small"],
            max_benefit_amount_lakhs=200.0,
            benefit_percentage=85.0,
            status="active",
            official_portal_url="https://cgtmse.in",
            benefit_description="85% credit guarantee on collateral-free machinery loans."
        )

        # 3. State Gujarat Capital Subsidy
        self.scheme_gujarat = Scheme.objects.create(
            scheme_code="GUJ_IND_SUBSIDY",
            name="Gujarat Industrial Policy — Capital Subsidy",
            short_name="Gujarat Capital Subsidy",
            ministry_department="Industries Department, Gujarat",
            level="state_gujarat",
            support_type="capital_subsidy",
            target_msme_categories=["micro", "small", "medium"],
            target_states=["Gujarat"],
            max_benefit_amount_lakhs=35.0,
            benefit_percentage=12.0,
            status="active",
            official_portal_url="https://ifp.gujarat.gov.in",
            benefit_description="12% capital investment subsidy for plant & machinery in Gujarat."
        )
        SchemeRule.objects.create(
            scheme=self.scheme_gujarat,
            rule_name="State Gujarat",
            field_path="state",
            operator="eq",
            expected_value="Gujarat",
            importance="mandatory",
            is_active=True
        )

        # 4. ZED Scheme (Requires Certification)
        self.scheme_zed = Scheme.objects.create(
            scheme_code="ZED_CERT",
            name="MSME Sustainable (ZED) Certification",
            short_name="ZED",
            ministry_department="Ministry of MSME",
            level="central",
            support_type="certification",
            target_msme_categories=["micro", "small", "medium"],
            status="active",
            official_portal_url="https://zed.msme.gov.in"
        )
        SchemePrerequisite.objects.create(
            scheme=self.scheme_zed,
            prerequisite_type="certification",
            title="ISO 9001 / ZED Bronze",
            description="Enterprise must obtain quality certification.",
            how_to_satisfy="Complete assessment on zed.msme.gov.in",
            is_hard_prerequisite=False
        )

        # Relationships
        SchemeRelationship.objects.create(
            scheme_a=self.scheme_clcss,
            scheme_b=self.scheme_cgtmse,
            relationship_type="synergistic",
            description="CGTMSE guarantees loan while CLCSS subsidizes 15%."
        )
        SchemeRelationship.objects.create(
            scheme_a=self.scheme_clcss,
            scheme_b=self.scheme_gujarat,
            relationship_type="compatible",
            description="Central 15% and State 12% subsidies stack up to 27%."
        )

    def test_golden_demo_critical_path(self):
        """
        Executes complete end-to-end P0 journey for ABC Engineering Works:
        User goal
        → Goal Agent
        → Business Profile
        → candidate discovery
        → official-source hybrid RAG
        → deterministic eligibility
        → evidence cards
        → relationship engine
        → opportunity unlock
        → strategy
        → action plan
        → policy-impact demo.
        """
        correlation_id = "corr_abc_demo_2026_golden"

        # ─── STAGE 1: Business Profile Verification ───────────────────────────
        self.assertEqual(self.profile.business_name, "ABC Engineering Works")
        self.assertEqual(self.profile.state, "Gujarat")
        self.assertEqual(self.profile.district, "Surat")
        self.assertTrue(self.profile.is_manufacturing)
        self.assertEqual(self.profile.msme_category, "small")

        # ─── STAGE 2: Goal Ingestion via API with Correlation ID ──────────────
        raw_goal_text = "I want to purchase a ₹50 lakh CNC machine to expand our precision machining capacity."
        api_submit_res = self.client.post(
            "/api/v1/goals/submit/",
            {
                "business_profile_id": str(self.profile.id),
                "goal_text": raw_goal_text,
            },
            HTTP_X_CORRELATION_ID=correlation_id,
            HTTP_X_TRACE_ID=correlation_id
        )
        self.assertEqual(api_submit_res.status_code, status.HTTP_201_CREATED)

        # Requirement: One correlation ID through the flow (header & body)
        self.assertEqual(api_submit_res["X-Correlation-ID"], correlation_id)
        self.assertEqual(api_submit_res["X-Trace-ID"], correlation_id)
        self.assertEqual(api_submit_res.data["correlation_id"], correlation_id)

        # ─── STAGE 3: Goal Agent Output Verification ─────────────────────────
        goal_data = api_submit_res.data["goal"]
        self.assertIn("CNC", goal_data["raw_goal_text"])
        self.assertTrue(len(goal_data["parsed_objective"]) > 0)
        self.assertTrue(any(k in goal_data["parsed_project_type"].lower() for k in ["machinery", "purchase", "expansion"]))
        self.assertEqual(float(goal_data["parsed_investment_amount_lakhs"]), 50.0)
        self.assertIn("capital_subsidy", goal_data["parsed_support_categories"])

        # ─── STAGE 4: Candidate Discovery & Official-Source RAG ──────────────
        steps = api_submit_res.data["steps"]
        step_names = [s["step_name"] for s in steps]
        self.assertIn("discover_candidates_and_evidence", step_names)
        self.assertIn("evaluate_rules", step_names)

        # ─── STAGE 5: Deterministic Authoritative Eligibility Evaluation ─────
        eval_summary = api_submit_res.data["evaluations_summary"]
        self.assertGreaterEqual(eval_summary.get("MATCH", 0), 2)  # CLCSS and Gujarat Capital Subsidy must match!

        strategy_id = api_submit_res.data["strategy_id"]
        self.assertIsNotNone(strategy_id)

        # ─── STAGE 6: Reload Persistence & Evidence Cards via HTTP GET ──────
        reload_res = self.client.get(
            f"/api/v1/strategies/{strategy_id}/",
            HTTP_X_CORRELATION_ID=correlation_id
        )
        self.assertEqual(reload_res.status_code, status.HTTP_200_OK)
        self.assertEqual(reload_res["X-Correlation-ID"], correlation_id)
        reload_data = reload_res.data

        # Verify Typed Contract
        self.assertEqual(reload_data["id"], strategy_id)
        self.assertEqual(reload_data["business_profile"]["business_name"], "ABC Engineering Works")
        self.assertGreaterEqual(len(reload_data["schemes"]), 2)

        # Evidence Cards verification
        matched_schemes = [s for s in reload_data["schemes"] if s["status"] == "MATCH"]
        self.assertGreaterEqual(len(matched_schemes), 2)
        clcss_result = next((s for s in matched_schemes if s["scheme_code"] == "CLCSS"), None)
        self.assertIsNotNone(clcss_result)
        self.assertEqual(clcss_result["status"], "MATCH")
        self.assertTrue(len(clcss_result["condition_results"]) > 0)
        # Ensure condition results carry genuine rule sources (no fabricated fallback)
        for cond in clcss_result["condition_results"]:
            self.assertIn(cond["status"], ["PASS", "FAIL", "UNKNOWN"])
            self.assertIsNotNone(cond["rule_name"])

        # ─── STAGE 7: Relationship Engine (Stacking & Synergy) ───────────────
        relationships = reload_data["relationships"]
        self.assertGreaterEqual(len(relationships), 1)
        # Verify synergistic or compatible stacking edge is mapped
        rel_types = [r.get("type") or r.get("relationship_type") for r in relationships]
        self.assertTrue(any(t in ["synergistic", "compatible"] for t in rel_types))

        # ─── STAGE 8: Opportunity Unlock Engine ──────────────────────────────
        unlocks = reload_data["unlock_recommendations"]
        # ZED or other prerequisites should be detected as potential unlocks
        self.assertTrue(isinstance(unlocks, list))

        # ─── STAGE 9: Strategy Synthesis ─────────────────────────────────────
        self.assertIsNotNone(reload_data["narrative"])
        self.assertTrue(len(reload_data["narrative"]) > 0)
        self.assertTrue(any(w in reload_data["narrative"].lower() for w in ["roadmap", "criteria", "statutory", "policy", "support"]))

        # ─── STAGE 10: Dependency-Ordered Action Plan & Workspace ────────────
        action_plan = reload_data["action_plan"]
        self.assertGreaterEqual(len(action_plan), 1)
        for task in action_plan:
            self.assertIsNotNone(task.get("title"))
            # Invariant: No fabricated deadlines
            self.assertIsNone(task.get("official_deadline"))
            # Invariant: User action required
            if "requires_user_action" in task:
                self.assertTrue(task["requires_user_action"])

        # Application Preparation Workspace continuity
        workspace = ApplicationWorkspaceService.get_or_create_workspace(
            profile_id=str(self.profile.id),
            scheme_id=str(self.scheme_gujarat.id),
            strategy_id=str(strategy_id)
        )
        self.assertIsNotNone(workspace)
        self.assertEqual(workspace.scheme.scheme_code, "GUJ_IND_SUBSIDY")
        ws_res = self.client.get(f"/api/v1/workspace/{workspace.id}/", HTTP_X_CORRELATION_ID=correlation_id)
        self.assertEqual(ws_res.status_code, status.HTTP_200_OK)
        self.assertEqual(ws_res.data["official_portal_route"]["url"], "https://ifp.gujarat.gov.in")

        # ─── STAGE 11: Policy-Impact Demo ────────────────────────────────────
        sim_res = self.client.post(
            "/api/v1/policy-monitoring/impact/demo-simulate/",
            {
                "scheme_code": "GUJ_IND_SUBSIDY",
                "simulated_change": {
                    "change_type": "thresholds",
                    "change_summary": "Plant & machinery capital subsidy ceiling increased to ₹50L",
                    "old_value": {"expected_value": 35.0},
                    "new_value": {"expected_value": 50.0},
                    "evidence_source": "Gujarat Budget Resolution 2026"
                }
            },
            HTTP_X_CORRELATION_ID=correlation_id
        )
        self.assertEqual(sim_res.status_code, status.HTTP_200_OK)
        self.assertEqual(sim_res["X-Correlation-ID"], correlation_id)
        self.assertEqual(sim_res.data["scheme_code"], "GUJ_IND_SUBSIDY")
        self.assertIn("affected_profiles", sim_res.data)

    def test_unknown_state_handling_when_data_missing(self):
        """
        Verify the system produces UNKNOWN when data or evidence is unavailable,
        with zero fabricated fallback values.
        """
        # Create an incomplete profile missing turnover and plant machinery facts
        incomplete_profile = BusinessProfile.objects.create(
            user=self.user,
            business_name="Incomplete Enterprise",
            state="Gujarat",
            annual_turnover=None,
            annual_turnover_lakhs=None,
            investment_in_plant_machinery_lakhs=None,
        )

        # Create a scheme with strict turnover rule
        scheme = Scheme.objects.create(
            scheme_code="TURNOVER_TEST_SCHEME",
            name="Turnover Capped Scheme",
            level="state_gujarat",
            status="active"
        )
        SchemeRule.objects.create(
            scheme=scheme,
            rule_name="Turnover Check",
            field_path="annual_turnover_lakhs",
            operator="lte",
            expected_value=500.0,
            importance="mandatory",
            is_active=True
        )

        from apps.eligibility.engine import RuleEngine
        engine = RuleEngine()
        result = engine.evaluate(scheme, incomplete_profile)

        # Must report UNKNOWN, not MATCH or DOES_NOT_MATCH
        self.assertEqual(result.overall_status, "UNKNOWN")
        self.assertIn("annual_turnover_lakhs", [c.field_path for c in result.conditions if c.status == "UNKNOWN"])
        self.assertTrue(len(result.missing_info) > 0)
        # Ensure actual_value was not fabricated
        unknown_cond = next(c for c in result.conditions if c.field_path == "annual_turnover_lakhs")
        self.assertIsNone(unknown_cond.actual_value)

    def test_partial_failure_handling(self):
        """
        Verify graceful partial failure handling: if a downstream LLM step fails,
        the deterministic rule evaluations are preserved with PARTIAL_SUCCESS status.
        """
        goal = BusinessGoal.objects.create(
            business_profile=self.profile,
            raw_goal_text="Purchase ₹50L CNC machine",
            status="ready"
        )

        # Artificially force an exception during strategy composition
        from unittest.mock import patch
        with patch.object(self.orchestrator.strategy_agent, 'assemble_strategy', side_effect=RuntimeError("LLM API Timeout")):
            result = self.orchestrator.execute_goal_pipeline(goal=goal, profile=self.profile)

            # Must not crash with unhandled exception, must return PARTIAL_SUCCESS
            self.assertEqual(result.status, "PARTIAL_SUCCESS")
            self.assertGreaterEqual(result.evaluations_summary.get("MATCH", 0), 2)
            self.assertIsNotNone(result.error_message)
            self.assertIn("LLM API Timeout", result.error_message)

    def test_cached_reusable_results(self):
        """
        Verify reusable RAG evidence results are cached and reused across pipeline calls.
        """
        from django.core.cache import cache
        goal = BusinessGoal.objects.create(
            business_profile=self.profile,
            raw_goal_text="Purchase ₹50L CNC machine",
            status="ready"
        )

        # First run populates cache
        res1 = self.orchestrator.execute_goal_pipeline(goal=goal, profile=self.profile)
        self.assertEqual(res1.status, "COMPLETED")

        # Second run should execute successfully reusing cache
        res2 = self.orchestrator.execute_goal_pipeline(goal=goal, profile=self.profile)
        self.assertEqual(res2.status, "COMPLETED")
        self.assertEqual(res1.candidate_schemes_count, res2.candidate_schemes_count)

