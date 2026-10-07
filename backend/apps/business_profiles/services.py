"""
Business Profile Service.
Handles profile mutations, field-level provenance updates, change history tracking,
snapshot generation, targeted clarifying question generation, and selective re-evaluation triggering.
"""
import logging
from typing import Dict, Any, List, Optional, Tuple
from django.db import transaction
from django.utils import timezone

from .models import (
    BusinessProfile,
    ProfileSnapshot,
    ProfileFieldProvenance,
    ProfileChangeHistory,
    BusinessFact,
    BusinessGoal
)

logger = logging.getLogger(__name__)

# List of high-value attributes that materially affect statutory scheme eligibility
MATERIAL_ELIGIBILITY_FIELDS = {
    'state',
    'district',
    'industry_sector',
    'industry_subsector',
    'msme_category',
    'entity_type',
    'is_manufacturing',
    'is_service',
    'investment_in_plant_machinery_lakhs',
    'annual_turnover_lakhs',
    'total_employees',
    'years_in_operation',
    'has_export_license',
    'has_iso_certification',
    'has_bis_certification',
    'has_gem_registration',
    'is_women_owned',
    'is_sc_st_owned',
    'is_npa',
    'udyam_registration_number',
    'gstin'
}


class BusinessProfileService:
    """
    Comprehensive service for MSME business profiles, field-level provenance,
    reproducible snapshots, and targeted clarifying questions.
    """

    @classmethod
    @transaction.atomic
    def update_profile(
        cls,
        profile: BusinessProfile,
        validated_data: Dict[str, Any],
        provenance_updates: Optional[Dict[str, Dict[str, Any]]] = None,
        user=None,
        change_reason: str = "User profile update",
        trigger_reeval: bool = True
    ) -> Tuple[BusinessProfile, List[ProfileChangeHistory], bool, Optional[ProfileSnapshot]]:
        """
        Updates profile fields, records field-level provenance, logs change history,
        detects material changes, takes a snapshot if material changes occur,
        and triggers selective re-evaluation.
        """
        changes_logged = []
        has_material_changes = False

        # 1. Inspect and apply field changes
        for field, new_val in validated_data.items():
            if not hasattr(profile, field):
                continue
            old_val = getattr(profile, field)

            # Compare values
            if str(old_val) != str(new_val):
                is_mat = field in MATERIAL_ELIGIBILITY_FIELDS
                if is_mat:
                    has_material_changes = True

                setattr(profile, field, new_val)

                # Format old and new values for JSON serialization
                old_val_serializable = float(old_val) if hasattr(old_val, '__float__') else old_val
                new_val_serializable = float(new_val) if hasattr(new_val, '__float__') else new_val

                change = ProfileChangeHistory.objects.create(
                    business_profile=profile,
                    field_name=field,
                    old_value=old_val_serializable,
                    new_value=new_val_serializable,
                    is_material=is_mat,
                    changed_by=user if getattr(user, 'is_authenticated', False) else None,
                    change_reason=change_reason
                )
                changes_logged.append(change)

        profile.save()

        # 2. Update field-level provenances if provided
        if provenance_updates:
            for field_name, prov_info in provenance_updates.items():
                ProfileFieldProvenance.objects.update_or_create(
                    business_profile=profile,
                    field_name=field_name,
                    defaults={
                        'source_type': prov_info.get('source_type', 'self_declared'),
                        'document_reference': prov_info.get('document_reference', ''),
                        'verified': prov_info.get('verified', False),
                        'verified_by': prov_info.get('verified_by', ''),
                        'verification_date': timezone.now() if prov_info.get('verified') else None,
                        'notes': prov_info.get('notes', '')
                    }
                )

        # 3. If material changes occurred, capture snapshot and optionally trigger re-evaluation
        snapshot = None
        if has_material_changes:
            snapshot = profile.create_snapshot(trigger_reason="material_field_change")
            if trigger_reeval:
                cls._trigger_selective_reevaluation(profile)

        return profile, changes_logged, has_material_changes, snapshot

    @classmethod
    def _trigger_selective_reevaluation(cls, profile: BusinessProfile):
        """
        Triggers deterministic eligibility re-evaluation for schemes previously assessed.
        """
        try:
            from apps.eligibility.services import EligibilityEvaluationService
            service = EligibilityEvaluationService()
            service.re_evaluate_profile(profile_id=profile.id)
            logger.info(f"Triggered selective re-evaluation for profile {profile.id}")
        except Exception as e:
            logger.warning(f"Could not trigger automatic re-evaluation for profile {profile.id}: {e}")

    @classmethod
    def get_profile_with_provenance(cls, profile: BusinessProfile) -> Dict[str, Any]:
        """
        Returns full profile data along with field-level provenance metadata.
        """
        provenances = {
            p.field_name: {
                "source_type": p.source_type,
                "document_reference": p.document_reference,
                "verified": p.verified,
                "verified_by": p.verified_by,
                "verification_date": p.verification_date.isoformat() if p.verification_date else None,
                "notes": p.notes
            }
            for p in profile.field_provenances.all()
        }

        # 8-10 high-value attributes overview
        high_value_attributes = {
            "location_state": {
                "value": profile.state,
                "district": profile.district,
                "provenance": provenances.get("state", {"source_type": "self_declared", "verified": False})
            },
            "industry": {
                "sector": profile.industry_sector,
                "subsector": profile.industry_subsector,
                "activity": "Manufacturing" if profile.is_manufacturing else "Service",
                "provenance": provenances.get("industry_sector", {"source_type": "self_declared", "verified": False})
            },
            "enterprise_category": {
                "value": profile.msme_category,
                "entity_type": profile.entity_type,
                "provenance": provenances.get("msme_category", {"source_type": "self_declared", "verified": False})
            },
            "annual_turnover": {
                "amount_lakhs": float(profile.annual_turnover_lakhs) if profile.annual_turnover_lakhs else None,
                "amount_crores": profile.turnover_crores,
                "unit": "INR Lakhs",
                "provenance": provenances.get("annual_turnover_lakhs", {"source_type": "self_declared", "verified": False})
            },
            "investment_in_machinery": {
                "amount_lakhs": float(profile.investment_in_plant_machinery_lakhs) if profile.investment_in_plant_machinery_lakhs else None,
                "amount_crores": profile.investment_crores,
                "unit": "INR Lakhs",
                "provenance": provenances.get("investment_in_plant_machinery_lakhs", {"source_type": "self_declared", "verified": False})
            },
            "employees": {
                "total_count": profile.total_employees,
                "provenance": provenances.get("total_employees", {"source_type": "self_declared", "verified": False})
            },
            "udyam_status": {
                "registered": bool(profile.udyam_registration_number),
                "registration_number": profile.udyam_registration_number,
                "provenance": provenances.get("udyam_registration_number", {
                    "source_type": "official_registry" if profile.udyam_registration_number else "self_declared",
                    "verified": bool(profile.udyam_registration_number)
                })
            },
            "gst_status": {
                "registered": bool(profile.gstin),
                "gstin": profile.gstin,
                "provenance": provenances.get("gstin", {
                    "source_type": "official_registry" if profile.gstin else "self_declared",
                    "verified": bool(profile.gstin)
                })
            },
            "exports": {
                "has_export_license": profile.has_export_license,
                "provenance": provenances.get("has_export_license", {"source_type": "self_declared", "verified": False})
            },
            "certifications": {
                "has_iso": profile.has_iso_certification,
                "has_bis": profile.has_bis_certification,
                "has_gem": profile.has_gem_registration,
                "provenance": provenances.get("has_iso_certification", {"source_type": "self_declared", "verified": False})
            }
        }

        return {
            "profile_id": str(profile.id),
            "business_name": profile.business_name,
            "high_value_attributes": high_value_attributes,
            "field_provenances": provenances,
            "total_snapshots": profile.snapshots.count(),
            "latest_snapshot_version": profile.snapshots.order_by('-snapshot_version').values_list('snapshot_version', flat=True).first() or 0
        }

    @classmethod
    def get_targeted_clarifying_questions(cls, profile: BusinessProfile) -> List[Dict[str, Any]]:
        """
        Generates targeted clarifying questions for missing or self-declared facts
        that have high statutory impact on MSME subsidies (Gujarat + Central).
        Avoids asking for unnecessary sensitive data (e.g. passwords, personal bank balances).
        """
        questions = []

        # 1. Taluka Category in Gujarat (Zones 1, 2, 3 materially impact capital subsidy from 10% to 25%)
        if profile.state and profile.state.lower() == 'gujarat':
            taluka_fact = BusinessFact.objects.filter(business_profile=profile, fact_key='taluka_category').first()
            if not taluka_fact:
                questions.append({
                    "field_key": "taluka_category",
                    "question": "Which Taluka category does your manufacturing plant fall under in Gujarat?",
                    "reason_it_matters": "Under Gujarat MSME Policy 2020-2025, Category 1 (less developed) talukas receive 25% subsidy, while Category 3 receives 10%.",
                    "field_type": "select",
                    "options": [
                        {"value": "Category 1", "label": "Category 1 (Developing Talukas - Up to 25% Capital Subsidy)"},
                        {"value": "Category 2", "label": "Category 2 (Intermediate Talukas - Up to 15% Capital Subsidy)"},
                        {"value": "Category 3", "label": "Category 3 (Developed Urban Talukas - Up to 10% Capital Subsidy)"},
                        {"value": "municipal_corporation", "label": "Municipal Corporation Area (Limited Schemes)"}
                    ]
                })

        # 2. Udyam Registration (Gatekeeper for Central Priority Subsidies)
        if not profile.udyam_registration_number:
            questions.append({
                "field_key": "udyam_registration_number",
                "question": "Do you possess an active Udyam Registration Certificate?",
                "reason_it_matters": "90% of central schemes (CGTMSE, PMEGP, ZED) mandate a valid Udyam Registration Number for verification.",
                "field_type": "text",
                "placeholder": "UDYAM-XX-00-0000000",
                "options": [
                    {"value": "already_registered", "label": "Yes, I have an Udyam Number"},
                    {"value": "not_registered", "label": "No, Not registered yet (Free assistance available)"}
                ]
            })

        # 3. ZED (Zero Defect Zero Effect) Certification Level
        zed_fact = BusinessFact.objects.filter(business_profile=profile, fact_key='zed_certification_level').first()
        if not zed_fact and profile.is_manufacturing:
            questions.append({
                "field_key": "zed_certification_level",
                "question": "Does your unit hold MSME Sustainable (ZED) Certification?",
                "reason_it_matters": "ZED Bronze/Silver/Gold unlocks up to 80% subsidy on certification and preferential interest subvention in state schemes.",
                "field_type": "select",
                "options": [
                    {"value": "gold", "label": "Gold Certified"},
                    {"value": "silver", "label": "Silver Certified"},
                    {"value": "bronze", "label": "Bronze Certified"},
                    {"value": "none", "label": "None / Planning to apply"}
                ]
            })

        # 4. Power Connection / HT vs LT Status
        power_fact = BusinessFact.objects.filter(business_profile=profile, fact_key='power_connection_type').first()
        if not power_fact and profile.is_manufacturing:
            questions.append({
                "field_key": "power_connection_type",
                "question": "What electricity tariff/connection does your unit use (LT or HT)?",
                "reason_it_matters": "Gujarat Power Tariff Subsidy provides ₹1 to ₹2 per unit relief for eligible HT/LT industrial connections.",
                "field_type": "select",
                "options": [
                    {"value": "lt_industrial", "label": "LT (Low Tension) Industrial"},
                    {"value": "ht_industrial", "label": "HT (High Tension) Industrial"},
                    {"value": "commercial", "label": "Commercial Tariff"}
                ]
            })

        # 5. Export Intent / IEC Code
        if not profile.has_export_license:
            questions.append({
                "field_key": "has_export_license",
                "question": "Does your enterprise have an Import-Export Code (IEC) or export turnover?",
                "reason_it_matters": "Enables Market Development Assistance (MDA) for international exhibitions, air freight subsidies, and export certifications.",
                "field_type": "boolean",
                "options": [
                    {"value": True, "label": "Yes, Active IEC / Exporting"},
                    {"value": False, "label": "No, Domestic Only"}
                ]
            })

        return questions
