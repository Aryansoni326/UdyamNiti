"""
Unit and Integration Tests for Action Plan Engine and Service.
Verifies:
1. Actionable task generation across categories: prerequisite, documentation, verification, certification, relationship_review, portal_submission.
2. Complete schema compliance: id, title, rationale, category, priority, dependency_ids, related_scheme_ids, evidence_ids, completion_status, external_url, requires_user_action.
3. Invariant: No fabricated deadlines unless present in official data.
4. Invariant: Never automatically submits applications (requires_user_action=True).
5. Dependency-aware topological ordering.
6. Service and API state machine: dependency validation on complete and task reopening.
"""
from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status

from apps.business_profiles.models import BusinessProfile, BusinessGoal
from apps.policies.models import Scheme
from apps.strategy.models import Strategy
from apps.actions.models import ActionTask, TaskCategory, CompletionStatus
from apps.actions.engine import ActionPlanEngine, ActionTaskData
from apps.actions.services import ActionPlanService


class ActionPlanEngineTests(TestCase):
    def setUp(self):
        self.engine = ActionPlanEngine()

    def test_generate_plan_full_spectrum_of_actionable_tasks(self):
        """Engine must generate tasks across documentation, verification, certification, relationship review, and portal submission."""
        goal = {
            "primary_goal": "Procure CNC machinery",
            "investment_amount_lakhs": 50.0
        }
        business_facts = {
            "business_name": "Patel Precision Lathes",
            "has_udyam": False,
            "has_zed_certification": False,
            "industry_sector": "Manufacturing"
        }
        selected_opportunities = [
            {
                "scheme_code": "GJ-CAPITAL-2025",
                "name": "Gujarat MSME Capital Subsidy",
                "official_portal_url": "https://ifp.gujarat.gov.in",
                "status": "MATCH",
                "max_benefit_lakhs": 25.0
            },
            {
                "scheme_code": "GJ-INTEREST-2025",
                "name": "Gujarat MSME Interest Subsidy",
                "status": "MATCH",
                "max_benefit_lakhs": 15.0
            }
        ]
        unknowns = [
            {
                "fact_key": "location.taluka_category",
                "question": "Which Taluka is your factory situated in?",
                "impact": "Determines subsidy ceiling"
            }
        ]

        tasks: list[ActionTaskData] = self.engine.generate_plan(
            goal=goal,
            business_facts=business_facts,
            selected_opportunities=selected_opportunities,
            unknowns=unknowns
        )

        categories = {t.category for t in tasks}
        self.assertIn(TaskCategory.PREREQUISITE, categories)
        self.assertIn(TaskCategory.DOCUMENTATION, categories)
        self.assertIn(TaskCategory.VERIFICATION, categories)
        self.assertIn(TaskCategory.CERTIFICATION, categories)
        self.assertIn(TaskCategory.RELATIONSHIP_REVIEW, categories)
        self.assertIn(TaskCategory.PORTAL_SUBMISSION, categories)

        # Check required fields
        for t in tasks:
            self.assertTrue(len(t.id) > 0)
            self.assertTrue(len(t.title) > 0)
            self.assertTrue(len(t.rationale) > 0)
            self.assertIsInstance(t.dependency_ids, list)
            self.assertIsInstance(t.related_scheme_ids, list)
            self.assertIsInstance(t.evidence_ids, list)
            self.assertEqual(t.completion_status, CompletionStatus.PENDING)
            self.assertTrue(t.requires_user_action)  # Invariant: never auto-submit

        # Check official statutory deadline invariant: non-fabricated
        portal_tasks = [t for t in tasks if t.category == TaskCategory.PORTAL_SUBMISSION]
        self.assertTrue(len(portal_tasks) > 0)
        # Gujarat Capital Subsidy has statutory 1-year DOCP deadline
        cap_portal_task = next(t for t in portal_tasks if "Capital" in t.title)
        self.assertEqual(cap_portal_task.official_deadline, "Within 1 year from Date of Commercial Production (DOCP)")

    def test_dependency_aware_topological_ordering(self):
        """Prerequisite tasks (Udyam, DPR) must appear strictly before dependent portal submission tasks."""
        goal = {"investment_amount_lakhs": 40.0}
        business_facts = {"has_udyam": False, "has_zed_certification": True}
        selected_opportunities = [
            {"scheme_code": "GJ-CAPITAL-2025", "status": "MATCH", "official_portal_url": "https://ifp.gujarat.gov.in"}
        ]

        tasks = self.engine.generate_plan(
            goal=goal,
            business_facts=business_facts,
            selected_opportunities=selected_opportunities
        )

        # Udyam prerequisite must be priority 1
        udyam_task = next(t for t in tasks if t.category == TaskCategory.PREREQUISITE)
        self.assertEqual(udyam_task.priority, 1)

        # Portal submission must depend on DPR / Udyam and have higher priority number (run later)
        portal_task = next(t for t in tasks if t.category == TaskCategory.PORTAL_SUBMISSION)
        self.assertTrue(portal_task.priority > udyam_task.priority)
        self.assertIn(udyam_task.id, portal_task.dependency_ids)


class ActionPlanServiceAndAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()

        self.profile = BusinessProfile.objects.create(
            business_name="Krishna CNC Tech",
            msme_category="small",
            state="Gujarat"
        )
        self.goal = BusinessGoal.objects.create(
            business_profile=self.profile,
            raw_goal_text="Procure multi-axis lathe"
        )
        self.strategy = Strategy.objects.create(
            goal=self.goal,
            business_profile=self.profile,
            narrative="Roadmap"
        )

    def test_service_generates_and_persists_tasks(self):
        """ActionPlanService persists tasks and respects dependency validation on completion."""
        evaluations_data = [
            {"scheme_code": "GJ-CAPITAL-2025", "status": "MATCH", "official_portal_url": "https://ifp.gujarat.gov.in"}
        ]

        tasks = ActionPlanService.generate_tasks_for_strategy(
            strategy=self.strategy,
            evaluations_data=evaluations_data
        )

        self.assertTrue(len(tasks) >= 2)

        # Find a dependent task and its prerequisite
        dependent_task = next(t for t in tasks if len(t.dependency_ids) > 0)
        prereq_id = dependent_task.dependency_ids[0]

        # Attempting to complete dependent task before prerequisite must fail
        with self.assertRaises(ValueError):
            ActionPlanService.complete_task(task_id=str(dependent_task.id), force=False)

        # Complete prerequisite first
        ActionPlanService.complete_task(task_id=prereq_id)
        prereq_task = ActionTask.objects.get(id=prereq_id)
        self.assertEqual(prereq_task.status, CompletionStatus.COMPLETED)

        # Now completing dependent task should succeed
        ActionPlanService.complete_task(task_id=str(dependent_task.id))
        dependent_task.refresh_from_db()
        self.assertEqual(dependent_task.status, CompletionStatus.COMPLETED)

    def test_api_complete_and_reopen_endpoints(self):
        """API endpoints to complete (with dependency validation) and reopen tasks."""
        # Create prerequisite task
        t1 = ActionTask.objects.create(
            strategy=self.strategy,
            business_profile=self.profile,
            priority=1,
            title="Complete Udyam Registration",
            rationale="Statutory gateway",
            status=CompletionStatus.PENDING
        )
        # Create dependent task
        t2 = ActionTask.objects.create(
            strategy=self.strategy,
            business_profile=self.profile,
            priority=2,
            title="Submit IFP Portal Application",
            rationale="State filing",
            dependency_ids=[str(t1.id)],
            status=CompletionStatus.PENDING
        )

        # 1. Completing t2 directly must return 400 with dependency error
        res_fail = self.client.post(f'/api/v1/actions/{t2.id}/complete/')
        self.assertEqual(res_fail.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("prerequisite tasks must be completed first", res_fail.data['error'])

        # 2. Complete t1
        res_t1 = self.client.post(f'/api/v1/actions/{t1.id}/complete/')
        self.assertEqual(res_t1.status_code, status.HTTP_200_OK)
        self.assertEqual(res_t1.data['status'], 'completed')

        # 3. Complete t2 now succeeds
        res_t2 = self.client.post(f'/api/v1/actions/{t2.id}/complete/')
        self.assertEqual(res_t2.status_code, status.HTTP_200_OK)
        self.assertEqual(res_t2.data['status'], 'completed')

        # 4. Reopen t2
        res_reopen = self.client.post(f'/api/v1/actions/{t2.id}/reopen/')
        self.assertEqual(res_reopen.status_code, status.HTTP_200_OK)
        self.assertEqual(res_reopen.data['status'], 'pending')
        self.assertIsNone(res_reopen.data['completed_at'])

    def test_api_generate_plan_endpoint(self):
        """POST /api/v1/actions/generate/ generates dependency-aware action tasks."""
        payload = {
            "goal": {"investment_amount_lakhs": 50.0},
            "business_facts": {"has_udyam": True},
            "selected_opportunities": [
                {"scheme_code": "GJ-CAPITAL-2025", "status": "MATCH"}
            ]
        }
        res = self.client.post('/api/v1/actions/generate/', payload, format='json')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertTrue(len(res.data) > 0)
        self.assertIn("dependency_ids", res.data[0])
        self.assertIn("rationale", res.data[0])
