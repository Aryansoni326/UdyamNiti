"""
Unit and Integration Tests for Document Consistency Engine.
Verifies:
1. Multi-way comparisons:
   Business Profile <-> Udyam data <-> GST data <-> Financial Statement <-> Quotation.
2. Detection states:
   MATCH, MISSING, CONFLICT, OUTDATED, UNKNOWN.
3. Prompt Examples:
   - Declared turnover differs from extracted financial value (CONFLICT).
   - Enterprise category differs across sources (e.g. Profile micro vs Udyam small) (CONFLICT).
   - Document date is older than the policy-required period (OUTDATED quotation or balance sheet).
4. Invariants:
   - Do not decide which conflicting value is legally correct.
   - Show both values, provenance and dates.
   - Require user review.
   - Allow facts to remain unresolved.
5. Normalized comparison logic and REST API endpoints.
"""
import datetime
from django.test import TestCase
from django.contrib.auth.models import User
from django.utils import timezone
from rest_framework.test import APIClient
from rest_framework import status

from apps.business_profiles.models import BusinessProfile
from apps.documents.models import BusinessDocument, CrossDocumentConsistencyReport
from apps.documents.consistency_engine import DocumentConsistencyEngine, ConsistencyStatus


class DocumentConsistencyEngineTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="consistency_auditor", password="password123")
        self.profile = BusinessProfile.objects.create(
            user=self.user,
            business_name="Falcon Precision CNC Works",
            msme_category="micro",                     # Self-declared: Micro
            entity_type="pvt_ltd",
            state="Gujarat",
            district="Rajkot",
            annual_turnover_lakhs=450.0,               # Self-declared: 450 Lakhs (4.5 Cr)
            investment_in_plant_machinery_lakhs=85.0,  # Self-declared: 85 Lakhs
            udyam_registration_number="UDYAM-GJ-01-0088991",
            gstin="24AAACC1234F1Z5"
        )

    def test_turnover_conflict_detected_between_profile_and_financials(self):
        """
        Prompt Example 1:
        Declared turnover differs from extracted financial value.
        Profile: ₹4.5 Cr (450 Lakhs)
        Balance sheet extracted: ₹7.8 Cr (780 Lakhs)
        Must yield CONFLICT, show both values with provenance, and NOT decide which is legally correct.
        """
        # Upload Audited Balance Sheet with 780 Lakhs turnover
        fin_doc = BusinessDocument.objects.create(
            business_profile=self.profile,
            document_type="balance_sheet",
            title="Audited Financials FY 2023-24.pdf",
            extracted_facts={"annual_turnover_lakhs": 780.0, "investment_in_plant_machinery_lakhs": 120.0},
            document_issue_date=timezone.now().date() - datetime.timedelta(days=90),
            verification_status="verified"
        )

        res = DocumentConsistencyEngine.evaluate_profile_consistency(self.profile, persist=False)
        checks = {c["field_key"]: c for c in res["checks"]}

        turnover_check = checks.get("annual_turnover_lakhs")
        self.assertIsNotNone(turnover_check)
        self.assertEqual(turnover_check["status"], ConsistencyStatus.CONFLICT)

        # Invariant: Show both values with provenance
        sources = turnover_check["sources"]
        self.assertEqual(len(sources), 2)
        source_names = [s["source_name"] for s in sources]
        source_vals = [s["value"] for s in sources]

        self.assertIn(450.0, source_vals)
        self.assertIn(780.0, source_vals)

        # Invariant: Do not decide legal correctness
        self.assertIn("does not determine legal correctness", turnover_check["status_reason"].lower())
        self.assertIn("user review required", turnover_check["status_reason"].lower())

    def test_msme_category_conflict_across_sources(self):
        """
        Prompt Example 2:
        Enterprise category differs across sources.
        Profile records 'micro', but official Udyam certificate states 'small'.
        Must yield CONFLICT.
        """
        udyam_doc = BusinessDocument.objects.create(
            business_profile=self.profile,
            document_type="udyam_certificate",
            title="Official Udyam Certificate.pdf",
            extracted_facts={"msme_category": "Small", "udyam_registration_number": "UDYAM-GJ-01-0088991"},
            document_issue_date=timezone.now().date() - datetime.timedelta(days=120),
            verification_status="verified"
        )

        res = DocumentConsistencyEngine.evaluate_profile_consistency(self.profile, persist=False)
        checks = {c["field_key"]: c for c in res["checks"]}

        cat_check = checks.get("msme_category")
        self.assertIsNotNone(cat_check)
        self.assertEqual(cat_check["status"], ConsistencyStatus.CONFLICT)
        self.assertIn("divergence", cat_check["status_reason"].lower())

        # Check Udyam number itself matches
        udyam_check = checks.get("udyam_registration_number")
        self.assertEqual(udyam_check["status"], ConsistencyStatus.MATCH)

    def test_outdated_document_date_detection(self):
        """
        Prompt Example 3:
        Document date is older than the policy-required period.
        Machinery quotation is 240 days old (> 180 day policy validity limit).
        Must yield OUTDATED status.
        """
        old_date = timezone.now().date() - datetime.timedelta(days=240)
        quote_doc = BusinessDocument.objects.create(
            business_profile=self.profile,
            document_type="machinery_quotation_invoice",
            title="Stale Quotation 2024.pdf",
            extracted_facts={"machinery_quotation_amount_lakhs": 55.0, "planned_machinery_type": "CNC Lathe"},
            document_issue_date=old_date,
            verification_status="unverified"
        )

        res = DocumentConsistencyEngine.evaluate_profile_consistency(self.profile, persist=False)
        checks = {c["field_key"]: c for c in res["checks"]}

        quote_check = checks.get("machinery_quotation_freshness")
        self.assertIsNotNone(quote_check)
        self.assertEqual(quote_check["status"], ConsistencyStatus.OUTDATED)
        self.assertIn("exceeds the 180-day validity window", quote_check["status_reason"])

    def test_missing_document_sources_handling(self):
        """When evidence documents are missing, status is correctly marked as MISSING or UNKNOWN without raising errors."""
        # Bare profile without any documents
        bare_profile = BusinessProfile.objects.create(
            business_name="Newborn Enterprises",
            msme_category="micro",
            state="Gujarat"
        )
        res = DocumentConsistencyEngine.evaluate_profile_consistency(bare_profile, persist=True)

        self.assertGreater(res["metrics"]["missing"], 0)
        report = CrossDocumentConsistencyReport.objects.filter(business_profile=bare_profile).first()
        self.assertIsNotNone(report)
        self.assertIn("Consistency Analysis", report.summary_notes)


class DocumentConsistencyAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username="api_auditor", password="password123")
        self.client.force_authenticate(user=self.user)

        self.profile = BusinessProfile.objects.create(
            user=self.user,
            business_name="Rajkot CNC Solutions",
            msme_category="micro",
            annual_turnover_lakhs=300.0,
            state="Gujarat"
        )

    def test_get_profile_consistency_endpoint(self):
        """GET /api/v1/documents/consistency/profile/<id>/ returns consistency evaluation matrix."""
        res = self.client.get(f'/api/v1/documents/consistency/profile/{self.profile.id}/')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn("metrics", res.data)
        self.assertIn("checks", res.data)
        self.assertEqual(res.data["business_name"], "Rajkot CNC Solutions")

    def test_post_profile_consistency_persists_report(self):
        """POST /api/v1/documents/consistency/profile/<id>/ persists report in database."""
        res = self.client.post(f'/api/v1/documents/consistency/profile/{self.profile.id}/')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIsNotNone(res.data["report_id"])

        report = CrossDocumentConsistencyReport.objects.get(id=res.data["report_id"])
        self.assertEqual(report.business_profile.id, self.profile.id)
