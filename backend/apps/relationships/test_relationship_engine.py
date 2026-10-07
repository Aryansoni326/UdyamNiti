"""
Unit and Integration Tests for Cross-Scheme Relationship Intelligence Engine.
Validates:
1. Structured relationship evaluation (COMPATIBLE, INCOMPATIBLE, PREREQUISITE, SEQUENTIAL, OVERLAPPING).
2. Cost-head overlap detection (statutory non-duplication on plant & machinery).
3. Fail-closed UNKNOWN behavior when official evidence is absent (never assumes compatibility).
4. 'Can I combine these?' multi-scheme query evaluation.
5. Topological sequencing recommendations.
6. API endpoint functionality and demo data seeding.
"""
from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status

from apps.policies.models import Scheme
from apps.relationships.models import (
    SchemeRelationship,
    RelationshipType,
    RelationshipDirection
)
from apps.relationships.services import RelationshipEngine, CanCombineResult
from apps.relationships.demo_data import SYNTHETIC_DEMO_RELATIONSHIPS


class RelationshipEngineUnitTests(TestCase):
    def setUp(self):
        self.engine = RelationshipEngine()

        self.scheme_gj_cap = Scheme.objects.create(
            scheme_code="GJ-CAPITAL-2025",
            name="Gujarat MSME Capital Investment Subsidy",
            ministry_department="Govt of Gujarat Industries Comm.",
            level="state_gujarat",
            support_type="capital_subsidy",
            status="active"
        )
        self.scheme_gj_int = Scheme.objects.create(
            scheme_code="GJ-INTEREST-2025",
            name="Gujarat MSME Interest Subsidy",
            ministry_department="Govt of Gujarat Industries Comm.",
            level="state_gujarat",
            support_type="interest_subvention",
            status="active"
        )
        self.scheme_pmegp = Scheme.objects.create(
            scheme_code="PMEGP-CENTRAL",
            name="Prime Minister Employment Generation Programme",
            ministry_department="Ministry of MSME",
            level="central",
            support_type="capital_subsidy",
            status="active"
        )
        self.scheme_cgtmse = Scheme.objects.create(
            scheme_code="CGTMSE-CENTRAL",
            name="Credit Guarantee Trust for MSMEs",
            ministry_department="Ministry of MSME",
            level="central",
            support_type="credit_guarantee",
            status="active"
        )
        self.scheme_unknown = Scheme.objects.create(
            scheme_code="UNKNOWN-SCHEME-X",
            name="Novel Uncatalogued Support Scheme",
            ministry_department="Department of Science",
            level="central",
            support_type="digitalization",
            status="active"
        )

        # Create structured relationship: GJ-CAPITAL and GJ-INTEREST are COMPATIBLE
        self.rel_compatible = SchemeRelationship.objects.create(
            scheme_a=self.scheme_gj_cap,
            scheme_b=self.scheme_gj_int,
            relationship_type=RelationshipType.COMPATIBLE,
            direction=RelationshipDirection.BIDIRECTIONAL,
            affected_cost_categories=["plant_and_machinery", "term_loan_interest"],
            conditions={"term_loan_required": True},
            evidence_ids=["chunk-gj-001"],
            source_evidence="Resolution Clause 4.3 permits concurrent interest subsidy on capital asset term loan.",
            description="Stackable benefits on identical term loan."
        )

        # Create structured relationship: PMEGP and GJ-CAPITAL are INCOMPATIBLE on same asset
        self.rel_incompatible = SchemeRelationship.objects.create(
            scheme_a=self.scheme_pmegp,
            scheme_b=self.scheme_gj_cap,
            relationship_type=RelationshipType.INCOMPATIBLE,
            direction=RelationshipDirection.BIDIRECTIONAL,
            affected_cost_categories=["plant_and_machinery"],
            conditions={"same_expenditure_invoice": True},
            evidence_ids=["chunk-pmegp-001"],
            source_evidence="PMEGP Para 11.2 prohibits dual central/state capital subsidy claims on same machinery.",
            description="Non-duplication conflict on capital subsidy."
        )

        # Create structured relationship: CGTMSE -> GJ-CAPITAL is SEQUENTIAL (A_TO_B)
        self.rel_sequential = SchemeRelationship.objects.create(
            scheme_a=self.scheme_cgtmse,
            scheme_b=self.scheme_gj_cap,
            relationship_type=RelationshipType.SEQUENTIAL,
            direction=RelationshipDirection.A_TO_B,
            affected_cost_categories=["credit_collateral", "plant_and_machinery"],
            conditions={"loan_sanction_first": True},
            evidence_ids=["chunk-cgtmse-001"],
            source_evidence="Operational manual requires loan sanction prior to capital subsidy filing.",
            description="Secure CGTMSE bank sanction before filing capital claim."
        )

    def test_evaluate_structured_compatible_pair(self):
        """Engine must return COMPATIBLE for pre-configured compatible schemes with citations."""
        res = self.engine.evaluate_pair(self.scheme_gj_cap, self.scheme_gj_int)
        self.assertEqual(res.relationship_type, RelationshipType.COMPATIBLE)
        self.assertIn("chunk-gj-001", res.evidence_ids)
        self.assertIn("plant_and_machinery", res.affected_cost_categories)
        self.assertIn("term_loan_interest", res.affected_cost_categories)

    def test_evaluate_structured_incompatible_pair(self):
        """Engine must return INCOMPATIBLE for mutually exclusive schemes."""
        res = self.engine.evaluate_pair(self.scheme_pmegp, self.scheme_gj_cap)
        self.assertEqual(res.relationship_type, RelationshipType.INCOMPATIBLE)
        self.assertIn("Non-duplication", res.tradeoff_explanation)
        self.assertIn("chunk-pmegp-001", res.evidence_ids)

    def test_evaluate_reverse_direction_lookup(self):
        """Querying (B, A) when relationship is stored as (A, B) must correctly invert direction."""
        # rel_sequential is stored as CGTMSE (A) -> GJ-CAPITAL (B) with A_TO_B
        res = self.engine.evaluate_pair(self.scheme_gj_cap, self.scheme_cgtmse)
        self.assertEqual(res.relationship_type, RelationshipType.SEQUENTIAL)
        # Because we queried GJ-CAPITAL as first param, direction relative to it is B_TO_A
        self.assertEqual(res.direction, RelationshipDirection.B_TO_A)

    def test_cost_head_overlap_detection(self):
        """Unstructured pair sharing plant & machinery capital expenditure must trigger OVERLAPPING."""
        # Create a new central capital scheme without an explicit relationship record
        new_cap = Scheme.objects.create(
            scheme_code="CENTRAL-TECH-CAPITAL",
            name="Central Technology Capital Grant",
            ministry_department="Govt of India",
            level="central",
            support_type="capital_subsidy",
            status="active"
        )
        res = self.engine.evaluate_pair(self.scheme_gj_cap, new_cap)
        self.assertEqual(res.relationship_type, RelationshipType.OVERLAPPING)
        self.assertTrue(res.is_overlapping_cost)
        self.assertIn("plant_and_machinery", res.affected_cost_categories)
        self.assertIn("Statutory Cost Overlap", res.tradeoff_explanation)

    def test_unknown_fail_closed_invariant(self):
        """Never assume compatibility merely because schemes differ: insufficient evidence returns UNKNOWN."""
        res = self.engine.evaluate_pair(self.scheme_gj_int, self.scheme_unknown)
        self.assertEqual(res.relationship_type, RelationshipType.UNKNOWN)
        self.assertIn("Statutory Relationship UNKNOWN", res.tradeoff_explanation)
        self.assertEqual(len(res.evidence_ids), 0)

    def test_can_combine_compatible_pair(self):
        """can_combine on compatible pair returns COMPATIBLE verdict and empty conflicts."""
        result: CanCombineResult = self.engine.can_combine(["GJ-CAPITAL-2025", "GJ-INTEREST-2025"])
        self.assertEqual(result.overall_verdict, RelationshipType.COMPATIBLE)
        self.assertEqual(len(result.conflicts), 0)
        self.assertIn("can be safely stacked concurrently", result.synthesis_explanation)

    def test_can_combine_incompatible_triplet(self):
        """can_combine including an incompatible scheme must yield INCOMPATIBLE with clear conflict."""
        result: CanCombineResult = self.engine.can_combine(
            ["GJ-CAPITAL-2025", "GJ-INTEREST-2025", "PMEGP-CENTRAL"]
        )
        self.assertEqual(result.overall_verdict, RelationshipType.INCOMPATIBLE)
        self.assertTrue(len(result.conflicts) > 0)
        conflict = result.conflicts[0]
        self.assertEqual(conflict["type"], "MUTUAL_EXCLUSION")
        self.assertIn("cannot be combined concurrently", result.synthesis_explanation)

    def test_can_combine_sequential_ordering(self):
        """can_combine must compute valid execution order based on prerequisite relationships."""
        result: CanCombineResult = self.engine.can_combine(
            ["GJ-CAPITAL-2025", "CGTMSE-CENTRAL"]
        )
        # CGTMSE is prerequisite to GJ-CAPITAL
        self.assertEqual(result.overall_verdict, RelationshipType.SEQUENTIAL)
        self.assertEqual(result.recommended_execution_order[0], "CGTMSE-CENTRAL")
        self.assertEqual(result.recommended_execution_order[1], "GJ-CAPITAL-2025")


class RelationshipAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()

        self.scheme_a = Scheme.objects.create(
            scheme_code="GJ-CAPITAL-2025",
            name="Gujarat MSME Capital Subsidy",
            ministry_department="Govt of Gujarat",
            level="state_gujarat",
            support_type="capital_subsidy",
            status="active"
        )
        self.scheme_b = Scheme.objects.create(
            scheme_code="GJ-INTEREST-2025",
            name="Gujarat MSME Interest Subsidy",
            ministry_department="Govt of Gujarat",
            level="state_gujarat",
            support_type="interest_subvention",
            status="active"
        )

        SchemeRelationship.objects.create(
            scheme_a=self.scheme_a,
            scheme_b=self.scheme_b,
            relationship_type=RelationshipType.COMPATIBLE,
            description="Stackable interest and capital subsidy.",
            evidence_ids=["chunk-001"]
        )

    def test_api_relationships_list(self):
        """GET /api/v1/relationships/ returns list of relationships."""
        response = self.client.get('/api/v1/relationships/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['relationship_type'], 'COMPATIBLE')

    def test_api_can_combine(self):
        """POST /api/v1/relationships/can-combine/ evaluates multi-scheme query."""
        payload = {
            "scheme_codes": ["GJ-CAPITAL-2025", "GJ-INTEREST-2025"]
        }
        response = self.client.post('/api/v1/relationships/can-combine/', payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['overall_verdict'], 'COMPATIBLE')
        self.assertIn('synthesis_explanation', response.data)

    def test_api_relationships_graph(self):
        """GET /api/v1/relationships/graph/ returns nodes and edges."""
        response = self.client.get('/api/v1/relationships/graph/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('nodes', response.data)
        self.assertIn('edges', response.data)
        self.assertEqual(len(response.data['nodes']), 2)
        self.assertEqual(len(response.data['edges']), 1)

    def test_api_seed_demo_relationships(self):
        """POST /api/v1/relationships/seed-demo/ seeds synthetic demo relationships."""
        response = self.client.post('/api/v1/relationships/seed-demo/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('total_records', response.data)
        self.assertTrue(response.data['total_records'] > 0)
        # Verify demo flag is set
        demo_count = SchemeRelationship.objects.filter(is_demo_data=True).count()
        self.assertEqual(demo_count, len(SYNTHETIC_DEMO_RELATIONSHIPS))
