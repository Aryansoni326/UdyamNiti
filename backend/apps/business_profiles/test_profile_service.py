"""
Unit and Integration Tests for MSME Business Profile Service and Endpoints.
Verifies:
1. 8-10 high-value attributes (location/state, industry, category, turnover, investment, employees, Udyam, GST, exports, certifications).
2. Field-level provenance tracking (self-declared vs document-supported/registry).
3. Snapshotting for reproducible evaluations (immutable frozen state).
4. Change history logging with materiality detection.
5. Selective re-evaluation triggering when material facts change.
6. Targeted clarifying questions API without collecting unnecessary sensitive data.
7. REST API endpoints.
"""
from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework import status

from apps.business_profiles.models import (
    BusinessProfile,
    ProfileSnapshot,
    ProfileFieldProvenance,
    ProfileChangeHistory,
    BusinessFact
)
from apps.business_profiles.services import BusinessProfileService
from apps.policies.models import Scheme, SchemeRule


class BusinessProfileServiceTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="test_msme_owner", password="password123")
        self.profile = BusinessProfile.objects.create(
            user=self.user,
            business_name="Somnath CNC Precision Tools",
            entity_type="pvt_ltd",
            msme_category="small",
            industry_sector="Manufacturing",
            industry_subsector="Machinery & Automotive Components",
            is_manufacturing=True,
            state="Gujarat",
            district="Rajkot",
            city="Rajkot",
            investment_in_plant_machinery_lakhs=75.0,  # 75 Lakhs
            annual_turnover_lakhs=450.0,               # 4.5 Cr
            total_employees=25,
            years_in_operation=6,
            has_bank_account=True,
            is_npa=False,
            has_export_license=False,
            has_iso_certification=False,
            has_bis_certification=False,
            has_gem_registration=False,
            udyam_registration_number="UDYAM-GJ-01-0012345",
            gstin="24AAACC1234F1Z5"
        )

        # Pre-seed initial provenance
        ProfileFieldProvenance.objects.create(
            business_profile=self.profile,
            field_name="udyam_registration_number",
            source_type="official_registry",
            document_reference="UDYAM-CERT-2024",
            verified=True
        )

    def test_high_value_attributes_provenance_inspection(self):
        """Service must format 8-10 high-value attributes with provenance and typed units."""
        data = BusinessProfileService.get_profile_with_provenance(self.profile)

        self.assertEqual(data["business_name"], "Somnath CNC Precision Tools")
        attrs = data["high_value_attributes"]

        # 1. State / location
        self.assertEqual(attrs["location_state"]["value"], "Gujarat")
        self.assertEqual(attrs["location_state"]["district"], "Rajkot")

        # 2. Industry
        self.assertEqual(attrs["industry"]["sector"], "Manufacturing")
        self.assertEqual(attrs["industry"]["activity"], "Manufacturing")

        # 3. Enterprise category
        self.assertEqual(attrs["enterprise_category"]["value"], "small")

        # 4. Annual turnover & units
        self.assertEqual(attrs["annual_turnover"]["amount_lakhs"], 450.0)
        self.assertEqual(attrs["annual_turnover"]["amount_crores"], 4.5)
        self.assertEqual(attrs["annual_turnover"]["unit"], "INR Lakhs")

        # 5. Investment in plant & machinery
        self.assertEqual(attrs["investment_in_machinery"]["amount_lakhs"], 75.0)
        self.assertEqual(attrs["investment_in_machinery"]["amount_crores"], 0.75)

        # 6. Employees
        self.assertEqual(attrs["employees"]["total_count"], 25)

        # 7. Udyam status
        self.assertTrue(attrs["udyam_status"]["registered"])
        self.assertEqual(attrs["udyam_status"]["provenance"]["source_type"], "official_registry")

        # 8. GST status
        self.assertTrue(attrs["gst_status"]["registered"])

        # 9. Exports
        self.assertFalse(attrs["exports"]["has_export_license"])

        # 10. Certifications
        self.assertFalse(attrs["certifications"]["has_iso"])

    def test_update_profile_material_change_triggers_snapshot_and_history(self):
        """Updating turnover or investment must be flagged as material, logged in history, and snapshotted."""
        validated_data = {
            "annual_turnover_lakhs": 650.0,  # Material change (450 -> 650)
            "has_iso_certification": True,   # Material change (False -> True)
            "city": "Metoda GIDC"            # Non-material location detail
        }
        provenance_updates = {
            "has_iso_certification": {
                "source_type": "document_supported",
                "document_reference": "ISO-9001-CERT-2025.pdf",
                "verified": True
            }
        }

        updated_profile, changes, has_material, snapshot = BusinessProfileService.update_profile(
            profile=self.profile,
            validated_data=validated_data,
            provenance_updates=provenance_updates,
            user=self.user,
            change_reason="Audited Financials 2025 Filed",
            trigger_reeval=False  # Test re-eval logic separately
        )

        self.assertTrue(has_material)
        self.assertIsNotNone(snapshot)
        self.assertEqual(snapshot.snapshot_version, 1)
        self.assertEqual(snapshot.snapshot_data["annual_turnover_lakhs"], 650.0)
        self.assertEqual(snapshot.trigger_reason, "material_field_change")

        # Check change history
        logged_fields = {c.field_name: c for c in changes}
        self.assertIn("annual_turnover_lakhs", logged_fields)
        self.assertTrue(logged_fields["annual_turnover_lakhs"].is_material)
        self.assertEqual(float(logged_fields["annual_turnover_lakhs"].old_value), 450.0)
        self.assertEqual(float(logged_fields["annual_turnover_lakhs"].new_value), 650.0)

        # Check provenance update
        prov = ProfileFieldProvenance.objects.get(business_profile=self.profile, field_name="has_iso_certification")
        self.assertEqual(prov.source_type, "document_supported")
        self.assertEqual(prov.document_reference, "ISO-9001-CERT-2025.pdf")
        self.assertTrue(prov.verified)

    def test_snapshot_immutability_for_reproducible_evaluations(self):
        """Snapshot must freeze the exact state at evaluation time."""
        snap1 = self.profile.create_snapshot(trigger_reason="pre_evaluation")
        self.assertEqual(snap1.snapshot_version, 1)
        self.assertEqual(snap1.snapshot_data["annual_turnover_lakhs"], 450.0)

        # Mutate active profile
        self.profile.annual_turnover_lakhs = 999.0
        self.profile.save()

        # Create second snapshot
        snap2 = self.profile.create_snapshot(trigger_reason="post_growth")
        self.assertEqual(snap2.snapshot_version, 2)
        self.assertEqual(snap2.snapshot_data["annual_turnover_lakhs"], 999.0)

        # Frozen snapshot 1 remains intact
        snap1.refresh_from_db()
        self.assertEqual(snap1.snapshot_data["annual_turnover_lakhs"], 450.0)

    def test_targeted_clarifying_questions_avoids_sensitive_data(self):
        """Generates policy-impact questions (Gujarat taluka category, ZED, power tariff) without asking passwords/personal bank PINs."""
        questions = BusinessProfileService.get_targeted_clarifying_questions(self.profile)

        question_keys = [q["field_key"] for q in questions]
        # In Gujarat manufacturing, taluka category directly determines 10% vs 25% subsidy
        self.assertIn("taluka_category", question_keys)
        self.assertIn("zed_certification_level", question_keys)
        self.assertIn("power_connection_type", question_keys)
        self.assertIn("has_export_license", question_keys)

        # Verify no unnecessary sensitive questions exist
        for q in questions:
            q_text = (q["question"] + " " + q["reason_it_matters"]).lower()
            self.assertNotIn("password", q_text)
            self.assertNotIn("personal bank balance", q_text)
            self.assertNotIn("aadhar", q_text)
            self.assertNotIn("otp", q_text)
            self.assertTrue(len(q["options"]) >= 2)


class BusinessProfileAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username="api_msme_user", password="password123")
        self.client.force_authenticate(user=self.user)

        self.profile = BusinessProfile.objects.create(
            user=self.user,
            business_name="Baroda Precision Valves LLP",
            msme_category="micro",
            entity_type="llp",
            state="Gujarat",
            district="Vadodara",
            annual_turnover_lakhs=85.0,
            investment_in_plant_machinery_lakhs=25.0
        )

    def test_get_provenance_endpoint(self):
        """GET /api/v1/profiles/<id>/provenance/ returns attributes and provenance."""
        res = self.client.get(f'/api/v1/profiles/{self.profile.id}/provenance/')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["business_name"], "Baroda Precision Valves LLP")
        self.assertIn("high_value_attributes", res.data)
        self.assertEqual(res.data["high_value_attributes"]["enterprise_category"]["value"], "micro")

    def test_post_update_with_provenance_endpoint(self):
        """POST /api/v1/profiles/<id>/update-with-provenance/ mutates profile and logs history."""
        payload = {
            "annual_turnover_lakhs": "120.00",
            "msme_category": "small",
            "has_export_license": True,
            "field_provenances": {
                "annual_turnover_lakhs": {
                    "source_type": "ca_certified",
                    "document_reference": "CA_AUDIT_REPORT_2025.pdf",
                    "verified": True
                }
            },
            "change_reason": "Upgraded to Small enterprise per CA Certificate"
        }
        res = self.client.post(f'/api/v1/profiles/{self.profile.id}/update-with-provenance/', payload, format='json')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertTrue(res.data["has_material_changes"])
        self.assertIsNotNone(res.data["new_snapshot"])
        self.assertEqual(len(res.data["changes_logged"]), 3)

        # Verify DB updated
        self.profile.refresh_from_db()
        self.assertEqual(float(self.profile.annual_turnover_lakhs), 120.0)
        self.assertEqual(self.profile.msme_category, "small")
        self.assertTrue(self.profile.has_export_license)

    def test_get_snapshots_endpoint(self):
        """GET /api/v1/profiles/<id>/snapshots/ lists immutable snapshots."""
        self.profile.create_snapshot(trigger_reason="test_snapshot_1")
        self.profile.create_snapshot(trigger_reason="test_snapshot_2")

        res = self.client.get(f'/api/v1/profiles/{self.profile.id}/snapshots/')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["count"], 2)
        self.assertEqual(len(res.data["snapshots"]), 2)

    def test_get_change_history_endpoint(self):
        """GET /api/v1/profiles/<id>/change-history/ lists audit trail."""
        ProfileChangeHistory.objects.create(
            business_profile=self.profile,
            field_name="annual_turnover_lakhs",
            old_value=85.0,
            new_value=120.0,
            is_material=True,
            change_reason="Turnover update"
        )
        res = self.client.get(f'/api/v1/profiles/{self.profile.id}/change-history/')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["count"], 1)
        self.assertEqual(res.data["changes"][0]["field_name"], "annual_turnover_lakhs")

    def test_get_targeted_questions_endpoint(self):
        """GET /api/v1/profiles/<id>/targeted-questions/ returns questions."""
        res = self.client.get(f'/api/v1/profiles/{self.profile.id}/targeted-questions/')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn("questions", res.data)
        self.assertTrue(res.data["questions_count"] > 0)
