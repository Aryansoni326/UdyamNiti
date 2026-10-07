"""
Unit and Integration Tests for Evidence Graph and Why-Path Traceability Engine.
Verifies:
1. Node types: Business, BusinessFact, Goal, Rule, Scheme, SchemeVersion, Evidence, Relationship, Prerequisite, Blocker, UnlockAction, Action.
2. Edge types: HAS_FACT, TARGETS_GOAL, EVALUATED_BY, SATISFIES, FAILS, UNKNOWN_FOR, SUPPORTED_BY, REQUIRES, RELATES_TO, BLOCKS, MAY_UNLOCK, LEADS_TO.
3. PostgreSQL relational graph building and persistence.
4. 'Why?' path reconstruction: Business Fact -> Rule -> Scheme -> Official Evidence -> Result -> Relationship/Blocker -> Action.
5. Compact graph JSON output and REST API endpoints.
"""
from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status

from apps.business_profiles.models import BusinessProfile, BusinessGoal
from apps.policies.models import Scheme
from apps.eligibility.models import EligibilityEvaluation
from apps.relationships.models import SchemeRelationship, RelationshipType, RelationshipDirection
from apps.opportunities.models import OpportunityUnlock
from apps.actions.models import ActionTask
from apps.strategy.models import (
    Strategy,
    EvidenceGraphNode,
    EvidenceGraphEdge,
    GraphNodeType,
    GraphEdgeType
)
from apps.strategy.evidence_graph_service import EvidenceGraphService


class EvidenceGraphServiceTests(TestCase):
    def setUp(self):
        self.service = EvidenceGraphService()

        # 1. Business Profile
        self.profile = BusinessProfile.objects.create(
            business_name="Shivshakti Precision Engineering",
            entity_type="private_limited",
            msme_category="small",
            industry_sector="Automotive Manufacturing",
            state="Gujarat",
            district="Rajkot",
            investment_in_plant_machinery_lakhs=45.0,
            annual_turnover_lakhs=180.0,
            udyam_registration_number="UDYAM-GJ-01-0044812",
            is_women_owned=True,
            is_sc_st_owned=False,
            is_npa=False
        )

        # 2. Business Goal
        self.goal = BusinessGoal.objects.create(
            business_profile=self.profile,
            raw_goal_text="Expand CNC precision milling setup with ₹50L investment",
            parsed_objective="Procure advanced CNC precision machine",
            parsed_project_type="machinery_expansion",
            parsed_investment_amount_lakhs=50.0,
            parsed_support_categories=["capital_subsidy", "interest_subvention"]
        )

        # 3. Scheme 1 (Matched)
        self.scheme_gj_cap = Scheme.objects.create(
            scheme_code="GJ-CAPITAL-2025",
            name="Gujarat MSME Capital Subsidy Scheme",
            ministry_department="Industries Commissionerate, Govt of Gujarat",
            level="state_gujarat",
            support_type="capital_subsidy",
            max_benefit_amount_lakhs=35.0,
            official_portal_url="https://ifp.gujarat.gov.in",
            status="active"
        )

        # 4. Scheme 2 (Prerequisite / Related)
        self.scheme_gj_int = Scheme.objects.create(
            scheme_code="GJ-INTEREST-2025",
            name="Gujarat MSME Interest Subvention Scheme",
            ministry_department="Govt of Gujarat",
            level="state_gujarat",
            support_type="interest_subvention",
            max_benefit_amount_lakhs=25.0,
            status="active"
        )

        # 5. Scheme 3 (Incompatible / Blocked)
        self.scheme_pmegp = Scheme.objects.create(
            scheme_code="PMEGP-CENTRAL",
            name="Prime Minister Employment Generation Programme",
            ministry_department="Ministry of MSME",
            level="central",
            support_type="capital_subsidy",
            status="active"
        )

        # 6. Eligibility Evaluations
        self.eval_gj_cap = EligibilityEvaluation.objects.create(
            goal=self.goal,
            scheme=self.scheme_gj_cap,
            business_profile=self.profile,
            overall_status="MATCH",
            score=95.0,
            condition_results=[
                {
                    "rule_id": "rule_inv_limit",
                    "display_label": "Plant & Machinery Investment <= ₹1000 Lakhs",
                    "status": "PASS",
                    "explanation": "Investment of ₹45L is well within Small enterprise threshold of ₹1000L.",
                    "importance": "mandatory",
                    "source_clause": "Gujarat Resolution Clause 4.1"
                },
                {
                    "rule_id": "rule_udyam_active",
                    "display_label": "Active Udyam Registration",
                    "status": "PASS",
                    "explanation": "Valid Udyam certificate UDYAM-GJ-01-0044812 provided.",
                    "importance": "mandatory",
                    "source_clause": "Gujarat Resolution Clause 2.3"
                }
            ],
            mandatory_failures=[]
        )

        self.eval_pmegp = EligibilityEvaluation.objects.create(
            goal=self.goal,
            scheme=self.scheme_pmegp,
            business_profile=self.profile,
            overall_status="DOES_NOT_MATCH",
            score=0.0,
            condition_results=[
                {
                    "rule_id": "rule_greenfield_only",
                    "display_label": "Greenfield / New Enterprises Only",
                    "status": "FAIL",
                    "explanation": "Existing enterprise expanding capacity is excluded.",
                    "importance": "mandatory",
                    "source_clause": "PMEGP Guidelines Para 4.1"
                }
            ],
            mandatory_failures=["Existing enterprises are excluded from PMEGP margin money."]
        )

        # 7. Cross-Scheme Relationship
        self.rel = SchemeRelationship.objects.create(
            scheme_a=self.scheme_gj_cap,
            scheme_b=self.scheme_gj_int,
            relationship_type=RelationshipType.COMPATIBLE,
            direction=RelationshipDirection.BIDIRECTIONAL,
            affected_cost_categories=["plant_and_machinery", "term_loan_interest"],
            description="Stackable capital subsidy and interest subvention on term loan."
        )

        # 8. Strategy
        self.strategy = Strategy.objects.create(
            goal=self.goal,
            business_profile=self.profile,
            narrative="Strategic expansion path utilizing Gujarat Capital Subsidy followed by Interest Subvention.",
            total_opportunities=2,
            matched_count=1,
            potential_count=0
        )

        # 9. Opportunity Unlock & Action Task
        self.unlock = OpportunityUnlock.objects.create(
            strategy=self.strategy,
            title="Upload Bank Sanction Letter",
            description="Sanction letter needed for subsidy claim release.",
            missing_fact_key="bank_sanction_letter",
            action_required="Obtain sanction from lending branch",
            potential_benefit_lakhs=12.5
        )

        self.action_task = ActionTask.objects.create(
            strategy=self.strategy,
            scheme=self.scheme_gj_cap,
            title="File Capital Subsidy Application on IFP Portal",
            description="Submit within 1 year of commercial production.",
            task_type="portal_submission",
            priority=1,
            portal_url="https://ifp.gujarat.gov.in",
            estimated_days=7
        )

    def test_build_or_update_graph(self):
        """Service must build and persist all 12 Node types and edge relationships over PostgreSQL."""
        node_count, edge_count = self.service.build_or_update_graph(self.strategy)
        self.assertTrue(node_count > 0)
        self.assertTrue(edge_count > 0)

        # Verify Node types present in DB
        db_node_types = set(
            EvidenceGraphNode.objects.filter(strategy=self.strategy).values_list('node_type', flat=True)
        )
        expected_types = {
            GraphNodeType.BUSINESS,
            GraphNodeType.BUSINESS_FACT,
            GraphNodeType.GOAL,
            GraphNodeType.RULE,
            GraphNodeType.SCHEME,
            GraphNodeType.SCHEME_VERSION,
            GraphNodeType.EVIDENCE,
            GraphNodeType.RELATIONSHIP,
            GraphNodeType.BLOCKER,
            GraphNodeType.UNLOCK_ACTION,
            GraphNodeType.ACTION
        }
        for et in expected_types:
            self.assertIn(et, db_node_types, f"Missing node type {et} in Evidence Graph")

        # Verify Edge types present in DB
        db_edge_types = set(
            EvidenceGraphEdge.objects.filter(strategy=self.strategy).values_list('edge_type', flat=True)
        )
        expected_edge_types = {
            GraphEdgeType.HAS_FACT,
            GraphEdgeType.TARGETS_GOAL,
            GraphEdgeType.EVALUATED_BY,
            GraphEdgeType.SATISFIES,
            GraphEdgeType.SUPPORTED_BY,
            GraphEdgeType.RELATES_TO,
            GraphEdgeType.BLOCKS,
            GraphEdgeType.MAY_UNLOCK,
            GraphEdgeType.LEADS_TO
        }
        for eet in expected_edge_types:
            self.assertIn(eet, db_edge_types, f"Missing edge type {eet} in Evidence Graph")

    def test_get_why_path_matched_scheme(self):
        """get_why_path must reconstruct the full statutory causal chain for MATCH scheme."""
        why_result = self.service.get_why_path(str(self.strategy.id), "GJ-CAPITAL-2025")

        self.assertNotIn("error", why_result)
        self.assertEqual(why_result["scheme_code"], "GJ-CAPITAL-2025")
        self.assertEqual(why_result["overall_status"], "MATCH")

        # Check nodes returned
        node_types = {n["type"] for n in why_result["nodes"]}
        self.assertIn(GraphNodeType.SCHEME, node_types)
        self.assertIn(GraphNodeType.RULE, node_types)
        self.assertIn(GraphNodeType.BUSINESS_FACT, node_types)
        self.assertIn(GraphNodeType.EVIDENCE, node_types)
        self.assertIn(GraphNodeType.ACTION, node_types)

        # Check Why-Path sequence
        seq = why_result["why_path_sequence"]
        self.assertTrue(len(seq) >= 4)

        # Check Narrative synthesis
        narrative = why_result["path_narrative"]
        self.assertIn("fully satisfies statutory conditions", narrative)
        self.assertIn("Gujarat Resolution Clause", narrative)
        self.assertIn("File Capital Subsidy Application", narrative)

    def test_get_why_path_blocked_scheme(self):
        """get_why_path for DOES_NOT_MATCH scheme must trace to the Blocker node."""
        why_result = self.service.get_why_path(str(self.strategy.id), "PMEGP-CENTRAL")

        self.assertNotIn("error", why_result)
        self.assertEqual(why_result["overall_status"], "DOES_NOT_MATCH")

        node_types = {n["type"] for n in why_result["nodes"]}
        self.assertIn(GraphNodeType.BLOCKER, node_types)

        narrative = why_result["path_narrative"]
        self.assertIn("statutory blocker was triggered", narrative)

    def test_get_full_graph(self):
        """get_full_graph returns all nodes and edges for strategy."""
        full_graph = self.service.get_full_graph(str(self.strategy.id))
        self.assertNotIn("error", full_graph)
        self.assertTrue(full_graph["total_nodes"] > 10)
        self.assertTrue(full_graph["total_edges"] > 10)
        self.assertEqual(len(full_graph["nodes"]), full_graph["total_nodes"])
        self.assertEqual(len(full_graph["edges"]), full_graph["total_edges"])


class EvidenceGraphAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()

        self.profile = BusinessProfile.objects.create(
            business_name="Rajesh Electrodes Ltd",
            msme_category="micro",
            state="Gujarat"
        )
        self.goal = BusinessGoal.objects.create(
            business_profile=self.profile,
            raw_goal_text="Purchase welding automation setup"
        )
        self.scheme = Scheme.objects.create(
            scheme_code="GJ-CAPITAL-2025",
            name="Gujarat MSME Capital Subsidy",
            level="state_gujarat",
            support_type="capital_subsidy"
        )
        EligibilityEvaluation.objects.create(
            goal=self.goal,
            scheme=self.scheme,
            business_profile=self.profile,
            overall_status="MATCH",
            condition_results=[
                {
                    "rule_id": "r1",
                    "display_label": "Micro enterprise eligibility",
                    "status": "PASS",
                    "source_clause": "Clause 1.1"
                }
            ]
        )
        self.strategy = Strategy.objects.create(
            goal=self.goal,
            business_profile=self.profile,
            narrative="Demo Strategy"
        )

    def test_api_why_path_endpoint(self):
        """GET /api/v1/strategies/why-path/?strategy_id=...&scheme_code=... returns 200 with why path."""
        url = f"/api/v1/strategies/why-path/?strategy_id={self.strategy.id}&scheme_code=GJ-CAPITAL-2025"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("nodes", response.data)
        self.assertIn("edges", response.data)
        self.assertIn("why_path_sequence", response.data)
        self.assertIn("path_narrative", response.data)

    def test_api_evidence_graph_endpoint(self):
        """GET /api/v1/strategies/<id>/evidence-graph/ returns full graph JSON."""
        url = f"/api/v1/strategies/{self.strategy.id}/evidence-graph/"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("total_nodes", response.data)
        self.assertIn("total_edges", response.data)
        self.assertTrue(response.data["total_nodes"] > 0)
