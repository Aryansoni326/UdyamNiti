"""
Unit tests for Document Verification, Checksum Hashing, and Audit Trails.
"""
from django.test import TestCase
from apps.business_profiles.models import BusinessProfile, BusinessFact
from apps.documents.models import BusinessDocument, DocumentAuditLog
from apps.documents.services import DocumentVerificationService


class DocumentVerificationTestCase(TestCase):
    def setUp(self):
        self.profile = BusinessProfile.objects.create(
            business_name="Audit Test Enterprise",
            msme_category="micro",
            entity_type="proprietorship",
            industry_sector="Manufacturing",
            state="Gujarat",
            district="Rajkot",
        )

    def test_udyam_certificate_processing(self):
        """Service should extract verified Udyam number, update profile, and record immutable audit."""
        doc = BusinessDocument.objects.create(
            business_profile=self.profile,
            document_type="udyam_certificate",
            title="Official Udyam Certificate - UDYAM-GJ-01-0012345.pdf",
            verification_status="unverified"
        )

        dummy_bytes = b"PDF-UDYAM-GJ-01-0012345-CONTENT-HASH-TEST"
        result = DocumentVerificationService.process_uploaded_document(
            document=doc,
            raw_content=dummy_bytes
        )

        doc.refresh_from_db()
        self.profile.refresh_from_db()

        self.assertEqual(doc.verification_status, "verified")
        self.assertEqual(len(doc.file_hash), 64)  # Valid SHA-256
        self.assertEqual(doc.extracted_facts.get('udyam_registration_number'), "UDYAM-GJ-01-0012345")
        self.assertEqual(self.profile.udyam_registration_number, "UDYAM-GJ-01-0012345")

        # Verify BusinessFact provenance
        fact = BusinessFact.objects.get(business_profile=self.profile, fact_key="udyam_registration_number")
        self.assertTrue(fact.verified)
        self.assertEqual(fact.source, "document_supported")

        # Verify Audit Log
        audit = DocumentAuditLog.objects.filter(document=doc, action="facts_extracted").first()
        self.assertIsNotNone(audit)
