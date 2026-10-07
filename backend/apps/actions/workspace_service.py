"""
Application Workspace Service.
Aggregates and synchronizes the application preparation workspace for a selected scheme opportunity.
Calculates readiness metrics, checks known vs unknown conditions, maps required documents
against uploaded verified documents, extracts required form fields, and exposes official government route.

Invariants:
- Never automate government submission, OTP, CAPTCHA, declarations, or final departmental approval.
- Expose clear "Continue to official government portal" action.
"""
import logging
from typing import Dict, Any, List, Optional
from django.db import transaction
from django.utils import timezone

from .models import ApplicationPreparationWorkspace, ActionTask, CompletionStatus
from apps.business_profiles.models import BusinessProfile, BusinessFact
from apps.policies.models import Scheme, SchemeRule
from apps.documents.models import BusinessDocument
from apps.eligibility.engine import RuleEngine

logger = logging.getLogger(__name__)

# Standard statutory portal mappings for Gujarat and Central schemes
DEFAULT_OFFICIAL_PORTALS = {
    'state_gujarat': {
        'portal_name': 'Investor Facilitation Portal (IFP) - Govt of Gujarat',
        'portal_url': 'https://ifp.gujarat.gov.in',
        'mode': 'Online State Single Window System'
    },
    'central': {
        'portal_name': 'Champions Portal / MSME Samadhaan & Udyam Portal',
        'portal_url': 'https://champions.gov.in',
        'mode': 'National MSME Single Window Portal'
    },
    'cgtmse': {
        'portal_name': 'CGTMSE Member Lending Institution (MLI) Portal',
        'portal_url': 'https://www.cgtmse.in',
        'mode': 'Scheduled Commercial Bank / NBFC Branch Processing'
    },
    'pmegp': {
        'portal_name': 'KVIC PMEGP e-Portal',
        'portal_url': 'https://www.kviconline.gov.in/pmegpeportal/',
        'mode': 'Online e-Portal with Aadhaar OTP Authentication'
    }
}


class ApplicationWorkspaceService:
    """
    Builds and maintains the application-preparation workspace for a selected opportunity.
    """

    @classmethod
    @transaction.atomic
    def get_or_create_workspace(
        cls,
        profile_id: str,
        scheme_id: str,
        strategy_id: Optional[str] = None
    ) -> ApplicationPreparationWorkspace:
        """
        Creates or updates a preparation workspace for the (profile, scheme) pair.
        """
        profile = BusinessProfile.objects.get(pk=profile_id)
        scheme = Scheme.objects.get(pk=scheme_id)

        workspace, created = ApplicationPreparationWorkspace.objects.get_or_create(
            business_profile=profile,
            scheme=scheme,
            defaults={
                'official_portal_url': cls._resolve_portal_url(scheme),
                'official_portal_name': cls._resolve_portal_name(scheme),
                'application_mode': cls._resolve_portal_mode(scheme),
            }
        )

        # Synchronize and refresh readiness checklist
        cls.refresh_workspace_state(workspace)
        return workspace

    @classmethod
    @transaction.atomic
    def refresh_workspace_state(cls, workspace: ApplicationPreparationWorkspace) -> ApplicationPreparationWorkspace:
        """
        Evaluates known vs unknown eligibility rules, cross-references required documents
        against uploaded documents, checks prepared form info, and tallies tasks.
        """
        profile: BusinessProfile = workspace.business_profile
        scheme: Scheme = workspace.scheme

        # 1. Evaluate Eligibility Rules (Known vs Unknown vs Failed)
        rule_engine = RuleEngine()
        eval_result = rule_engine.evaluate(scheme, profile)

        known_conditions = []
        unknown_conditions = []
        disqualifiers = []

        for r_res in eval_result.rule_results:
            cond_item = {
                "rule_name": r_res.rule_name,
                "field_path": r_res.field_path,
                "expected": r_res.expected_value,
                "actual": r_res.actual_value,
                "operator": r_res.operator,
                "status": r_res.status,  # PASS, FAIL, UNKNOWN
                "importance": r_res.importance,
                "source_clause": r_res.source_clause
            }
            if r_res.status == 'PASS':
                known_conditions.append(cond_item)
            elif r_res.status == 'FAIL':
                disqualifiers.append(cond_item)
            else:
                unknown_conditions.append(cond_item)

        # 2. Required Documents Mapping
        # Map scheme required documents against uploaded verified documents
        uploaded_docs = profile.documents.all()
        uploaded_doc_types = {d.document_type: d for d in uploaded_docs}

        scheme_doc_requirements = scheme.required_documents or [
            {"document_type": "udyam_certificate", "label": "Udyam Registration Certificate", "mandatory": True},
            {"document_type": "gstin_certificate", "label": "GST Registration / GSTR-3B Return", "mandatory": True},
            {"document_type": "balance_sheet", "label": "Audited Balance Sheet & P&L (Latest FY)", "mandatory": True},
            {"document_type": "machinery_quotation_invoice", "label": "OEM Machinery Quotation / Proforma Invoice", "mandatory": True}
        ]

        document_checklist = []
        docs_ready = 0

        for req in scheme_doc_requirements:
            d_type = req.get('document_type', '')
            label = req.get('label') or req.get('name') or d_type.replace('_', ' ').title()
            is_mandatory = req.get('mandatory', True)
            
            uploaded = uploaded_doc_types.get(d_type)
            is_available = uploaded is not None
            is_verified = uploaded.verification_status == 'verified' if uploaded else False

            if is_available:
                docs_ready += 1

            document_checklist.append({
                "document_type": d_type,
                "label": label,
                "is_mandatory": is_mandatory,
                "is_available": is_available,
                "is_verified": is_verified,
                "document_id": str(uploaded.id) if uploaded else None,
                "document_title": uploaded.title if uploaded else None,
                "document_date": uploaded.document_issue_date.isoformat() if uploaded and uploaded.document_issue_date else None
            })

        # 3. Required Information (Form Fields for Official Portal)
        required_info_fields = [
            {
                "field_key": "business_name",
                "label": "Legal Business Name",
                "value": profile.business_name,
                "is_prepared": bool(profile.business_name),
                "source": "Profile"
            },
            {
                "field_key": "udyam_registration_number",
                "label": "Udyam Registration Number",
                "value": profile.udyam_registration_number,
                "is_prepared": bool(profile.udyam_registration_number),
                "source": "Udyam Registry"
            },
            {
                "field_key": "gstin",
                "label": "GSTIN Identification Number",
                "value": profile.gstin,
                "is_prepared": bool(profile.gstin),
                "source": "GST Certificate"
            },
            {
                "field_key": "pan",
                "label": "Enterprise / Promoter PAN",
                "value": profile.pan,
                "is_prepared": bool(profile.pan),
                "source": "Tax Record"
            },
            {
                "field_key": "state_district",
                "label": "Plant Location (State / District)",
                "value": f"{profile.district}, {profile.state}",
                "is_prepared": bool(profile.state and profile.district),
                "source": "Profile Location"
            },
            {
                "field_key": "annual_turnover_lakhs",
                "label": "Audited Annual Turnover",
                "value": f"₹{profile.annual_turnover_lakhs} Lakhs" if profile.annual_turnover_lakhs else None,
                "is_prepared": profile.annual_turnover_lakhs is not None,
                "source": "Financials"
            },
            {
                "field_key": "investment_in_plant_machinery_lakhs",
                "label": "Gross Plant & Machinery Investment",
                "value": f"₹{profile.investment_in_plant_machinery_lakhs} Lakhs" if profile.investment_in_plant_machinery_lakhs else None,
                "is_prepared": profile.investment_in_plant_machinery_lakhs is not None,
                "source": "Fixed Assets"
            }
        ]

        info_ready = sum(1 for f in required_info_fields if f["is_prepared"])

        # 4. Tasks from Action Plan related to this scheme
        tasks = ActionTask.objects.filter(
            business_profile=profile
        ).filter(
            models_q_scheme(scheme)
        ).order_by('priority')

        task_list = [
            {
                "id": str(t.id),
                "title": t.title,
                "priority": t.priority,
                "category": t.category,
                "status": t.status,
                "is_completed": t.status == CompletionStatus.COMPLETED,
                "rationale": t.rationale,
                "external_url": t.external_url
            }
            for t in tasks
        ]

        tasks_completed = sum(1 for t in task_list if t["is_completed"])

        # Update metrics
        workspace.documents_ready_count = docs_ready
        workspace.documents_total_count = len(document_checklist)
        workspace.info_ready_count = info_ready
        workspace.info_total_count = len(required_info_fields)
        workspace.tasks_completed_count = tasks_completed
        workspace.tasks_total_count = len(task_list)
        workspace.unknowns_count = len(unknown_conditions)

        # Update overall preparation status
        all_docs_ready = docs_ready >= len(document_checklist)
        all_info_ready = info_ready >= len(required_info_fields)
        has_no_disqualifiers = len(disqualifiers) == 0

        if all_docs_ready and all_info_ready and has_no_disqualifiers:
            workspace.status = 'ready_for_portal'
        else:
            workspace.status = 'in_preparation'

        workspace.workspace_data = {
            "known_conditions": known_conditions,
            "unknown_conditions": unknown_conditions,
            "disqualifiers": disqualifiers,
            "required_documents": document_checklist,
            "required_information": required_info_fields,
            "tasks": task_list,
            "overall_eligibility_status": eval_result.overall_status,
            "max_benefit_lakhs": float(scheme.max_benefit_amount_lakhs or 0)
        }
        workspace.save()

        return workspace

    @classmethod
    def _resolve_portal_url(cls, scheme: Scheme) -> str:
        if scheme.official_portal_url:
            return scheme.official_portal_url
        if scheme.level in ('state', 'state_gujarat'):
            return DEFAULT_OFFICIAL_PORTALS['state_gujarat']['portal_url']
        if "cgtmse" in scheme.scheme_code.lower():
            return DEFAULT_OFFICIAL_PORTALS['cgtmse']['portal_url']
        if "pmegp" in scheme.scheme_code.lower():
            return DEFAULT_OFFICIAL_PORTALS['pmegp']['portal_url']
        return DEFAULT_OFFICIAL_PORTALS['central']['portal_url']

    @classmethod
    def _resolve_portal_name(cls, scheme: Scheme) -> str:
        if scheme.level in ('state', 'state_gujarat'):
            return DEFAULT_OFFICIAL_PORTALS['state_gujarat']['portal_name']
        if "cgtmse" in scheme.scheme_code.lower():
            return DEFAULT_OFFICIAL_PORTALS['cgtmse']['portal_name']
        if "pmegp" in scheme.scheme_code.lower():
            return DEFAULT_OFFICIAL_PORTALS['pmegp']['portal_name']
        return DEFAULT_OFFICIAL_PORTALS['central']['portal_name']

    @classmethod
    def _resolve_portal_mode(cls, scheme: Scheme) -> str:
        if scheme.level in ('state', 'state_gujarat'):
            return DEFAULT_OFFICIAL_PORTALS['state_gujarat']['mode']
        if "cgtmse" in scheme.scheme_code.lower():
            return DEFAULT_OFFICIAL_PORTALS['cgtmse']['mode']
        return DEFAULT_OFFICIAL_PORTALS['central']['mode']


def models_q_scheme(scheme: Scheme):
    from django.db.models import Q
    return Q(scheme=scheme) | Q(related_scheme_ids__contains=scheme.scheme_code)
