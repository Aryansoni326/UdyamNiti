"""
Unit and Integration Tests for Opportunity Unlock Engine.
Verifies:
1. Changeable prerequisites (registration, certification, documentation) vs hard disqualifiers (statutory ceiling exceeded, greenfield mismatch).
2. Refusal to advise falsifying facts or guaranteeing eligibility.
3. Graph reachability: finding all affected opportunities across prerequisite and relationship edges.
4. Strict schema compliance: unlock_action, current_blocker, affected_opportunities[], evidence_ids, required_user_confirmation, explanation.
5. Service persistence and REST API endpoints.
"""
from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status

from apps.business_profiles.models import BusinessProfile, BusinessGoal
from apps.policies.models import Scheme
from apps.relationships.models import SchemeRelationship, RelationshipType
from apps.strategy.models import Strategy
from apps.opportunities.models import OpportunityUnlock, PrerequisiteType
from apps.opportunities.engine import OpportunityUnlockEngine, UnlockCandidateData
from apps.opportunities.services import OpportunityUnlockService


class OpportunityUnlockEngineTests(TestCase):
    def setUp(self):
        self.engine = OpportunityUnlockEngine()

        self.scheme_gj_cap = Scheme.objects.create(
            scheme_code="GJ-CAPITAL-2025",
            name="Gujarat MSME Capital Subsidy Scheme",
            level="state_gujarat",
            support_type="capital_subsidy",
            max_benefit_amount_lakhs=35.0,
            status="active"
        )
        self.scheme_gj_int = Scheme.objects.create(
            scheme_code="GJ-INTEREST-2025",
            name="Gujarat MSME Interest Subsidy Scheme",
            level="state_gujarat",
            support_type="interest_subvention",
            max_benefit_amount_lakhs=25.0,
            status="active"
        )
        self.scheme_cgtmse = Scheme.objects.create(
            scheme_code="CGTMSE-CENTRAL",
            name="Credit Guarantee Trust for MSMEs",
            level="central",
            support_type="credit_guarantee",
            max_benefit_amount_lakhs=500.0,
            status="active"
        )
        self.scheme_pmegp = Scheme.objects.create(
            scheme_code="PMEGP-CENTRAL",
            name="Prime Minister Employment Generation Programme",
            level="central",
            support_type="capital_subsidy",
            max_benefit_amount_lakhs=25.0,
            status="active"
        )

        # Prerequisite edge: CGTMSE is a prerequisite for downstream scheme
        SchemeRelationship.objects.create(
            scheme_a=self.scheme_cgtmse,
            scheme_b=self.scheme_gj_cap,
            relationship_type=RelationshipType.PREREQUISITE,
            description="CGTMSE loan sanction required prior to state capital subsidy application."
        )

    def test_udyam_registration_unlock_derivation(self):
        """When Udyam is missing, engine generates registration unlock affecting multiple schemes."""
        business_facts = {
            "business_name": "Maruti Precision Lathes",
            "has_udyam": False,
            "udyam_registration_number": None,
            "industry_sector": "Automotive Engineering"
        }
        evaluations = [
            {
                "scheme_code": "GJ-CAPITAL-2025",
                "status": "POTENTIAL_MATCH",
                "condition_results": [
                    {
                        "rule_id": "rule_udyam_active",
                        "display_label": "Valid Udyam Registration Number",
                        "status": "FAIL",
                        "source_clause": "Clause 2.1"
                    }
                ],
                "missing_info": ["Udyam Registration Certificate"]
            }
        ]

        unlocks = self.engine.evaluate_unlocks(
            evaluations=evaluations,
            business_facts=business_facts,
            candidate_schemes=[self.scheme_gj_cap, self.scheme_gj_int]
        )

        # Must generate Udyam registration unlock
        udyam_unlock = next((u for u in unlocks if u.prerequisite_type == PrerequisiteType.REGISTRATION), None)
        self.assertIsNotNone(udyam_unlock)
        self.assertIn("Udyam Registration", udyam_unlock.unlock_action)
        self.assertEqual(udyam_unlock.difficulty, "low")
        self.assertEqual(udyam_unlock.estimated_days, 2)
        self.assertTrue(udyam_unlock.is_resolvable)

        # Check affected opportunities: Udyam is gateway for both Gujarat schemes
        aff_codes = {o.scheme_code for o in udyam_unlock.affected_opportunities}
        self.assertIn("GJ-CAPITAL-2025", aff_codes)
        self.assertIn("GJ-INTEREST-2025", aff_codes)

        # Check output contract guarantees
        self.assertTrue(len(udyam_unlock.evidence_ids) > 0)
        self.assertIn("Upload official Udyam Registration Certificate", udyam_unlock.required_user_confirmation)
        self.assertIn("Final statutory sanction remains subject to departmental verification", udyam_unlock.explanation)

    def test_rejection_of_hard_disqualifiers(self):
        """Engine must NEVER suggest an unlock for hard statutory disqualifications."""
        evaluations = [
            {
                "scheme_code": "PMEGP-CENTRAL",
                "status": "DOES_NOT_MATCH",
                "condition_results": [
                    {
                        "rule_id": "rule_greenfield_only",
                        "display_label": "Greenfield / New Unit Only",
                        "status": "FAIL"
                    }
                ],
                "mandatory_failures": [
                    "greenfield_only_violation: Existing enterprise expanding is strictly ineligible for PMEGP."
                ]
            }
        ]
        business_facts = {
            "has_udyam": True,
            "udyam_registration_number": "UDYAM-GJ-01-0012345",
            "has_zed_certification": True
        }

        unlocks = self.engine.evaluate_unlocks(
            evaluations=evaluations,
            business_facts=business_facts,
            candidate_schemes=[self.scheme_pmegp]
        )

        # PMEGP greenfield failure must NOT generate a bogus unlock advising the unit to falsify status
        pmegp_unlocks = [u for u in unlocks if any(o.scheme_code == "PMEGP-CENTRAL" for o in u.affected_opportunities)]
        self.assertEqual(len(pmegp_unlocks), 0)

    def test_zed_certification_unlock(self):
        """Manufacturing enterprise without ZED receives certification unlock candidate."""
        business_facts = {
            "industry_sector": "Machinery Manufacturing",
            "has_udyam": True,
            "udyam_registration_number": "UDYAM-GJ-01-9988776",
            "has_zed_certification": False
        }
        evaluations = [
            {
                "scheme_code": "GJ-INTEREST-2025",
                "status": "MATCH",
                "condition_results": []
            }
        ]

        unlocks = self.engine.evaluate_unlocks(
            evaluations=evaluations,
            business_facts=business_facts,
            candidate_schemes=[self.scheme_gj_int]
        )

        zed_unlock = next((u for u in unlocks if u.prerequisite_type == PrerequisiteType.CERTIFICATION), None)
        self.assertIsNotNone(zed_unlock)
        self.assertIn("ZED", zed_unlock.unlock_action)
        self.assertIn("QCI", zed_unlock.required_user_confirmation)

    def test_graph_reachability_across_prerequisite_edges(self):
        """Graph reachability expands affected opportunities across PREREQUISITE relationships."""
        business_facts = {
            "has_udyam": True,
            "udyam_registration_number": "UDYAM-GJ-01-1122334"
        }
        evaluations = [
            {
                "scheme_code": "CGTMSE-CENTRAL",
                "status": "POTENTIAL_MATCH",
                "condition_results": [
                    {
                        "rule_id": "rule_cgtmse_sanction",
                        "display_label": "Enrollment under CGTMSE trust cover",
                        "status": "UNKNOWN"
                    }
                ]
            }
        ]

        unlocks = self.engine.evaluate_unlocks(
            evaluations=evaluations,
            business_facts=business_facts,
            candidate_schemes=[self.scheme_cgtmse, self.scheme_gj_cap]
        )

        cgtmse_unlock = next((u for u in unlocks if "CGTMSE" in u.unlock_action), None)
        self.assertIsNotNone(cgtmse_unlock)
        # Because CGTMSE is prerequisite to GJ-CAPITAL, both should appear in affected_opportunities
        aff_codes = {o.scheme_code for o in cgtmse_unlock.affected_opportunities}
        self.assertIn("CGTMSE-CENTRAL", aff_codes)
        self.assertIn("GJ-CAPITAL-2025", aff_codes)


class OpportunityUnlockServiceAndAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()

        self.profile = BusinessProfile.objects.create(
            business_name="Shree Ram Forge Pvt Ltd",
            msme_category="small",
            industry_sector="Forging Manufacturing",
            state="Gujarat",
            district="Ahmedabad",
            investment_in_plant_machinery_lakhs=40.0,
            annual_turnover_lakhs=120.0,
            udyam_registration_number=""  # Missing Udyam triggers unlock
        )
        self.goal = BusinessGoal.objects.create(
            business_profile=self.profile,
            raw_goal_text="Setup hydraulic press machine"
        )
        self.strategy = Strategy.objects.create(
            goal=self.goal,
            business_profile=self.profile,
            narrative="Strategic Roadmap"
        )

    def test_service_generates_and_persists_unlocks(self):
        """OpportunityUnlockService persists OpportunityUnlock records with all schema fields."""
        evaluations_data = [
            {
                "scheme_code": "GJ-CAPITAL-2025",
                "status": "POTENTIAL_MATCH",
                "missing_info": ["Udyam Registration"]
            }
        ]

        unlocks = OpportunityUnlockService.generate_unlocks_for_strategy(
            strategy=self.strategy,
            evaluations_data=evaluations_data
        )

        self.assertTrue(len(unlocks) > 0)
        saved = OpportunityUnlock.objects.filter(strategy=self.strategy).first()
        self.assertIsNotNone(saved)
        self.assertTrue(len(saved.unlock_action) > 0)
        self.assertTrue(len(saved.current_blocker) > 0)
        self.assertTrue(len(saved.required_user_confirmation) > 0)
        self.assertTrue(len(saved.explanation) > 0)
        self.assertIsInstance(saved.affected_opportunities, list)
        self.assertIsInstance(saved.evidence_ids, list)

    def test_api_evaluate_unlocks(self):
        """POST /api/v1/opportunities/evaluate/ returns calculated unlock candidates."""
        payload = {
            "evaluations": [
                {
                    "scheme_code": "GJ-CAPITAL-2025",
                    "status": "POTENTIAL_MATCH",
                    "missing_info": ["Udyam Registration"]
                }
            ],
            "business_facts": {
                "has_udyam": False,
                "industry_sector": "Manufacturing"
            }
        }
        response = self.client.post('/api/v1/opportunities/evaluate/', payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(len(response.data) > 0)
        item = response.data[0]
        self.assertIn("unlock_action", item)
        self.assertIn("current_blocker", item)
        self.assertIn("affected_opportunities", item)
        self.assertIn("required_user_confirmation", item)
        self.assertIn("explanation", item)
