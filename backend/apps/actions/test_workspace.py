"""
Unit and Integration Tests for Application Preparation Workspace.
Verifies:
1. Workspace initialization for selected opportunity.
2. Tracks:
   - Eligibility conditions known vs unknown.
   - Required information prepared.
   - Required documents available vs missing/unverified.
   - Tasks completed.
   - Unknowns requiring verification.
3. Invariant: Never automate government submission, OTP, CAPTCHA, or final approvals.
4. Exposes clear official government route and portal link.
5. REST API endpoints (get-or-create, refresh, mark-applied).
"""
from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework import status

from apps.business_profiles.models import BusinessProfile
from apps.policies.models import Scheme, SchemeRule
from apps.documents.models import BusinessDocument
from apps.actions.models import ApplicationPreparationWorkspace, ActionTask, TaskCategory, CompletionStatus
from apps.actions.workspace_service import ApplicationWorkspaceService


class ApplicationWorkspaceTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="workspace_tester", password="password123")
        self.profile = BusinessProfile.objects.create(
            user=self.user,
            business_name="Mehsana Dairy Machinery Works",
            msme_category="small",
            entity_type="private_limited",
            industry_sector="Manufacturing",
            state="Gujarat",
            district="Mehsana",
            annual_turnover_lakhs=650.0,
            investment_in_plant_machinery_lakhs=140.0,
            udyam_registration_number="UDYAM-GJ-01-0077889",
            gstin="24AAACC9999F1Z1"
        )

        self.scheme = Scheme.objects.create(
            scheme_code="GJ-MSME-CAPITAL-2025",
            name="Gujarat MSME Capital Investment Subsidy Scheme",
            level="state_gujarat",
            support_type="capital_subsidy",
            max_benefit_amount_lakhs=35.0,
            status="active",
            target_states=["Gujarat"],
            official_portal_url="https://ifp.gujarat.gov.in"
        )

        # Add mandatory eligibility rules
        SchemeRule.objects.create(
            scheme=self.scheme,
            rule_name="Turnover Ceiling Check",
            field_path="annual_turnover_lakhs",
            operator="lte",
            expected_value=1000.0,
            importance="mandatory",
            is_active=True
        )
        SchemeRule.objects.create(
            scheme=self.scheme,
            rule_name="Plant Location Gujarat Check",
            field_path="state",
            operator="eq",
            expected_value="Gujarat",
            importance="mandatory",
            is_active=True
        )
        SchemeRule.objects.create(
            scheme=self.scheme,
            rule_name="Taluka Category Bonus Check",
            field_path="taluka_category",
            operator="in",
            expected_value=["Category 1", "Category 2"],
            importance="preferred",
            is_active=True
        )

        # Add an action task
        ActionTask.objects.create(
            business_profile=self.profile,
            scheme=self.scheme,
            title="Prepare OEM Quotation for CNC Equipment",
            rationale="Required for capital subsidy calculation",
            category=TaskCategory.DOCUMENTATION,
            status=CompletionStatus.PENDING
        )

        # Add an uploaded document (Udyam)
        BusinessDocument.objects.create(
            business_profile=self.profile,
            document_type="udyam_certificate",
            title="Udyam Certificate.pdf",
            verification_status="verified"
        )

    def test_workspace_initialization_and_readiness_metrics(self):
        """Workspace aggregates known/unknown conditions, required info, docs, and portal route."""
        ws = ApplicationWorkspaceService.get_or_create_workspace(
            profile_id=str(self.profile.id),
            scheme_id=str(self.scheme.id)
        )

        self.assertEqual(ws.business_profile.id, self.profile.id)
        self.assertEqual(ws.scheme.id, self.scheme.id)
        self.assertIn("ifp.gujarat.gov.in", ws.official_portal_url)

        # Invariant: Never automate government submission
        self.assertIn("final submission, OTP/Aadhaar verification", ws.disclaimer_notice)

        # Verify readiness metrics
        data = ws.workspace_data
        self.assertGreater(len(data["known_conditions"]), 0)
        self.assertGreater(len(data["unknown_conditions"]), 0)  # taluka_category is unknown
        self.assertEqual(ws.unknowns_count, 1)

        # Check required documents tracking
        req_docs = data["required_documents"]
        udyam_item = next((d for d in req_docs if d["document_type"] == "udyam_certificate"), None)
        self.assertIsNotNone(udyam_item)
        self.assertTrue(udyam_item["is_available"])
        self.assertTrue(udyam_item["is_verified"])

        # Check information fields
        info_fields = data["required_information"]
        self.assertTrue(all(f["is_prepared"] for f in info_fields if f["field_key"] in ("business_name", "udyam_registration_number", "gstin")))

        # Check task progress
        self.assertEqual(ws.tasks_total_count, 1)
        self.assertEqual(ws.tasks_completed_count, 0)

    def test_mark_applied_state_transition(self):
        """User records external submission on official government portal."""
        ws = ApplicationWorkspaceService.get_or_create_workspace(
            profile_id=str(self.profile.id),
            scheme_id=str(self.scheme.id)
        )
        self.assertEqual(ws.status, "in_preparation")

        ws.status = "applied_external"
        ws.save()
        ws.refresh_from_db()
        self.assertEqual(ws.status, "applied_external")


class ApplicationWorkspaceAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username="api_ws_user", password="password123")
        self.client.force_authenticate(user=self.user)

        self.profile = BusinessProfile.objects.create(
            user=self.user,
            business_name="Surat Weaving Mills LLP",
            msme_category="small",
            state="Gujarat"
        )
        self.scheme = Scheme.objects.create(
            scheme_code="CENTRAL-ZED-2025",
            name="ZED Certification Incentive Scheme",
            level="central",
            official_portal_url="https://zed.msme.gov.in"
        )

    def test_api_get_or_create_workspace(self):
        """POST /api/v1/workspaces/get-or-create/ initializes workspace."""
        payload = {
            "business_profile_id": str(self.profile.id),
            "scheme_id": str(self.scheme.id)
        }
        res = self.client.post('/api/v1/workspaces/get-or-create/', payload, format='json')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["scheme_code"], "CENTRAL-ZED-2025")
        self.assertIn("workspace_data", res.data)

    def test_api_mark_applied(self):
        """POST /api/v1/workspaces/<id>/mark-applied/ updates status."""
        ws = ApplicationWorkspaceService.get_or_create_workspace(
            profile_id=str(self.profile.id),
            scheme_id=str(self.scheme.id)
        )
        res = self.client.post(f'/api/v1/workspaces/{ws.id}/mark-applied/', {}, format='json')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["status"], "applied_external")
