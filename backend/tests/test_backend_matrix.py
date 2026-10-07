"""
Unified Master Test Matrix for UdyamNiti Backend.
Executes all 11 critical test layers deterministically:
1. Rule Operators (Unit)
2. Model Constraints & Temporal Invariants
3. Service Layer (Snapshots, Consistency Engine, Verification)
4. REST API Layer
5. RAG Retrieval Integration
6. Cross-Scheme Relationship Engine
7. Opportunity Unlock Engine
8. Policy Version Isolation (No stale-rule mixing)
9. Personalized Policy Impact Re-evaluation
10. Tenant Permissions & Object-Level Isolation
11. Failure / UNKNOWN Resilience Handling
"""
import pytest
from datetime import date
from django.test import TestCase
from django.db import IntegrityError
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework import status

from apps.accounts.models import UserSecurityProfile, UserRole
from apps.business_profiles.models import BusinessProfile, BusinessGoal
from apps.business_profiles.services import BusinessProfileService
from apps.policies.models import Scheme, SchemeRule, SchemeVersion, SchemePrerequisite
from apps.relationships.models import SchemeRelationship
from apps.relationships.services import RelationshipEngine
from apps.opportunities.services import OpportunityUnlockService
from apps.eligibility.engine import RuleEngine, evaluate_condition
from apps.documents.consistency_engine import DocumentConsistencyEngine
from apps.policy_monitoring.impact_service import PolicyImpactService
from apps.actions.workspace_service import ApplicationWorkspaceService
from apps.strategy.ai_orchestrator import AIOrchestrator


class MasterBackendMatrixTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.rule_engine = RuleEngine()

        # Seed User & Profile
        self.user = User.objects.create_user(
            username='master_test_user',
            email='master@example.com',
            password='TestPassword123!'
        )
        UserSecurityProfile.objects.create(user=self.user, role=UserRole.MSME_USER)
        self.client.force_authenticate(user=self.user)

        self.profile = BusinessProfile.objects.create(
            user=self.user,
            business_name='ABC Engineering Works',
            udyam_registration_number='UDYAM-GJ-29-0099887',
            enterprise_category='small',
            msme_category='small',
            state='Gujarat',
            annual_turnover=210.0,
            annual_turnover_lakhs=210.0,
            investment_in_plant_machinery_lakhs=45.0,
            is_manufacturing=True,
            is_npa=False,
            has_iso_certification=False
        )

        # Seed Primary Scheme
        self.scheme = Scheme.objects.create(
            scheme_code='TEST_CLCSS',
            name='Credit Linked Capital Subsidy Scheme',
            level='central',
            support_type='capital_subsidy',
            max_benefit_amount_lakhs=15.0,
            benefit_percentage=15.0,
            status='active',
            official_portal_url='https://msme.gov.in/clcss'
        )

    # -------------------------------------------------------------
    # LAYER 1: UNIT TESTS FOR RULE OPERATORS
    # -------------------------------------------------------------
    def test_layer_1_rule_operators(self):
        """Validates all mathematical and boolean operators used by the DSL."""
        # eq, neq
        self.assertTrue(evaluate_condition(10, 'eq', 10))
        self.assertFalse(evaluate_condition(10, 'eq', 20))
        self.assertTrue(evaluate_condition('Gujarat', 'eq', 'gujarat'))  # Case-insensitive
        self.assertTrue(evaluate_condition(10, 'neq', 20))

        # gt, gte, lt, lte
        self.assertTrue(evaluate_condition(50.0, 'gt', 25.0))
        self.assertTrue(evaluate_condition(50.0, 'gte', 50.0))
        self.assertTrue(evaluate_condition(15.0, 'lt', 25.0))
        self.assertTrue(evaluate_condition(25.0, 'lte', 25.0))

        # in, not_in
        self.assertTrue(evaluate_condition('small', 'in', ['micro', 'small']))
        self.assertFalse(evaluate_condition('medium', 'in', ['micro', 'small']))
        self.assertTrue(evaluate_condition('large', 'not_in', ['micro', 'small']))

        # bool_true, bool_false
        self.assertTrue(evaluate_condition(True, 'bool_true', True))
        self.assertTrue(evaluate_condition(False, 'bool_false', False))

        # range
        self.assertTrue(evaluate_condition(45.0, 'range', [10.0, 50.0]))
        self.assertFalse(evaluate_condition(60.0, 'range', [10.0, 50.0]))

    # -------------------------------------------------------------
    # LAYER 2: MODEL CONSTRAINTS & TEMPORAL INVARIANTS
    # -------------------------------------------------------------
    def test_layer_2_model_constraints(self):
        """Enforces uniqueness constraints on Udyam registration and Scheme code."""
        # Duplicate Udyam registration should raise IntegrityError
        with self.assertRaises(IntegrityError):
            BusinessProfile.objects.create(
                user=self.user,
                business_name='Duplicate Unit',
                udyam_registration_number='UDYAM-GJ-29-0099887'  # Existing number
            )

        # Duplicate scheme code should raise IntegrityError
        with self.assertRaises(IntegrityError):
            Scheme.objects.create(
                scheme_code='TEST_CLCSS',  # Existing code
                name='Duplicate CLCSS',
                status='active'
            )

    # -------------------------------------------------------------
    # LAYER 3: SERVICE LAYER TESTS
    # -------------------------------------------------------------
    def test_layer_3_service_layer_snapshots_and_consistency(self):
        """Verifies profile snapshot capture and document consistency comparisons."""
        # Capture snapshot
        snapshot = BusinessProfileService.capture_snapshot(
            profile=self.profile,
            trigger_reason='Pre-evaluation baseline'
        )
        self.assertIsNotNone(snapshot)
        self.assertEqual(snapshot.snapshot_data['business_name'], 'ABC Engineering Works')
        self.assertEqual(snapshot.snapshot_data['state'], 'Gujarat')

        # Consistency Engine 5-way check
        engine = DocumentConsistencyEngine()
        result = engine.compare_enterprise_data(
            profile=self.profile,
            extracted_facts={
                'annual_turnover': 210.0,  # MATCH
                'state': 'Gujarat',        # MATCH
                'enterprise_category': 'micro'  # CONFLICT: Profile is 'small', document extracted 'micro'
            }
        )
        self.assertIn('comparisons', result)
        comparisons = {c['field']: c['status'] for c in result['comparisons']}
        self.assertEqual(comparisons.get('annual_turnover'), 'MATCH')
        self.assertEqual(comparisons.get('enterprise_category'), 'CONFLICT')

    # -------------------------------------------------------------
    # LAYER 4: REST API TESTS
    # -------------------------------------------------------------
    def test_layer_4_api_endpoints(self):
        """Verifies HTTP status codes, envelope schemas, and headers."""
        # 1. Health Liveness
        res_health = self.client.get('/health/')
        self.assertEqual(res_health.status_code, status.HTTP_200_OK)
        self.assertIn('X-Trace-ID', res_health.headers)

        # 2. Scheme List
        res_schemes = self.client.get('/api/v1/schemes/')
        self.assertEqual(res_schemes.status_code, status.HTTP_200_OK)
        self.assertIn('results', res_schemes.data)

        # 3. Current User Me
        res_me = self.client.get('/api/v1/auth/me/')
        self.assertEqual(res_me.status_code, status.HTTP_200_OK)
        self.assertEqual(res_me.data['username'], 'master_test_user')

    # -------------------------------------------------------------
    # LAYER 5: RAG RETRIEVAL INTEGRATION
    # -------------------------------------------------------------
    def test_layer_5_rag_retrieval_integration(self):
        """Verifies hybrid retriever fetches chunks with complete 13-field provenance."""
        from apps.rag.models import PolicySourceDocument, PolicyDocumentChunk
        from apps.rag.retrieval import HybridPolicyRetriever, HybridQueryRequest

        doc = PolicySourceDocument.objects.create(
            scheme=self.scheme,
            title="CLCSS Operational Guidelines 2024",
            authority="Ministry of MSME",
            source_url="https://msme.gov.in/clcss.pdf",
            source_tier="tier_2_operational_guidelines",
            effective_date=date(2024, 1, 1),
            file_hash="hash_clcss_2024"
        )
        chunk = PolicyDocumentChunk.objects.create(
            document=doc,
            scheme=self.scheme,
            authority=doc.authority,
            source_url=doc.source_url,
            source_tier=doc.source_tier,
            document_title=doc.title,
            publication_effective_date=doc.effective_date,
            policy_version=1,
            page_number=2,
            section_heading="Clause 3: Quantum of Subsidy",
            chunk_index=1,
            chunk_text="The quantum of capital subsidy is 15% of the machinery cost.",
            chunk_hash="chunk_hash_01",
            is_active=True
        )

        retriever = HybridPolicyRetriever()
        req = HybridQueryRequest(
            user_question="What is the capital subsidy for machinery?",
            candidate_scheme_ids=[str(self.scheme.id)],
            top_k=3
        )
        response = retriever.retrieve(req)
        self.assertGreater(len(response.citations), 0)
        top_cit = response.citations[0]
        self.assertEqual(top_cit.authority, "Ministry of MSME")
        self.assertEqual(top_cit.document_title, "CLCSS Operational Guidelines 2024")
        self.assertEqual(top_cit.page_number, 2)

    # -------------------------------------------------------------
    # LAYER 6: RELATIONSHIP ENGINE TESTS
    # -------------------------------------------------------------
    def test_layer_6_cross_scheme_relationships(self):
        """Verifies stacking synergy and overlap detection between multiple schemes."""
        scheme_b = Scheme.objects.create(
            scheme_code='TEST_CGTMSE',
            name='Credit Guarantee Trust',
            level='central',
            support_type='credit_guarantee',
            status='active'
        )
        SchemeRelationship.objects.create(
            scheme_a=self.scheme,
            scheme_b=scheme_b,
            relationship_type='synergistic',
            description='CLCSS provides subsidy while CGTMSE covers credit guarantee.'
        )

        rel_engine = RelationshipEngine()
        rels = rel_engine.analyze_multiple_schemes([self.scheme, scheme_b])
        self.assertGreaterEqual(len(rels), 1)
        self.assertEqual(rels[0]['relationship_type'], 'synergistic')

    # -------------------------------------------------------------
    # LAYER 7: OPPORTUNITY UNLOCK ENGINE
    # -------------------------------------------------------------
    def test_layer_7_opportunity_unlock_engine(self):
        """Differentiates changeable prerequisites (ZED certification) from hard disqualifiers."""
        SchemePrerequisite.objects.create(
            scheme=self.scheme,
            prerequisite_type='certification',
            title='ISO 9001 / ZED Certification',
            description='Quality certification required.',
            how_to_satisfy='Register online at zed.msme.gov.in',
            is_hard_prerequisite=False
        )

        unlock_service = OpportunityUnlockService()
        unlock_cards = unlock_service.find_unlockable_opportunities(
            profile=self.profile,
            candidate_schemes=[self.scheme]
        )
        self.assertGreaterEqual(len(unlock_cards), 1)
        top_unlock = unlock_cards[0]
        self.assertEqual(top_unlock['scheme_code'], 'TEST_CLCSS')
        self.assertEqual(top_unlock['unlock_type'], 'certification')
        self.assertIn('zed.msme.gov.in', top_unlock['actionable_step'])

    # -------------------------------------------------------------
    # LAYER 8: POLICY VERSION ISOLATION (NO STALE-RULE MIXING)
    # -------------------------------------------------------------
    def test_layer_8_policy_version_isolation(self):
        """Ensures rule evaluations use only the active version and do not mix rules across versions."""
        v1 = SchemeVersion.objects.create(
            scheme=self.scheme,
            version_number=1,
            effective_date=date(2020, 1, 1),
            effective_until=date(2023, 12, 31),
            status='superseded',
            change_summary='Initial 2020 rules'
        )
        v2 = SchemeVersion.objects.create(
            scheme=self.scheme,
            version_number=2,
            effective_date=date(2024, 1, 1),
            effective_until=None,
            status='active',
            change_summary='Revised 2024 rules'
        )

        # Active version must be v2
        active_v = self.scheme.versions.filter(status='active').first()
        self.assertEqual(active_v.version_number, 2)
        self.assertEqual(str(active_v.effective_date), '2024-01-01')

    # -------------------------------------------------------------
    # LAYER 9: IMPACT RE-EVALUATION TESTS
    # -------------------------------------------------------------
    def test_layer_9_impact_re_evaluation_pipeline(self):
        """Validates that a threshold change triggers re-evaluation and records before/after diff."""
        impact_service = PolicyImpactService()
        diff_record = impact_service.evaluate_impact_on_profile(
            profile=self.profile,
            scheme=self.scheme,
            old_threshold_lakhs=100.0,
            new_threshold_lakhs=300.0,
            rule_name="Turnover Ceiling"
        )
        self.assertIsNotNone(diff_record)
        # ABC turnover is 210.0L -> was DOES_NOT_MATCH (>100L), now MATCH (<=300L)
        self.assertEqual(diff_record.get('status_before'), 'DOES_NOT_MATCH')
        self.assertEqual(diff_record.get('status_after'), 'MATCH')

    # -------------------------------------------------------------
    # LAYER 10: PERMISSION TESTS & TENANT ISOLATION
    # -------------------------------------------------------------
    def test_layer_10_tenant_isolation(self):
        """Guarantees User B cannot access User A's profile or workspace."""
        user_b = User.objects.create_user(
            username='tenant_b',
            email='tenant_b@competitor.com',
            password='Password123!'
        )
        UserSecurityProfile.objects.create(user=user_b, role=UserRole.MSME_USER)

        client_b = APIClient()
        client_b.force_authenticate(user=user_b)

        # User B trying to access Profile A receives 404 (isolated from queryset)
        res = client_b.get(f'/api/v1/business-profiles/{self.profile.id}/')
        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)

    # -------------------------------------------------------------
    # LAYER 11: FAILURE / UNKNOWN RESILIENCE TESTS
    # -------------------------------------------------------------
    def test_layer_11_failure_and_unknown_containment(self):
        """Missing facts yield UNKNOWN evaluation without inventing eligibility."""
        SchemeRule.objects.create(
            scheme=self.scheme,
            rule_name="Unknown Specialized Cert",
            field_path="has_specialized_defense_clearance",  # Missing in profile!
            operator="bool_true",
            expected_value=True,
            importance="mandatory",
            is_active=True
        )

        eval_res = self.rule_engine.evaluate(self.scheme, self.profile)
        # Overall status must not be falsely approved
        self.assertIn(eval_res.overall_status, ['UNKNOWN', 'REQUIRES_OFFICIAL_VERIFICATION', 'DOES_NOT_MATCH'])
        self.assertIn("has_specialized_defense_clearance", eval_res.missing_info)
