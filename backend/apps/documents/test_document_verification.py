"""
Unit and Integration Tests for Optional Document Verification Workflow.
Verifies:
1. Document ingest & text extraction across initial document types:
   - Udyam certificate
   - GST-related document (GSTR-3B / REG-06)
   - Financial statement / summary (Balance Sheet / P&L)
   - Machinery quotation / commercial invoice
2. Invariant: Source document, page, and evidence snippet are preserved.
3. Invariant: NEVER overwrite profile silently (proposals waiting for user review).
4. Invariant: Show extracted value vs current value.
5. Invariant: Mark extraction uncertainty (confidence score).
6. Invariant: Report conflicts instead of deciding legal correctness.
7. User approves updates -> accepted facts become document_supported on profile with provenance.
8. Rejected facts leave profile un-mutated.
9. Secure file handling and prototype deletion/retention controls.
10. REST API endpoints.
"""
from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework import status

from apps.business_profiles.models import (
    BusinessProfile,
    ProfileFieldProvenance,
    ProfileSnapshot
)
from apps.documents.models import BusinessDocument, DocumentFactProposal, DocumentAuditLog
from apps.documents.services import DocumentVerificationService


class DocumentVerificationWorkflowTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="doc_verifier", password="password123")
        self.profile = BusinessProfile.objects.create(
            user=self.user,
            business_name="Shree Ram Precision Engineering",
            msme_category="micro",
            entity_type="proprietorship",
            industry_sector="Manufacturing",
            state="Gujarat",
            district="Surat",
            annual_turnover_lakhs=45.0,                         # Current self-declared: ₹45 Lakhs
            investment_in_plant_machinery_lakhs=18.0,           # Current self-declared: ₹18 Lakhs
            udyam_registration_number="",                       # Self-declared: None
            gstin="24AAACC1234F1Z5"
        )

    def test_udyam_certificate_proposal_and_user_approval_flow(self):
        """Udyam upload extracts number & category -> proposals created -> user approves -> applied to profile."""
        doc = BusinessDocument.objects.create(
            business_profile=self.profile,
            document_type="udyam_certificate",
            title="Official Udyam Registration Certificate.pdf",
            verification_status="unverified"
        )

        udyam_text = (
            "MINISTRY OF MICRO, SMALL & MEDIUM ENTERPRISES\n"
            "UDYAM REGISTRATION CERTIFICATE\n"
            "UDYAM REGISTRATION NUMBER: UDYAM-GJ-01-0098765\n"
            "NAME OF ENTERPRISE: SHREE RAM PRECISION ENGINEERING\n"
            "TYPE OF ENTERPRISE: Small\n"
            "MAJOR ACTIVITY: Manufacturing\n"
            "DATE OF INCORPORATION: 15/04/2019\n"
            "State: Gujarat   District: Surat\n"
        )

        result = DocumentVerificationService.process_uploaded_document(
            document=doc,
            raw_content=udyam_text.encode('utf-8'),
            performed_by=self.user
        )

        self.assertEqual(result["status"], "proposals_generated")
        doc.refresh_from_db()
        self.assertEqual(doc.verification_status, "unverified")

        # Invariant 2: NEVER overwrite profile silently before user review
        self.profile.refresh_from_db()
        self.assertEqual(self.profile.udyam_registration_number, "")  # Still empty!

        # Invariant 3 & 4: Proposals show extracted vs current value & confidence
        proposals = DocumentFactProposal.objects.filter(document=doc)
        prop_dict = {p.fact_key: p for p in proposals}

        self.assertIn("udyam_registration_number", prop_dict)
        udyam_prop = prop_dict["udyam_registration_number"]
        self.assertEqual(udyam_prop.current_value, "")
        self.assertEqual(udyam_prop.extracted_value, "UDYAM-GJ-01-0098765")
        self.assertEqual(udyam_prop.source_page, 1)
        self.assertIn("UDYAM-GJ-01-0098765", udyam_prop.evidence_snippet)
        self.assertGreaterEqual(udyam_prop.confidence_score, 0.90)

        # Category proposal has conflict (Current: micro, Extracted: small)
        self.assertIn("msme_category", prop_dict)
        cat_prop = prop_dict["msme_category"]
        self.assertEqual(cat_prop.current_value, "micro")
        self.assertEqual(cat_prop.extracted_value, "small")
        self.assertTrue(cat_prop.has_conflict)
        self.assertIn("Discrepancy noted", cat_prop.conflict_notes)

        # Step 5: User reviews and approves Udyam number & Category update
        decisions = [
            {"proposal_id": str(udyam_prop.id), "action": "accept"},
            {"proposal_id": str(cat_prop.id), "action": "accept"}
        ]
        review_res = DocumentVerificationService.apply_user_review_decisions(
            document=doc,
            decisions=decisions,
            user=self.user
        )
        self.assertEqual(review_res["accepted_facts_count"], 2)

        # Profile is now updated and provenance is document_supported
        self.profile.refresh_from_db()
        self.assertEqual(self.profile.udyam_registration_number, "UDYAM-GJ-01-0098765")
        self.assertEqual(self.profile.msme_category, "small")

        prov = ProfileFieldProvenance.objects.get(business_profile=self.profile, field_name="udyam_registration_number")
        self.assertEqual(prov.source_type, "document_supported")
        self.assertTrue(prov.verified)

    def test_rejection_leaves_profile_unaltered(self):
        """If user rejects an extracted fact proposal, the profile remains untouched."""
        doc = BusinessDocument.objects.create(
            business_profile=self.profile,
            document_type="balance_sheet",
            title="FY2024 Audited Balance Sheet.pdf"
        )
        bs_text = (
            "Audited Financial Statement 2023-2024\n"
            "Revenue from operations: INR 8,50,00,000\n"  # 850 Lakhs
            "Plant and Machinery Gross Block: INR 3,20,00,000\n"  # 320 Lakhs
        )
        DocumentVerificationService.process_uploaded_document(
            document=doc,
            raw_content=bs_text.encode('utf-8')
        )

        turnover_prop = DocumentFactProposal.objects.get(document=doc, fact_key="annual_turnover_lakhs")
        self.assertEqual(turnover_prop.current_value, 45.0)
        self.assertEqual(turnover_prop.extracted_value, 850.0)

        # User rejects the update (e.g. statement belongs to sister company)
        decisions = [{"proposal_id": str(turnover_prop.id), "action": "reject"}]
        DocumentVerificationService.apply_user_review_decisions(
            document=doc,
            decisions=decisions,
            user=self.user
        )

        turnover_prop.refresh_from_db()
        self.assertEqual(turnover_prop.status, "rejected")

        # Invariant: Self-declared turnover retained
        self.profile.refresh_from_db()
        self.assertEqual(float(self.profile.annual_turnover_lakhs), 45.0)

    def test_machinery_quotation_extraction(self):
        """Machinery quotation extracts proposed machine equipment and proforma cost."""
        doc = BusinessDocument.objects.create(
            business_profile=self.profile,
            document_type="machinery_quotation_invoice",
            title="Quotation - Jyoti CNC VMC Machine.pdf"
        )
        quote_text = (
            "PROFORMA INVOICE / QUOTATION\n"
            "Supplier: Jyoti CNC Automation Ltd, Rajkot\n"
            "Item: CNC 5-Axis Milling Machine Model RX-200\n"
            "Grand Total: Rs. 65,00,000\n"  # 65 Lakhs
        )
        res = DocumentVerificationService.process_uploaded_document(
            document=doc,
            raw_content=quote_text.encode('utf-8')
        )

        facts = doc.extracted_facts
        self.assertEqual(facts.get("machinery_quotation_amount_lakhs"), 65.0)
        self.assertIn("CNC", facts.get("planned_machinery_type", ""))

    def test_secure_deletion_and_retention(self):
        """Secure deletion purges document and extraction proposals, preserving cryptographic audit."""
        doc = BusinessDocument.objects.create(
            business_profile=self.profile,
            document_type="gstin_certificate",
            title="Confidential GST Certificate.pdf",
            file_hash="e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
        )
        doc_id = str(doc.id)

        del_res = DocumentVerificationService.delete_document_secure(
            document=doc,
            user=self.user,
            reason="GDPR / DPDP MSME Data Purge Request"
        )

        self.assertEqual(del_res["status"], "deleted")
        self.assertFalse(BusinessDocument.objects.filter(id=doc_id).exists())

        # Audit log must remain recorded
        audit = DocumentAuditLog.objects.filter(action="deleted").first()
        self.assertIsNotNone(audit)
        self.assertEqual(audit.details["deleted_document_id"], doc_id)


class DocumentVerificationAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username="api_user", password="password123")
        self.client.force_authenticate(user=self.user)

        self.profile = BusinessProfile.objects.create(
            user=self.user,
            business_name="Ahmedabad Polymers Pvt Ltd",
            msme_category="small",
            state="Gujarat",
            annual_turnover_lakhs=120.0
        )
        self.doc = BusinessDocument.objects.create(
            business_profile=self.profile,
            document_type="udyam_certificate",
            title="Udyam Certificate.pdf"
        )
        self.proposal = DocumentFactProposal.objects.create(
            document=self.doc,
            business_profile=self.profile,
            fact_key="udyam_registration_number",
            current_value="",
            extracted_value="UDYAM-GJ-01-0055443",
            confidence_score=0.98
        )

    def test_api_list_proposals(self):
        """GET /api/v1/documents/<id>/proposals/ returns proposals."""
        res = self.client.get(f'/api/v1/documents/{self.doc.id}/proposals/')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["proposals_count"], 1)
        self.assertEqual(res.data["proposals"][0]["fact_key"], "udyam_registration_number")

    def test_api_review_proposals_accept(self):
        """POST /api/v1/documents/<id>/review-proposals/ accepts fact and mutates profile."""
        payload = {
            "decisions": [
                {"proposal_id": str(self.proposal.id), "action": "accept"}
            ]
        }
        res = self.client.post(f'/api/v1/documents/{self.doc.id}/review-proposals/', payload, format='json')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["accepted_facts_count"], 1)

        self.profile.refresh_from_db()
        self.assertEqual(self.profile.udyam_registration_number, "UDYAM-GJ-01-0055443")

    def test_api_secure_delete(self):
        """POST /api/v1/documents/<id>/secure-delete/ purges document."""
        res = self.client.post(f'/api/v1/documents/{self.doc.id}/secure-delete/', {"reason": "User cleanup"}, format='json')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertFalse(BusinessDocument.objects.filter(id=self.doc.id).exists())
