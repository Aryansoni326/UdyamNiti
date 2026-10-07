"""
Automated pytest suite for the Official Policy Curation pipeline.
Tests JSON schema validation, Pydantic CanonicalScheme adherence, domain allowlists,
verbatim quote enforcement, and QA checklist standards across all curated golden programs.
"""
import json
import pytest
from pathlib import Path
from apps.policies.schema import CanonicalScheme
from apps.policies.curation.validator import validate_curated_file

CURATION_DIR = Path(__file__).resolve().parent
EXAMPLES_DIR = CURATION_DIR / "examples"


@pytest.mark.unit
class TestCurationPipeline:
    """Tests the curation validator and canonical schema compliance."""

    def test_curation_template_passes_validator(self):
        template_file = CURATION_DIR / "curation_template.json"
        is_valid, errors, _ = validate_curated_file(template_file)
        assert is_valid, f"Template failed validation: {errors}"

    def test_golden_clcss_passes_validator_and_pydantic(self):
        file_path = EXAMPLES_DIR / "example_clcss_central.json"
        is_valid, errors, _ = validate_curated_file(file_path)
        assert is_valid, f"CLCSS failed validation: {errors}"

        with open(file_path, "r", encoding="utf-8") as f:
            raw_data = json.load(f)

        # Validate with CanonicalScheme Pydantic model
        scheme = CanonicalScheme.parse_obj(raw_data)
        assert scheme.scheme_id == "IN-CENTRAL-MSME-CLCSS-2024"
        assert scheme.authority == "Ministry of Micro, Small and Medium Enterprises, Government of India"
        assert len(scheme.eligibility_rules) == 3
        assert scheme.benefit_calculation.maximum_cap_lakhs == 15.0

    def test_golden_gujarat_passes_validator_and_pydantic(self):
        file_path = EXAMPLES_DIR / "example_gujarat_msme_capital.json"
        is_valid, errors, _ = validate_curated_file(file_path)
        assert is_valid, f"Gujarat MSME scheme failed validation: {errors}"

        with open(file_path, "r", encoding="utf-8") as f:
            raw_data = json.load(f)

        scheme = CanonicalScheme.parse_obj(raw_data)
        assert scheme.scheme_id == "IN-GUJARAT-MSME-CAPITAL-2020"
        assert scheme.central_or_state == "state"
        assert scheme.applicable_state == "Gujarat"
        assert scheme.benefit_calculation.base_percentage == 25.0
        assert scheme.benefit_calculation.maximum_cap_lakhs == 25.0
        assert len(scheme.possible_relationships) == 1
        assert scheme.possible_relationships[0].relationship_type.value == "stacks_with"

    def test_golden_cgtmse_passes_validator_and_pydantic(self):
        file_path = EXAMPLES_DIR / "example_cgtmse_credit_guarantee.json"
        is_valid, errors, _ = validate_curated_file(file_path)
        assert is_valid, f"CGTMSE scheme failed validation: {errors}"

        with open(file_path, "r", encoding="utf-8") as f:
            raw_data = json.load(f)

        scheme = CanonicalScheme.parse_obj(raw_data)
        assert scheme.scheme_id == "IN-CENTRAL-CGTMSE-2024"
        assert scheme.benefit_type == "credit_guarantee"
        assert scheme.benefit_calculation.maximum_cap_lakhs == 500.0

    def test_validator_rejects_unallowed_third_party_domain(self, tmp_path):
        """Ensures commercial blog URLs (e.g. cleartax, indiamart) are rejected."""
        bad_data = {
            "scheme_id": "TEST-SCHEME",
            "scheme_name": "Test Scheme",
            "short_name": "TS",
            "authority": "Test Authority",
            "central_or_state": "central",
            "objective": "Test objective",
            "support_categories": ["capital_subsidy"],
            "benefit_type": "capital_subsidy",
            "target_enterprise_types": ["micro"],
            "target_sectors": ["Manufacturing"],
            "eligibility_rules": [
                {
                    "rule_id": "R-01",
                    "rule_name": "Test Rule",
                    "field_path": "business_profile.msme_category",
                    "operator": "eq",
                    "expected_value": "micro",
                    "importance": "mandatory",
                    "display_label": "Micro test",
                    "failure_message": "Failed",
                    "effective_from": "2024-01-01",
                    "evidence": {
                        "document_title": "Blog Summary",
                        "source_tier": "tier_4_portal_faq",
                        "issuing_authority": "Third Party",
                        "notification_or_doc_number": "BLOG-01",
                        "clause_or_section": "Para 1",
                        "exact_quote": "This is a summary from a commercial consulting blog website.",
                        "document_url": "https://cleartax.in/s/msme-schemes",
                        "last_verified_date": "2026-09-30",
                    },
                }
            ],
            "required_documents": ["Document A"],
            "application_process": "Apply online",
            "official_application_url": "https://cleartax.in/apply",
            "source_documents": [
                {
                    "document_title": "Blog Summary",
                    "source_tier": "tier_4_portal_faq",
                    "issuing_authority": "Third Party",
                    "notification_or_doc_number": "BLOG-01",
                    "clause_or_section": "Para 1",
                    "exact_quote": "This is a summary from a commercial consulting blog website.",
                    "document_url": "https://cleartax.in/s/msme-schemes",
                    "last_verified_date": "2026-09-30",
                }
            ],
            "effective_date": "2024-01-01",
            "last_verified_date": "2026-09-30",
        }

        bad_file = tmp_path / "bad_scheme.json"
        with open(bad_file, "w", encoding="utf-8") as f:
            json.dump(bad_data, f)

        is_valid, errors, _ = validate_curated_file(bad_file)
        assert not is_valid
        assert any("official government domain" in err for err in errors)

    def test_validator_rejects_missing_verbatim_quote(self, tmp_path):
        """Ensures rules without verbatim evidence are rejected."""
        no_quote_data = {
            "scheme_id": "TEST-SCHEME-2",
            "scheme_name": "Test Scheme 2",
            "short_name": "TS2",
            "authority": "Ministry of MSME",
            "central_or_state": "central",
            "objective": "Test objective",
            "support_categories": ["capital_subsidy"],
            "benefit_type": "capital_subsidy",
            "target_enterprise_types": ["micro"],
            "target_sectors": ["Manufacturing"],
            "eligibility_rules": [
                {
                    "rule_id": "R-01",
                    "rule_name": "Test Rule",
                    "field_path": "business_profile.msme_category",
                    "operator": "eq",
                    "expected_value": "micro",
                    "importance": "mandatory",
                    "display_label": "Micro test",
                    "failure_message": "Failed",
                    "effective_from": "2024-01-01",
                    "evidence": {
                        "document_title": "Official Guidelines",
                        "source_tier": "tier_2_operational_guidelines",
                        "issuing_authority": "Ministry of MSME",
                        "notification_or_doc_number": "NOTIF-01",
                        "clause_or_section": "Clause 1.1",
                        "exact_quote": "short",  # Too short (< 10 chars)
                        "document_url": "https://msme.gov.in/guidelines.pdf",
                        "last_verified_date": "2026-09-30",
                    },
                }
            ],
            "required_documents": ["Document A"],
            "application_process": "Apply online",
            "official_application_url": "https://msme.gov.in/apply",
            "source_documents": [
                {
                    "document_title": "Official Guidelines",
                    "source_tier": "tier_2_operational_guidelines",
                    "issuing_authority": "Ministry of MSME",
                    "notification_or_doc_number": "NOTIF-01",
                    "clause_or_section": "Clause 1.1",
                    "exact_quote": "Official MSME guidelines for implementation of the program.",
                    "document_url": "https://msme.gov.in/guidelines.pdf",
                    "last_verified_date": "2026-09-30",
                }
            ],
            "effective_date": "2024-01-01",
            "last_verified_date": "2026-09-30",
        }

        no_quote_file = tmp_path / "no_quote.json"
        with open(no_quote_file, "w", encoding="utf-8") as f:
            json.dump(no_quote_data, f)

        is_valid, errors, _ = validate_curated_file(no_quote_file)
        assert not is_valid
        assert any("verbatim quote" in err for err in errors)
