"""
Policy Change Detection Pipeline Service.
Performs multidimensional diffing across 7 statutory dimensions:
1. Eligibility Rules
2. Thresholds
3. Dates
4. Benefit Details
5. Prerequisites
6. Required Documents
7. Application Routes
Classifies changes into MATERIAL vs INFORMATIONAL and routes to curator review.
"""
import logging
import datetime
from typing import Dict, Any, List, Optional, Tuple
from django.db import transaction

from apps.policies.models import Scheme
from apps.policy_monitoring.models import (
    PolicyChange,
    ChangeType,
    MaterialityClassification,
    ReviewStatus
)

logger = logging.getLogger(__name__)


class PolicyDiffPipelineService:
    """
    Core engine for detecting statutory changes between policy versions.
    """

    @classmethod
    @transaction.atomic
    def execute_diff_pipeline(
        cls,
        scheme: Scheme,
        old_policy_data: Dict[str, Any],
        new_policy_data: Dict[str, Any],
        evidence_source: str,
        effective_date: Optional[datetime.date] = None,
        confidence_of_extraction: float = 1.0,
        persist: bool = True
    ) -> List[PolicyChange]:
        """
        Executes the 7-dimension diff pipeline between old and new policy payloads.
        Returns a list of created PolicyChange records.
        """
        detected_changes: List[Dict[str, Any]] = []
        eff_date = effective_date or datetime.date.today()

        # -------------------------------------------------------------
        # 1. Diff Eligibility Rules & Thresholds
        # -------------------------------------------------------------
        old_rules = {r.get('rule_id', r.get('rule_name', str(i))): r for i, r in enumerate(old_policy_data.get('rules', []))}
        new_rules = {r.get('rule_id', r.get('rule_name', str(i))): r for i, r in enumerate(new_policy_data.get('rules', []))}

        # Added & Modified Rules
        for r_id, n_rule in new_rules.items():
            if r_id not in old_rules:
                detected_changes.append({
                    "change_type": ChangeType.ELIGIBILITY_RULES,
                    "materiality": MaterialityClassification.MATERIAL,
                    "summary": f"New eligibility rule added: '{n_rule.get('rule_name', r_id)}'.",
                    "old_value": None,
                    "new_value": n_rule,
                    "affected_rule_ids": [r_id],
                    "requires_review": True
                })
            else:
                o_rule = old_rules[r_id]
                # Check for Threshold Changes (Numeric / Currency / Operators)
                if o_rule.get('expected_value') != n_rule.get('expected_value') or o_rule.get('operator') != n_rule.get('operator'):
                    detected_changes.append({
                        "change_type": ChangeType.THRESHOLDS,
                        "materiality": MaterialityClassification.MATERIAL,
                        "summary": (
                            f"Threshold modified for '{n_rule.get('rule_name', r_id)}': "
                            f"{o_rule.get('operator')} {o_rule.get('expected_value')} -> "
                            f"{n_rule.get('operator')} {n_rule.get('expected_value')}."
                        ),
                        "old_value": {"operator": o_rule.get('operator'), "expected_value": o_rule.get('expected_value')},
                        "new_value": {"operator": n_rule.get('operator'), "expected_value": n_rule.get('expected_value')},
                        "affected_rule_ids": [r_id],
                        "requires_review": True
                    })

                # Check for Prerequisite / Importance Changes
                if o_rule.get('importance') != n_rule.get('importance'):
                    detected_changes.append({
                        "change_type": ChangeType.PREREQUISITES,
                        "materiality": MaterialityClassification.MATERIAL,
                        "summary": (
                            f"Rule importance changed for '{n_rule.get('rule_name', r_id)}': "
                            f"shifted from '{o_rule.get('importance')}' to '{n_rule.get('importance')}'."
                        ),
                        "old_value": o_rule.get('importance'),
                        "new_value": n_rule.get('importance'),
                        "affected_rule_ids": [r_id],
                        "requires_review": True
                    })

        # Removed Rules
        for r_id, o_rule in old_rules.items():
            if r_id not in new_rules:
                detected_changes.append({
                    "change_type": ChangeType.ELIGIBILITY_RULES,
                    "materiality": MaterialityClassification.MATERIAL,
                    "summary": f"Eligibility rule removed: '{o_rule.get('rule_name', r_id)}'.",
                    "old_value": o_rule,
                    "new_value": None,
                    "affected_rule_ids": [r_id],
                    "requires_review": True
                })

        # -------------------------------------------------------------
        # 2. Diff Benefit Details
        # -------------------------------------------------------------
        old_cap = old_policy_data.get('max_benefit_amount_lakhs')
        new_cap = new_policy_data.get('max_benefit_amount_lakhs')
        if old_cap != new_cap and new_cap is not None:
            detected_changes.append({
                "change_type": ChangeType.BENEFIT_DETAILS,
                "materiality": MaterialityClassification.MATERIAL,
                "summary": f"Subsidy ceiling revised from ₹{old_cap} Lakhs to ₹{new_cap} Lakhs.",
                "old_value": float(old_cap) if old_cap else None,
                "new_value": float(new_cap),
                "affected_rule_ids": ["statutory_benefit_cap"],
                "requires_review": True
            })

        old_pct = old_policy_data.get('benefit_percentage')
        new_pct = new_policy_data.get('benefit_percentage')
        if old_pct != new_pct and new_pct is not None:
            detected_changes.append({
                "change_type": ChangeType.BENEFIT_DETAILS,
                "materiality": MaterialityClassification.MATERIAL,
                "summary": f"Subsidy percentage adjusted from {old_pct}% to {new_pct}%.",
                "old_value": float(old_pct) if old_pct else None,
                "new_value": float(new_pct),
                "affected_rule_ids": ["statutory_benefit_percentage"],
                "requires_review": True
            })

        # -------------------------------------------------------------
        # 3. Diff Dates (Deadlines, Effective periods)
        # -------------------------------------------------------------
        old_valid = old_policy_data.get('valid_until')
        new_valid = new_policy_data.get('valid_until')
        if old_valid != new_valid and new_valid is not None:
            detected_changes.append({
                "change_type": ChangeType.DATES,
                "materiality": MaterialityClassification.MATERIAL,
                "summary": f"Policy validity deadline extended / modified: {old_valid} -> {new_valid}.",
                "old_value": str(old_valid),
                "new_value": str(new_valid),
                "affected_rule_ids": ["scheme_validity_window"],
                "requires_review": False
            })

        # -------------------------------------------------------------
        # 4. Diff Prerequisites (Certifications, Sector criteria)
        # -------------------------------------------------------------
        old_prereqs = set(old_policy_data.get('prerequisites', []))
        new_prereqs = set(new_policy_data.get('prerequisites', []))
        added_prereqs = list(new_prereqs - old_prereqs)
        removed_prereqs = list(old_prereqs - new_prereqs)

        if added_prereqs:
            detected_changes.append({
                "change_type": ChangeType.PREREQUISITES,
                "materiality": MaterialityClassification.MATERIAL,
                "summary": f"New mandatory prerequisite(s) introduced: {', '.join(added_prereqs)}.",
                "old_value": list(old_prereqs),
                "new_value": list(new_prereqs),
                "affected_rule_ids": ["mandatory_prerequisites"],
                "requires_review": True
            })

        # -------------------------------------------------------------
        # 5. Diff Required Documents
        # -------------------------------------------------------------
        old_docs = set(old_policy_data.get('required_documents', []))
        new_docs = set(new_policy_data.get('required_documents', []))
        if old_docs != new_docs:
            added_docs = list(new_docs - old_docs)
            detected_changes.append({
                "change_type": ChangeType.REQUIRED_DOCUMENTS,
                "materiality": MaterialityClassification.MATERIAL if added_docs else MaterialityClassification.INFORMATIONAL,
                "summary": f"Required statutory documentation updated. Added: {added_docs if added_docs else 'None'}.",
                "old_value": list(old_docs),
                "new_value": list(new_docs),
                "affected_rule_ids": ["documentation_checklist"],
                "requires_review": bool(added_docs)
            })

        # -------------------------------------------------------------
        # 6. Diff Application Route
        # -------------------------------------------------------------
        old_url = old_policy_data.get('official_portal_url')
        new_url = new_policy_data.get('official_portal_url')
        if old_url != new_url and new_url:
            detected_changes.append({
                "change_type": ChangeType.APPLICATION_ROUTE,
                "materiality": MaterialityClassification.INFORMATIONAL,
                "summary": f"Official application portal route updated: {old_url} -> {new_url}.",
                "old_value": old_url,
                "new_value": new_url,
                "affected_rule_ids": ["application_portal_url"],
                "requires_review": False
            })

        # -------------------------------------------------------------
        # Persist or Return Records
        # -------------------------------------------------------------
        created_records: List[PolicyChange] = []

        for chg in detected_changes:
            req_review = chg.get("requires_review", False) or (confidence_of_extraction < 0.95)
            initial_status = ReviewStatus.PENDING_REVIEW if req_review else ReviewStatus.APPROVED_ACTIVE

            if persist:
                rec = PolicyChange.objects.create(
                    scheme=scheme,
                    change_type=chg["change_type"],
                    materiality=chg["materiality"],
                    change_summary=chg["summary"],
                    old_value=chg["old_value"],
                    new_value=chg["new_value"],
                    affected_rule_ids=chg["affected_rule_ids"],
                    effective_date=eff_date,
                    evidence_source=evidence_source,
                    confidence_of_extraction=confidence_of_extraction,
                    requires_human_review=req_review,
                    review_status=initial_status
                )
                created_records.append(rec)
            else:
                created_records.append(PolicyChange(
                    scheme=scheme,
                    change_type=chg["change_type"],
                    materiality=chg["materiality"],
                    change_summary=chg["summary"],
                    old_value=chg["old_value"],
                    new_value=chg["new_value"],
                    affected_rule_ids=chg["affected_rule_ids"],
                    effective_date=eff_date,
                    evidence_source=evidence_source,
                    confidence_of_extraction=confidence_of_extraction,
                    requires_human_review=req_review,
                    review_status=initial_status
                ))

        logger.info(f"Policy diff pipeline completed for {scheme.scheme_code}: {len(created_records)} changes detected.")
        return created_records
