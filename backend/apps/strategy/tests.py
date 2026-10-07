"""
Unit tests for the Strategy Orchestrator, Action Plan Service, and Opportunity Unlock Engine.
"""
from django.test import TestCase
from apps.business_profiles.models import BusinessProfile, BusinessGoal
from apps.policies.models import Scheme, SchemeRule
from apps.strategy.models import Strategy
from apps.strategy.services import StrategyOrchestrator
from apps.actions.models import ActionTask
from apps.opportunities.models import OpportunityUnlock


class StrategyOrchestratorTestCase(TestCase):
    def setUp(self):
        self.profile = BusinessProfile.objects.create(
            business_name="Test Engineering Works",
            msme_category="small",
            entity_type="proprietorship",
            industry_sector="Manufacturing",
            state="Gujarat",
            district="Ahmedabad",
            investment_in_plant_machinery_lakhs=50.0,
            annual_turnover_lakhs=150.0,
            is_women_owned=False,
            is_sc_st_owned=False,
            is_npa=False,
            has_bank_account=True,
            has_existing_loan=False,
        )

        self.scheme = Scheme.objects.create(
            scheme_code="GJ_MSME_TEST",
            name="Gujarat MSME Capital Subsidy",
            ministry_department="Govt of Gujarat",
            level="state_gujarat",
            support_type="capital_subsidy",
            max_benefit_amount_lakhs=12.5,
            benefit_description="25% capital subsidy",
            description="Manufacturing subsidy",
            status="active",
            target_msme_categories=["small", "micro"],
            target_states=["Gujarat"]
        )

        self.goal = BusinessGoal.objects.create(
            business_profile=self.profile,
            raw_goal_text="I want to purchase a ₹50 lakh CNC machine to expand production",
            status="pending"
        )

    def test_end_to_end_orchestration(self):
        """Orchestrator should process goal, evaluate schemes, generate narrative, actions, and unlocks."""
        orchestrator = StrategyOrchestrator()
        result = orchestrator.analyze(self.goal, self.profile)

        self.assertIsNotNone(result.get('strategy_id'))
        strategy = Strategy.objects.get(pk=result['strategy_id'])

        # Verify strategy attributes
        self.assertEqual(strategy.business_profile.id, self.profile.id)
        self.assertTrue(len(strategy.narrative) > 0)
        self.assertTrue(strategy.total_opportunities > 0)

        # Verify Action Tasks were generated
        tasks = ActionTask.objects.filter(strategy=strategy)
        self.assertTrue(tasks.count() > 0)

        # Verify Opportunity Unlocks were synthesized
        unlocks = OpportunityUnlock.objects.filter(strategy=strategy)
        self.assertTrue(unlocks.count() > 0)
