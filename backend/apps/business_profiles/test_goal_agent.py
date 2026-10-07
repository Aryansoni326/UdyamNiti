"""
Unit & Integration Tests for Goal Understanding Agent.
Validates:
1. Free-form Gujarati / Gujlish transliterated input interpretation.
2. English input with money normalization (separate amount, unit, and normalized INR).
3. Invariant: Ask ONLY questions likely to materially change discovery/eligibility.
4. Invariant: NEVER invent business facts not present in user statement.
5. Invariant: NO scheme recommendations at this stage.
6. API endpoint integration (/api/v1/goals/interpret/).
"""
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status

from apps.business_profiles.goal_agent import GoalUnderstandingAgent
from apps.business_profiles.models import BusinessProfile


class GoalUnderstandingAgentTestCase(TestCase):
    def setUp(self):
        self.agent = GoalUnderstandingAgent()
        self.client = APIClient()

    def test_gujarati_transliterated_input(self):
        """
        Tests the prompt's exact sample input:
        “Mare CNC machine levani che ane production increase karvu che. Government taraf thi kai support mali shake?”
        """
        guj_input = "Mare CNC machine levani che ane production increase karvu che. Government taraf thi kai support mali shake?"
        res = self.agent.interpret_goal(guj_input)

        # 1. Linguistic Detection
        self.assertEqual(res.detected_language, "Gujarati (Transliterated)")

        # 2. Project & Objectives Extraction
        self.assertIn("CNC", res.project.upper())
        self.assertIn("capital_subsidy", res.support_categories)

        # 3. Invariant: Never invent facts (User did NOT state investment amount or taluka)
        self.assertIsNone(res.estimated_investment.amount)
        self.assertIn("location.taluka_category", res.missing_material_facts)

        # 4. Clarifying questions: Asks targeted questions with selectable options
        self.assertGreaterEqual(len(res.clarifying_questions), 2)
        for q in res.clarifying_questions:
            self.assertTrue(len(q.question) > 10)
            self.assertTrue(len(q.reason_it_matters) > 10)
            self.assertGreaterEqual(len(q.options), 2)

        # 5. Invariant: Strictly NO scheme recommendations at this stage
        output_str = str(res.to_dict()).lower()
        self.assertNotIn("pmegp", output_str)
        self.assertNotIn("cgtmse", output_str)
        self.assertNotIn("clcss", output_str)

    def test_english_detailed_input_with_money_normalization(self):
        """
        Tests money normalization:
        'Rs. 50 Lakhs' -> amount: 50.0, unit: 'Lakhs', normalized_inr: 5000000.0, raw_text: 'Rs. 50 Lakhs'
        """
        eng_input = "I want to purchase a new 5-axis CNC machine for Rs. 50 Lakhs to expand my precision engineering factory in Rajkot."
        res = self.agent.interpret_goal(eng_input)

        self.assertEqual(res.detected_language, "English")

        # Money Normalization
        inv = res.estimated_investment
        self.assertEqual(inv.amount, 50.0)
        self.assertEqual(inv.unit, "Lakhs")
        self.assertEqual(inv.normalized_inr, 5000000.0)
        self.assertIn("50", inv.raw_text)

        # Sector & Categories
        self.assertIn("Engineering", res.industry_hint)
        self.assertIn("capital_subsidy", res.support_categories)
        self.assertIn("interest_subvention", res.support_categories)

        # Known Facts
        fact_keys = [f.fact_key for f in res.known_facts]
        self.assertIn("equipment.type", fact_keys)
        self.assertIn("financials.estimated_investment_inr", fact_keys)

        # Zero scheme recommendations
        for cat in res.support_categories:
            self.assertNotIn("scheme", cat)

    def test_crore_money_normalization(self):
        """Tests '1.5 Crore' normalization."""
        text = "We are setting up a food processing cold chain unit with an investment of 1.5 Crore in Banaskantha."
        res = self.agent.interpret_goal(text)

        inv = res.estimated_investment
        self.assertEqual(inv.amount, 1.5)
        self.assertEqual(inv.unit, "Crores")
        self.assertEqual(inv.normalized_inr, 15000000.0)
        self.assertIn("Food", res.industry_hint)

    def test_missing_material_facts_and_clarifying_questions(self):
        """
        Verifies that questions asked are limited to high-impact variables
        (e.g., location/taluka category and Udyam registration).
        """
        text = "I want to buy solar panels for my factory."
        res = self.agent.interpret_goal(text)

        self.assertIn("power_tariff_subsidy", res.support_categories)
        question_keys = [q.fact_key for q in res.clarifying_questions]
        # Should ask for taluka category or investment
        self.assertTrue(any("location" in k or "investment" in k for k in question_keys))

    def test_api_endpoint_goal_interpret(self):
        """Tests POST /api/v1/goals/interpret/ REST endpoint."""
        url = reverse('goal-interpret')
        payload = {
            "goal_text": "Mare CNC machine levani che ane production increase karvu che."
        }
        response = self.client.post(url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.data
        self.assertIn('primary_goal', data)
        self.assertIn('project', data)
        self.assertIn('estimated_investment', data)
        self.assertIn('industry_hint', data)
        self.assertIn('business_objectives', data)
        self.assertIn('support_categories', data)
        self.assertIn('known_facts', data)
        self.assertIn('missing_material_facts', data)
        self.assertIn('clarifying_questions', data)
        self.assertIn('detected_language', data)
        self.assertEqual(data['detected_language'], "Gujarati (Transliterated)")
