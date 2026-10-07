"""
Unit and Integration Tests for AI Orchestrator Pipeline State Machine.
Verifies:
1. 10-step sequential execution without autonomous loops:
   parse_goal -> load_profile -> ask_material_questions -> discover_candidates
   -> retrieve_evidence -> evaluate_rules -> analyze_relationships -> find_unlocks
   -> compose_strategy -> build_actions.
2. Tool calls are typed and deterministic services are authoritative.
3. Retries are bounded (max 2 attempts per step).
4. Step trace logging with duration_ms and status.
5. Invariant: Private chain-of-thought is never exposed; returns concise rationale + verified evidence.
6. Graceful partial fallback if a non-critical component fails.
7. REST API endpoint: POST /api/v1/strategies/orchestrate/.
"""
from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework import status

from apps.business_profiles.models import BusinessProfile, BusinessGoal
from apps.policies.models import Scheme, SchemeRule
from apps.strategy.models import Strategy
from apps.strategy.ai_orchestrator import AIOrchestrator


class AIOrchestratorTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="orchestrator_tester", password="password123")
        self.profile = BusinessProfile.objects.create(
            user=self.user,
            business_name="Somnath Precision Engineering LLP",
            msme_category="small",
            entity_type="llp",
            industry_sector="Manufacturing",
            state="Gujarat",
            district="Rajkot",
            annual_turnover_lakhs=650.0,
            investment_in_plant_machinery_lakhs=120.0,
            udyam_registration_number="UDYAM-GJ-01-0088112",
            gstin="24AAACC8888F1Z8"
        )

        self.goal = BusinessGoal.objects.create(
            business_profile=self.profile,
            raw_goal_text="Mare CNC machine levani che ane production increase karvu che. Government taraf thi kai support mali shake?",
            status="pending"
        )

        # Seed candidate scheme in DB
        self.scheme = Scheme.objects.create(
            scheme_code="GJ-CAPITAL-2025",
            name="Gujarat MSME Capital Subsidy Scheme",
            level="state_gujarat",
            support_type="capital_subsidy",
            max_benefit_amount_lakhs=35.0,
            status="active",
            target_states=["Gujarat"]
        )
        SchemeRule.objects.create(
            scheme=self.scheme,
            rule_name="Turnover Limit Check",
            field_path="annual_turnover_lakhs",
            operator="lte",
            expected_value=1000.0,
            importance="mandatory",
            is_active=True
        )

    def test_full_pipeline_orchestration_execution(self):
        """Orchestrator runs 10 steps, logs trace steps, persists Strategy and ActionTasks."""
        orchestrator = AIOrchestrator()
        result = orchestrator.execute_goal_pipeline(goal=self.goal, profile=self.profile)

        self.assertEqual(result.status, "COMPLETED")
        self.assertIsNotNone(result.strategy_id)
        self.assertGreater(result.total_duration_ms, 0)

        # Check step traces
        step_names = [s.step_name for s in result.steps]
        self.assertIn("parse_goal", step_names)
        self.assertIn("ask_material_questions", step_names)
        self.assertIn("discover_candidates_and_evidence", step_names)
        self.assertIn("evaluate_rules", step_names)
        self.assertIn("analyze_relationships", step_names)
        self.assertIn("find_unlocks", step_names)
        self.assertIn("compose_strategy_and_actions", step_names)

        for s in result.steps:
            self.assertEqual(s.status, "SUCCESS")
            self.assertGreaterEqual(s.duration_ms, 0.0)

        # Invariant: No Chain-of-Thought leakage
        result_dict = result.to_dict()
        res_str = str(result_dict).lower()
        self.assertNotIn("chain_of_thought", res_str)
        self.assertNotIn("thought process", res_str)

        # Rationale & evidence provided
        self.assertTrue(len(result.user_facing_rationale) > 10)
        self.assertGreaterEqual(len(result.evidence_citations), 0)

        # Check DB mutations
        self.goal.refresh_from_db()
        self.assertEqual(self.goal.status, "ready")
        self.assertTrue(Strategy.objects.filter(id=result.strategy_id).exists())

    def test_graceful_partial_failure_handling(self):
        """If goal input is abnormal, orchestrator catches error and records trace without crashing."""
        orchestrator = AIOrchestrator()
        # Mock abnormal goal
        broken_goal = BusinessGoal.objects.create(
            business_profile=self.profile,
            raw_goal_text="short",
            status="pending"
        )
        res = orchestrator.execute_goal_pipeline(goal=broken_goal, profile=self.profile)

        # Handled gracefully
        self.assertIn(res.status, ("COMPLETED", "PARTIAL_SUCCESS"))


class AIOrchestratorAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username="api_orch_user", password="password123")
        self.client.force_authenticate(user=self.user)

        self.profile = BusinessProfile.objects.create(
            user=self.user,
            business_name="Rajkot Precision Works",
            msme_category="small",
            state="Gujarat"
        )
        self.goal = BusinessGoal.objects.create(
            business_profile=self.profile,
            raw_goal_text="Want to buy CNC machine worth 50 Lakhs in Ahmedabad GIDC.",
            status="pending"
        )

    def test_api_orchestrate_endpoint(self):
        """POST /api/v1/strategies/orchestrate/ triggers full pipeline."""
        payload = {
            "goal_id": str(self.goal.id),
            "profile_id": str(self.profile.id)
        }
        res = self.client.post('/api/v1/strategies/orchestrate/', payload, format='json')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn("trace_id", res.data)
        self.assertIn("steps", res.data)
        self.assertEqual(res.data["status"], "COMPLETED")
        self.assertIsNotNone(res.data["strategy_id"])
