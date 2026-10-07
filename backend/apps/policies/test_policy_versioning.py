"""
Unit and Integration Tests for Temporal Policy Versioning.
Verifies:
1. Preservation of version, effective dates, source, document, clause/page, last_verified, document checksum.
2. Immutability constraints: historical versions cannot be tampered with in-place.
3. Constraint: Exactly one active version per scheme.
4. Field-level & Rule-level diffing: detecting added, removed, changed thresholds and prerequisites.
5. Controlled hackathon demo update workflow.
6. Zero-mixing invariant: evaluating as of a given date never mixes rules across versions.
7. REST API endpoints.
"""
import datetime
from django.test import TestCase
from django.core.exceptions import ValidationError
from rest_framework.test import APIClient
from rest_framework import status

from apps.policies.models import Scheme, SchemeRule
from apps.policies.versioning_models import PolicyVersion
from apps.policies.versioning_service import PolicyVersioningService


class PolicyVersioningModelTests(TestCase):
    def setUp(self):
        self.scheme = Scheme.objects.create(
            scheme_code="GJ-CAPITAL-2025",
            name="Gujarat MSME Capital Subsidy Scheme",
            level="state_gujarat",
            support_type="capital_subsidy",
            status="active"
        )
        self.doc_text = "Official Gazette Notification No. SSI/102020/MSME-Incentive/W"
        self.checksum = PolicyVersion.calculate_checksum(self.doc_text)

        self.v1 = PolicyVersion.objects.create(
            scheme=self.scheme,
            version_tag="v2020.1",
            version_number=1,
            effective_from=datetime.date(2020, 8, 7),
            effective_until=datetime.date(2025, 3, 31),
            source_authority="Industries Commissionerate, Govt of Gujarat",
            source_document="Gujarat Industrial Policy 2020 Resolution",
            document_checksum=self.checksum,
            clause_or_page="Clauses 4.1-4.8, pp. 10-14",
            is_active=False,
            is_immutable=True,
            rules_snapshot=[
                {
                    "rule_id": "max_investment",
                    "rule_name": "Maximum Investment Cap",
                    "field_path": "investment_in_plant_machinery_lakhs",
                    "operator": "lte",
                    "expected_value": 1000.0,
                    "importance": "mandatory"
                },
                {
                    "rule_id": "max_subsidy_cap",
                    "rule_name": "Maximum Subsidy Ceiling",
                    "field_path": "subsidy_ceiling",
                    "operator": "lte",
                    "expected_value": 25.0,
                    "importance": "mandatory"
                }
            ],
            change_summary="Initial Gujarat Industrial Policy 2020 baseline."
        )

    def test_single_active_version_constraint(self):
        """Only one policy version may be active per scheme at any given time."""
        # Create first active version
        v_active_1 = PolicyVersion.objects.create(
            scheme=self.scheme,
            version_tag="v2025.1",
            version_number=2,
            effective_from=datetime.date(2025, 4, 1),
            effective_until=None,
            source_authority="Govt of Gujarat",
            source_document="Gujarat Industrial Policy 2025 Resolution",
            document_checksum="abc123hash",
            clause_or_page="Clauses 5.1-5.5",
            is_active=True,
            is_immutable=True,
            rules_snapshot=[],
            change_summary="2025 Policy update"
        )
        self.assertTrue(v_active_1.is_active)

        # Attempting to activate a second version for the same scheme must fail validation
        v_active_2 = PolicyVersion(
            scheme=self.scheme,
            version_tag="v2025.2",
            version_number=3,
            effective_from=datetime.date(2025, 9, 1),
            effective_until=None,
            source_authority="Govt of Gujarat",
            source_document="Gujarat Industrial Amendment Resolution",
            document_checksum="xyz789hash",
            clause_or_page="Clause 5.1",
            is_active=True,
            is_immutable=True,
            rules_snapshot=[],
            change_summary="Conflicting active version"
        )

        with self.assertRaises(ValidationError) as ctx:
            v_active_2.save()
        self.assertIn("already has an active policy version", str(ctx.exception))

    def test_immutable_version_tamper_protection(self):
        """Immutable historical versions cannot be modified in-place."""
        self.v1.rules_snapshot = [{"tampered": "rule"}]
        with self.assertRaises(ValidationError) as ctx:
            self.v1.save()
        self.assertIn("is immutable. Rules snapshot cannot be altered", str(ctx.exception))

    def test_effective_date_ordering_validation(self):
        """effective_from cannot be after effective_until."""
        bad_version = PolicyVersion(
            scheme=self.scheme,
            version_tag="v_bad_dates",
            version_number=99,
            effective_from=datetime.date(2025, 5, 1),
            effective_until=datetime.date(2025, 4, 1),  # Earlier than from
            source_authority="Govt of Gujarat",
            source_document="Resolution",
            document_checksum="hash",
            clause_or_page="p. 1",
            rules_snapshot=[],
            change_summary="Bad dates"
        )
        with self.assertRaises(ValidationError) as ctx:
            bad_version.save()
        self.assertIn("effective_from", str(ctx.exception))


class PolicyVersioningServiceTests(TestCase):
    def setUp(self):
        self.scheme = Scheme.objects.create(
            scheme_code="GJ-CAPITAL-2025",
            name="Gujarat MSME Capital Subsidy Scheme",
            level="state_gujarat",
            support_type="capital_subsidy",
            status="active"
        )

        # Version 1 (2020 Baseline)
        self.v1 = PolicyVersion.objects.create(
            scheme=self.scheme,
            version_tag="v2020.1",
            version_number=1,
            effective_from=datetime.date(2020, 8, 7),
            effective_until=datetime.date(2025, 3, 31),
            source_authority="Govt of Gujarat",
            source_document="2020 Resolution",
            document_checksum="checksum_2020_hash",
            clause_or_page="Clauses 4.1-4.8",
            is_active=False,
            is_immutable=True,
            rules_snapshot=[
                {
                    "rule_id": "rule_max_subsidy",
                    "rule_name": "Maximum Subsidy Cap",
                    "field_path": "max_benefit_lakhs",
                    "operator": "lte",
                    "expected_value": 25.0,
                    "importance": "mandatory",
                    "source_clause": "Clause 4.3"
                },
                {
                    "rule_id": "rule_old_compliance",
                    "rule_name": "Legacy Environmental Clearance",
                    "field_path": "legacy_audit",
                    "operator": "eq",
                    "expected_value": True,
                    "importance": "preferred"
                }
            ],
            benefits_snapshot={"max_subsidy_lakhs": 25.0, "percentage": 20.0},
            change_summary="2020 Policy Baseline"
        )

        # Version 2 (2025 Overhaul)
        self.v2 = PolicyVersion.objects.create(
            scheme=self.scheme,
            version_tag="v2025.1",
            version_number=2,
            effective_from=datetime.date(2025, 4, 1),
            effective_until=None,
            source_authority="Govt of Gujarat",
            source_document="2025 Gazette Resolution",
            document_checksum="checksum_2025_hash",
            clause_or_page="Clauses 5.1-5.9",
            is_active=True,
            is_immutable=True,
            rules_snapshot=[
                {
                    "rule_id": "rule_max_subsidy",
                    "rule_name": "Maximum Subsidy Cap",
                    "field_path": "max_benefit_lakhs",
                    "operator": "lte",
                    "expected_value": 35.0,  # Increased from 25.0 to 35.0
                    "importance": "mandatory",
                    "source_clause": "Clause 5.2"
                },
                {
                    "rule_id": "rule_zed_bronze_required",  # Newly added rule
                    "rule_name": "ZED Quality Certification",
                    "field_path": "has_zed_certification",
                    "operator": "eq",
                    "expected_value": True,
                    "importance": "preferred",
                    "source_clause": "Clause 5.6"
                }
            ],
            benefits_snapshot={"max_subsidy_lakhs": 35.0, "percentage": 25.0},
            change_summary="2025 Policy Enhancement: Subsidy cap raised to ₹35 Lakhs."
        )

    def test_compare_versions_detects_changes(self):
        """compare_versions detects added rules, removed rules, changed thresholds, and benefit diffs."""
        diff = PolicyVersioningService.compare_versions(self.v1, self.v2)

        self.assertTrue(diff["has_material_changes"])
        self.assertTrue(diff["metadata_diff"]["checksum_changed"])

        # Check added rule (ZED)
        added_ids = [r["rule_id"] for r in diff["added_rules"]]
        self.assertIn("rule_zed_bronze_required", added_ids)

        # Check removed rule (legacy compliance)
        removed_ids = [r["rule_id"] for r in diff["removed_rules"]]
        self.assertIn("rule_old_compliance", removed_ids)

        # Check changed threshold (25.0 -> 35.0)
        self.assertEqual(len(diff["changed_thresholds"]), 1)
        th = diff["changed_thresholds"][0]
        self.assertEqual(th["rule_id"], "rule_max_subsidy")
        self.assertEqual(th["previous"]["expected_value"], 25.0)
        self.assertEqual(th["new"]["expected_value"], 35.0)

        # Check benefits diff
        self.assertIn("previous_benefit", diff["benefits_diff"])
        self.assertIn("new_benefit", diff["benefits_diff"])

    def test_zero_rule_mixing_invariant(self):
        """Querying rules as of 2022 strictly returns 2020 rules; querying as of 2026 strictly returns 2025 rules."""
        # 1. Evaluate as of 2022 (should return v1 rules with ₹25L cap)
        v_2022, rules_2022 = PolicyVersioningService.get_rules_for_evaluation(
            scheme_code="GJ-CAPITAL-2025",
            as_of_date=datetime.date(2022, 5, 1)
        )
        self.assertEqual(v_2022.version_tag, "v2020.1")
        cap_rule_2022 = next(r for r in rules_2022 if r["rule_id"] == "rule_max_subsidy")
        self.assertEqual(cap_rule_2022["expected_value"], 25.0)
        # ZED rule must NOT exist in 2022 evaluation context
        self.assertFalse(any(r["rule_id"] == "rule_zed_bronze_required" for r in rules_2022))

        # 2. Evaluate as of 2026 (should return v2 rules with ₹35L cap)
        v_2026, rules_2026 = PolicyVersioningService.get_rules_for_evaluation(
            scheme_code="GJ-CAPITAL-2025",
            as_of_date=datetime.date(2026, 6, 1)
        )
        self.assertEqual(v_2026.version_tag, "v2025.1")
        cap_rule_2026 = next(r for r in rules_2026 if r["rule_id"] == "rule_max_subsidy")
        self.assertEqual(cap_rule_2026["expected_value"], 35.0)
        # Legacy rule must NOT exist in 2026 evaluation context
        self.assertFalse(any(r["rule_id"] == "rule_old_compliance" for r in rules_2026))

    def test_controlled_hackathon_demo_update(self):
        """publish_version_update supersedes active version and activates new version atomically."""
        new_rules = [
            {
                "rule_id": "rule_max_subsidy",
                "rule_name": "Maximum Subsidy Cap",
                "field_path": "max_benefit_lakhs",
                "operator": "lte",
                "expected_value": 50.0,  # Demo update: increased to 50L
                "importance": "mandatory"
            }
        ]

        old_v, new_v = PolicyVersioningService.publish_version_update(
            scheme_code="GJ-CAPITAL-2025",
            new_version_tag="v2025.2-demo",
            effective_from=datetime.date(2026, 1, 1),
            new_rules_snapshot=new_rules,
            change_summary="Hackathon demo: Enhanced subsidy cap to ₹50 Lakhs.",
            source_authority="Industries Department",
            source_document="Demo Gazette Amendment 2026",
            document_text_or_bytes="Special Demo Gazette Content 2026",
            clause_or_page="Clause 1.1",
            new_benefits_snapshot={"max_subsidy_lakhs": 50.0}
        )

        # Old active version must now be superseded and inactive
        self.assertEqual(old_v.version_tag, "v2025.1")
        self.assertFalse(old_v.is_active)
        self.assertEqual(old_v.effective_until, datetime.date(2025, 12, 31))

        # New version must be active
        self.assertEqual(new_v.version_tag, "v2025.2-demo")
        self.assertTrue(new_v.is_active)
        self.assertIsNone(new_v.effective_until)
        self.assertTrue(len(new_v.document_checksum) == 64)

        # Live SchemeRule table must now reflect the new active version
        live_rules = SchemeRule.objects.filter(scheme=self.scheme)
        self.assertEqual(live_rules.count(), 1)
        self.assertEqual(live_rules.first().expected_value, 50.0)


class PolicyVersioningAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.scheme = Scheme.objects.create(
            scheme_code="GJ-CAPITAL-2025",
            name="Gujarat MSME Capital Subsidy",
            level="state_gujarat",
            support_type="capital_subsidy"
        )
        self.v1 = PolicyVersion.objects.create(
            scheme=self.scheme,
            version_tag="v2020.1",
            version_number=1,
            effective_from=datetime.date(2020, 1, 1),
            effective_until=datetime.date(2024, 12, 31),
            source_authority="Govt of Gujarat",
            source_document="Resolution 2020",
            document_checksum="hash2020",
            clause_or_page="pp. 1-5",
            is_active=False,
            rules_snapshot=[{"rule_id": "cap", "expected_value": 25.0}],
            change_summary="V1"
        )
        self.v2 = PolicyVersion.objects.create(
            scheme=self.scheme,
            version_tag="v2025.1",
            version_number=2,
            effective_from=datetime.date(2025, 1, 1),
            effective_until=None,
            source_authority="Govt of Gujarat",
            source_document="Resolution 2025",
            document_checksum="hash2025",
            clause_or_page="pp. 1-8",
            is_active=True,
            rules_snapshot=[{"rule_id": "cap", "expected_value": 35.0}],
            change_summary="V2"
        )

    def test_api_list_versions(self):
        """GET /api/v1/policies/versions/?scheme_code=... returns list of versions with checksums."""
        res = self.client.get(f'/api/v1/policies/versions/?scheme_code={self.scheme.scheme_code}')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 2)
        self.assertEqual(res.data[0]["version_tag"], "v2025.1")
        self.assertTrue(res.data[0]["is_active"])
        self.assertEqual(res.data[1]["version_tag"], "v2020.1")
        self.assertFalse(res.data[1]["is_active"])

    def test_api_compare_versions(self):
        """GET /api/v1/policies/versions/compare/?scheme_code=...&v1=...&v2=... returns diff."""
        url = f'/api/v1/policies/versions/compare/?scheme_code={self.scheme.scheme_code}&v1=v2020.1&v2=v2025.1'
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn("changed_thresholds", res.data)
        self.assertEqual(len(res.data["changed_thresholds"]), 1)
        self.assertEqual(res.data["changed_thresholds"][0]["new"]["expected_value"], 35.0)

    def test_api_demo_update(self):
        """POST /api/v1/policies/versions/demo-update/ triggers controlled update."""
        payload = {
            "scheme_code": self.scheme.scheme_code,
            "new_version_tag": "v2026.1-hackathon",
            "effective_from": "2026-03-01",
            "new_rules_snapshot": [{"rule_id": "cap", "expected_value": 40.0}],
            "change_summary": "Hackathon Demo Update",
            "document_text": "Live Demo Gazette"
        }
        res = self.client.post('/api/v1/policies/versions/demo-update/', payload, format='json')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["new_active_version"], "v2026.1-hackathon")
        self.assertEqual(res.data["superseded_version"], "v2025.1")
        self.assertTrue(len(res.data["document_checksum"]) == 64)
