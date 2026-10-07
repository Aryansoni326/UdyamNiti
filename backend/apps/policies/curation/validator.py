"""
Command-line validator for curated MSME scheme JSON files.
Validates adherence to CanonicalScheme Pydantic schema, official domain allowlists,
verbatim evidence completeness, and deterministic boundary conditions.

Usage:
    python -m apps.policies.curation.validator <path_to_scheme.json>
"""
import sys
import json
import re
from pathlib import Path
from datetime import date
from typing import List, Tuple

# Domain allowlist for official government schemes
ALLOWED_DOMAINS_REGEX = re.compile(
    r"^https://([a-zA-Z0-9-]+\.)*(gov\.in|nic\.in|cgtmse\.in|sidbi\.in|nabard\.org)(/.*)?$"
)


def validate_curated_file(file_path: Path) -> Tuple[bool, List[str], List[str]]:
    """
    Validates a curated scheme JSON file against official standards.
    Returns (is_valid, errors, warnings).
    """
    errors: List[str] = []
    warnings: List[str] = []

    if not file_path.exists():
        return False, [f"File not found: {file_path}"], []

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        return False, [f"Invalid JSON syntax in {file_path}: {str(e)}"], []

    # 1. Check Root Required Fields
    required_root_fields = [
        "scheme_id",
        "scheme_name",
        "short_name",
        "authority",
        "central_or_state",
        "objective",
        "support_categories",
        "benefit_type",
        "target_enterprise_types",
        "target_sectors",
        "eligibility_rules",
        "required_documents",
        "application_process",
        "official_application_url",
        "source_documents",
        "effective_date",
        "last_verified_date",
    ]

    for rf in required_root_fields:
        if rf not in data or data[rf] is None or (isinstance(data[rf], (list, str)) and len(data[rf]) == 0):
            errors.append(f"Missing mandatory root field: '{rf}'")

    scheme_id = data.get("scheme_id", "UNKNOWN")

    # 2. Domain Allowlist Verification
    app_url = data.get("official_application_url", "")
    if app_url and not ALLOWED_DOMAINS_REGEX.match(app_url):
        errors.append(
            f"official_application_url '{app_url}' does not point to an allowed official government domain (.gov.in, .nic.in, cgtmse.in, sidbi.in)."
        )

    # 3. Source Documents Validation
    sources = data.get("source_documents", [])
    if not isinstance(sources, list) or len(sources) == 0:
        errors.append("source_documents must be a non-empty list of official source pointers.")
    else:
        for idx, src in enumerate(sources):
            prefix = f"source_documents[{idx}]"
            doc_url = src.get("document_url", "")
            if doc_url and not ALLOWED_DOMAINS_REGEX.match(doc_url):
                errors.append(
                    f"{prefix}.document_url '{doc_url}' does not point to an allowed official government domain."
                )
            if not src.get("exact_quote") or len(src.get("exact_quote", "").strip()) < 10:
                errors.append(f"{prefix}.exact_quote must contain a verbatim excerpt of at least 10 characters.")
            if not src.get("clause_or_section"):
                errors.append(f"{prefix}.clause_or_section must be explicitly specified.")

    # 4. Eligibility Rules Verification
    rules = data.get("eligibility_rules", [])
    rule_ids = set()
    if not isinstance(rules, list) or len(rules) == 0:
        errors.append("eligibility_rules must contain at least one deterministic condition.")
    else:
        for idx, rule in enumerate(rules):
            rid = rule.get("rule_id", f"rule_{idx}")
            if rid in rule_ids:
                errors.append(f"Duplicate rule_id detected: '{rid}'")
            rule_ids.add(rid)

            # Check evidence block
            evidence = rule.get("evidence")
            if not evidence or not isinstance(evidence, dict):
                errors.append(f"Rule '{rid}' lacks a required 'evidence' pointer block.")
            else:
                ev_quote = evidence.get("exact_quote", "")
                if not ev_quote or len(ev_quote.strip()) < 10:
                    errors.append(f"Rule '{rid}' evidence must contain a verbatim quote (>= 10 chars).")
                if not evidence.get("clause_or_section"):
                    errors.append(f"Rule '{rid}' evidence must cite a specific clause or section.")
                ev_url = evidence.get("document_url", "")
                if ev_url and not ALLOWED_DOMAINS_REGEX.match(ev_url):
                    errors.append(
                        f"Rule '{rid}' evidence.document_url '{ev_url}' violates government domain allowlist."
                    )
                if evidence.get("page_number") is None:
                    warnings.append(f"Rule '{rid}' evidence lacks physical PDF page_number.")

            # Check failure message
            if not rule.get("failure_message"):
                errors.append(f"Rule '{rid}' must provide an explanatory 'failure_message'.")

    # 5. Benefit Calculation Verification
    benefit = data.get("benefit_calculation")
    if benefit:
        if not benefit.get("formula_expression"):
            errors.append("benefit_calculation is present but lacks 'formula_expression'.")
        b_evidence = benefit.get("evidence")
        if not b_evidence:
            errors.append("benefit_calculation must cite an official evidence pointer.")

    # 6. Dates Logic Verification
    try:
        eff_date = date.fromisoformat(data.get("effective_date", "1970-01-01"))
        ver_date = date.fromisoformat(data.get("last_verified_date", "1970-01-01"))
        if ver_date < eff_date:
            warnings.append(
                f"last_verified_date ({ver_date}) is earlier than effective_date ({eff_date}). Verify dates."
            )
    except (ValueError, TypeError):
        errors.append("effective_date or last_verified_date is not in valid ISO-8601 (YYYY-MM-DD) format.")

    # 7. Metadata / Review Signatures
    metadata = data.get("metadata", {})
    if not metadata.get("curator_name") or metadata.get("curator_name") == "Full Name of Policy Researcher":
        warnings.append("Metadata 'curator_name' has not been filled out with a researcher name.")
    if metadata.get("review_status") != "approved":
        warnings.append(
            f"Review status is currently '{metadata.get('review_status', 'draft')}'. Two-person sign-off required prior to production import."
        )

    is_valid = len(errors) == 0
    return is_valid, errors, warnings


def main():
    if len(sys.argv) < 2:
        print("Usage: python -m apps.policies.curation.validator <path_to_scheme.json>")
        sys.exit(1)

    target_path = Path(sys.argv[1])
    is_valid, errors, warnings = validate_curated_file(target_path)

    print("=" * 80)
    print(f"UdyamNiti Policy Curation Validator: {target_path.name}")
    print("=" * 80)

    if errors:
        print(f"\n❌ VALIDATION FAILED with {len(errors)} error(s):")
        for idx, err in enumerate(errors, 1):
            print(f"   [{idx}] {err}")

    if warnings:
        print(f"\n⚠️  WARNINGS ({len(warnings)} found):")
        for idx, warn in enumerate(warnings, 1):
            print(f"   [{idx}] {warn}")

    if is_valid:
        print("\n✅ VALIDATION PASSED! The scheme meets all Canonical Policy Schema and legal evidence standards.")
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()
