"""
Unit and Integration Tests for Policy Change Detection Pipeline.
Verifies:
1. Multidimensional diffing across rules, thresholds, dates, benefits, prerequisites, documents, and routes.
2. Material vs Informational change classification.
3. Output schema: change_type, old_value, new_value, affected_rule_ids, effective_date, evidence_source, confidence, requires_human_review.
4. Curated manual confirmation workflow (approve / reject).
5. Celery asynchronous task execution.
6. REST API endpoints.
"""
import datetime
from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status

from apps.policies.models import Scheme
from apps.policy_monitoring.models import (
    PolicyChange,
    ChangeType,
    MaterialityClassification,
    ReviewStatus
)
from apps.policy_monitoring.diff_service import PolicyDiffPipelineService
from apps.policy_monitoring.tasks import detect_policy_changes_task


class PolicyDiffPipelineTests(TestCase):
    def setUp(self):
        self.scheme = Scheme.objects.create(
            scheme_code="GJ-CAPITAL-2025",
            name="Gujarat MSME Capital Subsidy Scheme",
            level="state_gujarat",
            support_type="capital_subsidy",
            status="active"
        )

        self.old_policy_data = {
            "max_benefit_amount_lakhs": 25.0,
            "benefit_percentage": 20.0,
            "valid_until": "2025-03-31",
            "official_portal_url": "https://legacy-dic.gujarat.gov.in",
            "prerequisites": ["udyam_registration"],
            "required_documents": ["udyam_certificate", "pan_card"],
            "rules": [
                {
                    "rule_id": "rule_investment_cap",
                    "rule_name": "Investment in Machinery",
                    "operator": "lte",
                    "expected_value": 500.0,
                    "importance": "mandatory"
                },
                {
                    "rule_id": "rule_old_power_audit",
                    "rule_name": "Power Audit Report",
                    "operator": "eq",
                    "expected_value": True,
                    "importance": "preferred"
                }
            ]
        }

        self.new_policy_data = {
            "max_benefit_amount_lakhs": 35.0,  # Changed threshold & benefit
            "benefit_percentage": 25.0,        # Changed benefit percentage
            "valid_until": "2027-12-31",       # Extended date
            "official_portal_url": "https://ifp.gujarat.gov.in",  # Changed route
            "prerequisites": ["udyam_registration", "zed_bronze_certification"],  # Added prerequisite
            "required_documents": ["udyam_certificate", "pan_card", "ca_gfci_certificate"],  # Added document
            "rules": [
                {
                    "rule_id": "rule_investment_cap",
                    "rule_name": "Investment in Machinery",
                    "operator": "lte",
                    "expected_value": 1000.0,  # Changed threshold (500L -> 1000L)
                    "importance": "mandatory"
                },
                {
                    "rule_id": "rule_zed_bronze",  # Newly added rule
                    "rule_name": "ZED Bronze Quality Certification",
                    "operator": "eq",
                    "expected_value": True,
                    "importance": "preferred"
                }
                # rule_old_power_audit removed
            ]
        }

    def test_execute_diff_pipeline_detects_all_dimensions(self):
        """Pipeline must detect changes across all 7 dimensions and classify materiality."""
        changes = PolicyDiffPipelineService.execute_diff_pipeline(
            scheme=self.scheme,
            old_policy_data=self.old_policy_data,
            new_policy_data=self.new_policy_data,
            evidence_source="Gazette Resolution No. SSI/102020/MSME-Incentive/W, Clause 4.1",
            effective_date=datetime.date(2025, 4, 1),
            confidence_of_extraction=0.98,
            persist=True
        )

        self.assertTrue(len(changes) >= 7)

        change_types = {c.change_type for c in changes}
        self.assertIn(ChangeType.THRESHOLDS, change_types)
        self.assertIn(ChangeType.ELIGIBILITY_RULES, change_types)
        self.assertIn(ChangeType.BENEFIT_DETAILS, change_types)
        self.assertIn(ChangeType.DATES, change_types)
        self.assertIn(ChangeType.PREREQUISITES, change_types)
        self.assertIn(ChangeType.REQUIRED_DOCUMENTS, change_types)
        self.assertIn(ChangeType.APPLICATION_ROUTE, change_types)

        # Threshold change check
        th_change = next(c for c in changes if c.change_type == ChangeType.THRESHOLDS)
        self.assertEqual(th_change.materiality, MaterialityClassification.MATERIAL)
        self.assertEqual(th_change.old_value["expected_value"], 500.0)
        self.assertEqual(th_change.new_value["expected_value"], 1000.0)
        self.assertTrue(th_change.requires_human_review)
        self.assertEqual(th_change.review_status, ReviewStatus.PENDING_REVIEW)

        # Benefit change check
        ben_change = next(c for c in changes if c.change_type == ChangeType.BENEFIT_DETAILS and c.new_value == 35.0)
        self.assertEqual(ben_change.materiality, MaterialityClassification.MATERIAL)
        self.assertEqual(ben_change.old_value, 25.0)

        # Application route check (should be classified as INFORMATIONAL)
        route_change = next(c for c in changes if c.change_type == ChangeType.APPLICATION_ROUTE)
        self.assertEqual(route_change.materiality, MaterialityClassification.INFORMATIONAL)
        self.assertEqual(route_change.new_value, "https://ifp.gujarat.gov.in")

    def test_curated_approval_and_rejection_workflow(self):
        """Curator approval marks change approved_active; rejection marks rejected."""
        change = PolicyChange.objects.create(
            scheme=self.scheme,
            change_type=ChangeType.THRESHOLDS,
            materiality=MaterialityClassification.MATERIAL,
            change_summary="Subsidy cap increased",
            old_value={"expected_value": 25.0},
            new_value={"expected_value": 35.0},
            evidence_source="Clause 4.1",
            requires_human_review=True,
            review_status=ReviewStatus.PENDING_REVIEW
        )

        self.assertEqual(change.review_status, ReviewStatus.PENDING_REVIEW)

        # Approve
        change.approve(curator_name="lead_curator")
        change.refresh_from_db()
        self.assertEqual(change.review_status, ReviewStatus.APPROVED_ACTIVE)
        self.assertEqual(change.reviewed_by, "lead_curator")
        self.assertIsNotNone(change.reviewed_at)

        # Reject
        change.reject(curator_name="lead_curator")
        change.refresh_from_db()
        self.assertEqual(change.review_status, ReviewStatus.REJECTED)

    def test_celery_task_execution(self):
        """Celery task executes asynchronously and returns summary counts."""
        res = detect_policy_changes_task(
            scheme_code="GJ-CAPITAL-2025",
            old_policy_data=self.old_policy_data,
            new_policy_data=self.new_policy_data,
            evidence_source="Official Notification 2025",
            effective_date_str="2025-04-01",
            confidence_of_extraction=0.99
        )
        self.assertEqual(res["status"], "success")
        self.assertTrue(res["total_changes"] > 0)
        self.assertTrue(res["material_changes"] > 0)


class PolicyMonitoringAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.scheme = Scheme.objects.create(
            scheme_code="GJ-CAPITAL-2025",
            name="Gujarat MSME Capital Subsidy",
            level="state_gujarat",
            support_type="capital_subsidy"
        )
        self.change = PolicyChange.objects.create(
            scheme=self.scheme,
            change_type=ChangeType.THRESHOLDS,
            materiality=MaterialityClassification.MATERIAL,
            change_summary="Cap increased from 25L to 35L",
            old_value=25.0,
            new_value=35.0,
            evidence_source="Gazette 2025",
            requires_human_review=True,
            review_status=ReviewStatus.PENDING_REVIEW
        )

    def test_api_execute_diff(self):
        """POST /api/v1/policy-monitoring/diff/ runs diff pipeline."""
        payload = {
            "scheme_code": "GJ-CAPITAL-2025",
            "old_policy_data": {"max_benefit_amount_lakhs": 25.0},
            "new_policy_data": {"max_benefit_amount_lakhs": 35.0},
            "evidence_source": "Notification 2025"
        }
        res = self.client.post('/api/v1/policy-monitoring/diff/', payload, format='json')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn("total_changes_detected", res.data)
        self.assertTrue(res.data["total_changes_detected"] > 0)

    def test_api_list_changes_filtered(self):
        """GET /api/v1/policy-monitoring/changes/ supports filtering."""
        res = self.client.get('/api/v1/policy-monitoring/changes/?materiality=material&review_status=pending_review')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data['results']), 1)
        self.assertEqual(res.data['results'][0]['change_type'], 'thresholds')

    def test_api_approve_change(self):
        """POST /api/v1/policy-monitoring/changes/<id>/approve/ approves change."""
        res = self.client.post(f'/api/v1/policy-monitoring/changes/{self.change.id}/approve/', {'curator_name': 'test_admin'})
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data['review_status'], 'approved_active')
        self.assertEqual(res.data['reviewed_by'], 'test_admin')

    def test_api_reject_change(self):
        """POST /api/v1/policy-monitoring/changes/<id>/reject/ rejects change."""
        res = self.client.post(f'/api/v1/policy-monitoring/changes/{self.change.id}/reject/', {'curator_name': 'test_admin'})
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data['review_status'], 'rejected')
