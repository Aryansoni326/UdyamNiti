"""
Temporal Policy Versioning Service & Diff Engine.
Implements field-level and rule-level policy diffing, atomic version transitions,
and strict anti-rule-mixing evaluation queries.
"""
import logging
import datetime
from typing import Dict, Any, List, Optional, Tuple
from django.db import transaction, models
from django.core.exceptions import ValidationError
from django.utils import timezone

from apps.policies.models import Scheme, SchemeRule
from apps.policies.versioning_models import PolicyVersion

logger = logging.getLogger(__name__)


class PolicyVersioningService:
    """
    Manages statutory version lifecycles, field/rule diffing, and zero-mixing temporal queries.
    """

    @classmethod
    def compare_versions(cls, version_a: PolicyVersion, version_b: PolicyVersion) -> Dict[str, Any]:
        """
        Performs fine-grained field-level and rule-level diffing between two policy versions.
        Detects added, removed, and changed thresholds, prerequisites, and source citations.
        """
        # 1. Metadata Differences
        metadata_diff = {
            "version_a": {
                "tag": version_a.version_tag,
                "effective_from": str(version_a.effective_from),
                "effective_until": str(version_a.effective_until) if version_a.effective_until else "ACTIVE",
                "source_document": version_a.source_document,
                "document_checksum": version_a.document_checksum,
                "clause_or_page": version_a.clause_or_page
            },
            "version_b": {
                "tag": version_b.version_tag,
                "effective_from": str(version_b.effective_from),
                "effective_until": str(version_b.effective_until) if version_b.effective_until else "ACTIVE",
                "source_document": version_b.source_document,
                "document_checksum": version_b.document_checksum,
                "clause_or_page": version_b.clause_or_page
            },
            "checksum_changed": version_a.document_checksum != version_b.document_checksum
        }

        # 2. Rule-Level Comparison
        rules_a = {r.get('rule_id', r.get('rule_name', str(i))): r for i, r in enumerate(version_a.rules_snapshot)}
        rules_b = {r.get('rule_id', r.get('rule_name', str(i))): r for i, r in enumerate(version_b.rules_snapshot)}

        added_rules: List[Dict[str, Any]] = []
        removed_rules: List[Dict[str, Any]] = []
        changed_thresholds: List[Dict[str, Any]] = []
        changed_prerequisites: List[Dict[str, Any]] = []

        # Find Added & Changed Rules
        for r_id, rb in rules_b.items():
            if r_id not in rules_a:
                added_rules.append({
                    "rule_id": r_id,
                    "rule_name": rb.get('rule_name', r_id),
                    "operator": rb.get('operator'),
                    "expected_value": rb.get('expected_value'),
                    "importance": rb.get('importance', 'mandatory'),
                    "source_clause": rb.get('source_clause', '')
                })
            else:
                ra = rules_a[r_id]
                # Check threshold changes
                if ra.get('expected_value') != rb.get('expected_value') or ra.get('operator') != rb.get('operator'):
                    changed_thresholds.append({
                        "rule_id": r_id,
                        "rule_name": rb.get('rule_name', r_id),
                        "field_path": rb.get('field_path', ra.get('field_path')),
                        "previous": {
                            "operator": ra.get('operator'),
                            "expected_value": ra.get('expected_value')
                        },
                        "new": {
                            "operator": rb.get('operator'),
                            "expected_value": rb.get('expected_value')
                        },
                        "statutory_citation": rb.get('source_clause', '')
                    })

                # Check prerequisite / importance changes
                if ra.get('importance') != rb.get('importance'):
                    changed_prerequisites.append({
                        "rule_id": r_id,
                        "rule_name": rb.get('rule_name', r_id),
                        "previous_importance": ra.get('importance'),
                        "new_importance": rb.get('importance'),
                        "explanation": f"Condition shifted from {ra.get('importance')} to {rb.get('importance')}"
                    })

        # Find Removed Rules
        for r_id, ra in rules_a.items():
            if r_id not in rules_b:
                removed_rules.append({
                    "rule_id": r_id,
                    "rule_name": ra.get('rule_name', r_id),
                    "operator": ra.get('operator'),
                    "expected_value": ra.get('expected_value'),
                    "importance": ra.get('importance')
                })

        # 3. Benefits Diff
        benefits_diff = {}
        ben_a = version_a.benefits_snapshot or {}
        ben_b = version_b.benefits_snapshot or {}
        if ben_a != ben_b:
            benefits_diff = {
                "previous_benefit": ben_a,
                "new_benefit": ben_b
            }

        return {
            "scheme_code": version_a.scheme.scheme_code,
            "comparison": f"{version_a.version_tag} -> {version_b.version_tag}",
            "metadata_diff": metadata_diff,
            "added_rules": added_rules,
            "removed_rules": removed_rules,
            "changed_thresholds": changed_thresholds,
            "changed_prerequisites": changed_prerequisites,
            "benefits_diff": benefits_diff,
            "has_material_changes": bool(added_rules or removed_rules or changed_thresholds or changed_prerequisites or benefits_diff)
        }

    @classmethod
    @transaction.atomic
    def publish_version_update(
        cls,
        scheme_code: str,
        new_version_tag: str,
        effective_from: datetime.date,
        new_rules_snapshot: List[Dict[str, Any]],
        change_summary: str,
        source_authority: str,
        source_document: str,
        document_text_or_bytes: Any,
        clause_or_page: str,
        new_benefits_snapshot: Optional[Dict[str, Any]] = None
    ) -> Tuple[PolicyVersion, PolicyVersion]:
        """
        Executes a controlled hackathon demo policy update:
        1. Closes out current active version (sets effective_until = effective_from - 1 day, is_active=False).
        2. Preserves historical version as immutable.
        3. Creates and activates new PolicyVersion with fresh SHA-256 checksum.
        4. Updates active SchemeRule records to match the new version.
        Returns (superseded_version, new_active_version).
        """
        scheme = Scheme.objects.get(scheme_code=scheme_code)

        # 1. Supersede existing active version
        old_active = PolicyVersion.objects.filter(scheme=scheme, is_active=True).first()
        if old_active:
            # Set effective_until to one day before new version starts
            day_before = effective_from - datetime.timedelta(days=1)
            # Temporarily permit updating effective_until and is_active on the historical record
            old_active.effective_until = day_before
            old_active.is_active = False
            # Save bypassing immutability check for closure fields
            super(PolicyVersion, old_active).save(update_fields=['effective_until', 'is_active', 'updated_at'])

        # 2. Compute SHA-256 Checksum
        checksum = PolicyVersion.calculate_checksum(document_text_or_bytes)

        # Determine next sequential version number
        last_version = PolicyVersion.objects.filter(scheme=scheme).order_by('-version_number').first()
        next_num = (last_version.version_number + 1) if last_version else 1

        # 3. Create new active PolicyVersion
        new_version = PolicyVersion.objects.create(
            scheme=scheme,
            version_tag=new_version_tag,
            version_number=next_num,
            effective_from=effective_from,
            effective_until=None,
            source_authority=source_authority,
            source_document=source_document,
            document_checksum=checksum,
            clause_or_page=clause_or_page,
            is_active=True,
            is_immutable=True,
            rules_snapshot=new_rules_snapshot,
            benefits_snapshot=new_benefits_snapshot or {},
            change_summary=change_summary
        )

        # 4. Synchronize live SchemeRule table to mirror new active version
        cls._sync_scheme_rules_to_version(scheme, new_rules_snapshot)

        logger.info(
            f"Published policy update for {scheme_code}: {old_active.version_tag if old_active else 'INIT'} -> {new_version.version_tag}"
        )
        return old_active, new_version

    @classmethod
    def get_rules_for_evaluation(
        cls,
        scheme_code: str,
        as_of_date: Optional[datetime.date] = None
    ) -> Tuple[PolicyVersion, List[Dict[str, Any]]]:
        """
        Temporal query returning strictly the rules of the single effective version at as_of_date.
        INVARIANT: Never mix rules from different effective versions in one evaluation.
        """
        target_date = as_of_date or timezone.now().date()
        scheme = Scheme.objects.get(scheme_code=scheme_code)

        # Find version active as of target_date
        version = PolicyVersion.objects.filter(
            scheme=scheme,
            effective_from__lte=target_date
        ).filter(
            models.Q(effective_until__isnull=True) | models.Q(effective_until__gte=target_date)
        ).order_by('-version_number').first()

        if not version:
            # Fallback to current active version
            version = PolicyVersion.objects.filter(scheme=scheme, is_active=True).first()

        if not version:
            raise ValueError(f"No policy version found for scheme '{scheme_code}' effective as of {target_date}.")

        # Return strictly the frozen rules snapshot of this single version
        return version, version.rules_snapshot

    @classmethod
    def _sync_scheme_rules_to_version(cls, scheme: Scheme, rules_snapshot: List[Dict[str, Any]]):
        """
        Syncs the operational SchemeRule table with a published rules snapshot.
        """
        SchemeRule.objects.filter(scheme=scheme).delete()
        new_rules = []
        for idx, r in enumerate(rules_snapshot):
            new_rules.append(SchemeRule(
                scheme=scheme,
                rule_name=r.get('rule_name', f"Rule_{idx + 1}"),
                field_path=r.get('field_path', 'facts'),
                operator=r.get('operator', 'eq'),
                expected_value=r.get('expected_value'),
                importance=r.get('importance', 'mandatory'),
                source_clause=r.get('source_clause', ''),
                source_document=r.get('source_document', ''),
                source_page=r.get('source_page', ''),
                display_label=r.get('display_label', r.get('rule_name', '')),
                order=idx + 1,
                is_active=True
            ))
        SchemeRule.objects.bulk_create(new_rules)
