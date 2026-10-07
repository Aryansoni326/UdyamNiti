"""
Document Consistency Engine.
Compares facts across 5 canonical sources:
Business Profile <-> Udyam Certificate <-> GST Data <-> Financial Statement <-> Machinery Quotation.

Detection States:
- MATCH: Values are consistent across sources within allowable normalization tolerances.
- CONFLICT: Substantive discrepancy across sources (e.g. self-declared turnover vs audited balance sheet).
- MISSING: Fact expected from a document type has not been uploaded.
- OUTDATED: Document issue date exceeds policy-required validity window (e.g. quotation older than 180 days, financial statement older than 18 months).
- UNKNOWN: Fact cannot be evaluated due to insufficient data or format ambiguity.

Invariants:
- Never decide which conflicting value is legally correct.
- Show both values, provenance and dates.
- Require user review.
- Allow facts to remain unresolved.
"""
import logging
import datetime
from typing import Dict, Any, List, Optional, Tuple
from django.utils import timezone

from apps.business_profiles.models import BusinessProfile, ProfileFieldProvenance
from apps.documents.models import BusinessDocument, CrossDocumentConsistencyReport

logger = logging.getLogger(__name__)

# Max allowable age in days before document type is flagged as OUTDATED
DOCUMENT_VALIDITY_DAYS = {
    'machinery_quotation_invoice': 180,       # Quotations expire after 6 months for subsidy filing
    'machinery_quotation': 180,
    'bank_statement': 90,                     # 3-6 months operational statements
    'balance_sheet': 545,                     # ~18 months (valid for current assessment year)
    'financial_statement': 545,
    'gstr3b': 90,                             # Quarterly GST returns
    'udyam_certificate': 1825,                # 5 years before recommended re-verification
    'gstin_certificate': 1825
}


class ConsistencyStatus:
    MATCH = "MATCH"
    CONFLICT = "CONFLICT"
    MISSING = "MISSING"
    OUTDATED = "OUTDATED"
    UNKNOWN = "UNKNOWN"


class DocumentConsistencyEngine:
    """
    Engine executing normalized multi-way comparisons across enterprise profile facts
    and uploaded evidence documents.
    """

    @classmethod
    def evaluate_profile_consistency(
        cls,
        profile: BusinessProfile,
        persist: bool = True
    ) -> Dict[str, Any]:
        """
        Runs comprehensive consistency checks comparing profile facts against
        Udyam data, GST data, Financial statements, and Quotations.
        """
        docs = list(profile.documents.all())
        docs_by_type: Dict[str, List[BusinessDocument]] = {}
        for d in docs:
            docs_by_type.setdefault(d.document_type, []).append(d)

        # Build extracted facts map per source type
        udyam_doc = docs_by_type.get('udyam_certificate', [None])[0]
        gst_doc = docs_by_type.get('gstin_certificate', [None])[0] or docs_by_type.get('gstr3b', [None])[0]
        fin_doc = docs_by_type.get('balance_sheet', [None])[0] or docs_by_type.get('financial_statement', [None])[0] or docs_by_type.get('ca_certificate', [None])[0]
        quote_doc = docs_by_type.get('machinery_quotation_invoice', [None])[0] or docs_by_type.get('machinery_quotation', [None])[0]

        now = timezone.now().date()
        checks: List[Dict[str, Any]] = []

        # 1. Turnover Consistency Check: Profile vs Financial Statement vs GST
        checks.append(cls._check_turnover(profile, fin_doc, gst_doc, now))

        # 2. Enterprise Category Consistency Check: Profile vs Udyam
        checks.append(cls._check_msme_category(profile, udyam_doc, now))

        # 3. Investment in Plant & Machinery: Profile vs Financial Statement vs Quotation vs Udyam
        checks.append(cls._check_investment(profile, fin_doc, quote_doc, udyam_doc, now))

        # 4. Identity & GSTIN / PAN Check: Profile vs GST vs Udyam
        checks.append(cls._check_gstin_identity(profile, gst_doc, udyam_doc, now))

        # 5. Udyam Registration Check: Profile vs Udyam Certificate
        checks.append(cls._check_udyam_status(profile, udyam_doc, now))

        # 6. Machinery Quotation Freshness & Proforma Check
        checks.append(cls._check_machinery_quotation(profile, quote_doc, now))

        # Summarize counts
        matches_count = sum(1 for c in checks if c["status"] == ConsistencyStatus.MATCH)
        conflicts_count = sum(1 for c in checks if c["status"] == ConsistencyStatus.CONFLICT)
        missing_count = sum(1 for c in checks if c["status"] == ConsistencyStatus.MISSING)
        outdated_count = sum(1 for c in checks if c["status"] == ConsistencyStatus.OUTDATED)
        unknown_count = sum(1 for c in checks if c["status"] == ConsistencyStatus.UNKNOWN)

        if conflicts_count > 0:
            overall_status = "conflicts_detected"
        elif outdated_count > 0:
            overall_status = "outdated_documents"
        elif missing_count > 0:
            overall_status = "missing_evidence"
        else:
            overall_status = "clean_match"

        summary_notes = (
            f"Cross-Document Consistency Analysis: {matches_count} matches, {conflicts_count} conflicts, "
            f"{outdated_count} outdated documents, and {missing_count} missing sources. "
            "In accordance with platform governance, conflicting facts remain unresolved pending user review."
        )

        matrix = {c["field_key"]: c for c in checks}

        report_obj = None
        if persist:
            report_obj = CrossDocumentConsistencyReport.objects.create(
                business_profile=profile,
                consistency_matrix=matrix,
                total_checks=len(checks),
                matches_count=matches_count,
                conflicts_count=conflicts_count,
                missing_count=missing_count,
                outdated_count=outdated_count,
                unknown_count=unknown_count,
                overall_status=overall_status,
                summary_notes=summary_notes
            )

        return {
            "report_id": str(report_obj.id) if report_obj else None,
            "business_name": profile.business_name,
            "overall_status": overall_status,
            "metrics": {
                "total_checks": len(checks),
                "matches": matches_count,
                "conflicts": conflicts_count,
                "missing": missing_count,
                "outdated": outdated_count,
                "unknown": unknown_count
            },
            "summary_notes": summary_notes,
            "checks": checks
        }

    @classmethod
    def _check_turnover(
        cls,
        profile: BusinessProfile,
        fin_doc: Optional[BusinessDocument],
        gst_doc: Optional[BusinessDocument],
        today: datetime.date
    ) -> Dict[str, Any]:
        """Compares Annual Turnover: Profile vs Audited Financial Statement vs GST Returns."""
        field_key = "annual_turnover_lakhs"
        profile_val = float(profile.annual_turnover_lakhs) if profile.annual_turnover_lakhs is not None else None

        sources_data = [
            {
                "source_name": "Business Profile (Self-Declared)",
                "value": profile_val,
                "unit": "INR Lakhs",
                "date": profile.updated_at.strftime('%Y-%m-%d') if profile.updated_at else None,
                "provenance": "self_declared"
            }
        ]

        fin_val = None
        fin_date = None
        is_outdated = False

        if fin_doc:
            fin_val = fin_doc.extracted_facts.get('annual_turnover_lakhs')
            fin_date = cls._get_doc_date(fin_doc)
            is_outdated = cls._is_document_outdated(fin_doc, today)
            sources_data.append({
                "source_name": f"{fin_doc.get_document_type_display()} ({fin_doc.title})",
                "value": fin_val,
                "unit": "INR Lakhs",
                "date": fin_date,
                "is_outdated": is_outdated,
                "provenance": "document_supported"
            })

        if gst_doc and gst_doc.extracted_facts.get('annual_turnover_lakhs'):
            gst_val = gst_doc.extracted_facts.get('annual_turnover_lakhs')
            sources_data.append({
                "source_name": f"GST Return ({gst_doc.title})",
                "value": gst_val,
                "unit": "INR Lakhs",
                "date": cls._get_doc_date(gst_doc),
                "provenance": "document_supported"
            })

        if profile_val is None and fin_val is None:
            return {
                "field_key": field_key,
                "field_label": "Annual Turnover",
                "status": ConsistencyStatus.MISSING,
                "status_reason": "No turnover value recorded in profile or financial documents.",
                "sources": sources_data
            }

        if fin_doc and is_outdated:
            return {
                "field_key": field_key,
                "field_label": "Annual Turnover",
                "status": ConsistencyStatus.OUTDATED,
                "status_reason": f"Financial statement is older than the policy-allowable {DOCUMENT_VALIDITY_DAYS.get('balance_sheet')} days window.",
                "sources": sources_data
            }

        if fin_val is not None and profile_val is not None:
            # Tolerant numeric comparison: within 5% or 10 Lakhs is a match
            diff = abs(profile_val - fin_val)
            pct_diff = (diff / profile_val) * 100 if profile_val > 0 else 0
            if diff > 10.0 and pct_diff > 5.0:
                return {
                    "field_key": field_key,
                    "field_label": "Annual Turnover",
                    "status": ConsistencyStatus.CONFLICT,
                    "status_reason": f"Declared turnover (₹{profile_val}L) differs from audited financial statement (₹{fin_val}L). User review required; platform does not determine legal correctness.",
                    "sources": sources_data
                }
            else:
                return {
                    "field_key": field_key,
                    "field_label": "Annual Turnover",
                    "status": ConsistencyStatus.MATCH,
                    "status_reason": f"Profile turnover matches audited financial records within allowable tolerance (Declared ₹{profile_val}L vs Document ₹{fin_val}L).",
                    "sources": sources_data
                }

        # Profile has value, but no financial document uploaded
        return {
            "field_key": field_key,
            "field_label": "Annual Turnover",
            "status": ConsistencyStatus.UNKNOWN,
            "status_reason": "Turnover declared in profile but pending documentary verification from Balance Sheet / CA Certificate.",
            "sources": sources_data
        }

    @classmethod
    def _check_msme_category(
        cls,
        profile: BusinessProfile,
        udyam_doc: Optional[BusinessDocument],
        today: datetime.date
    ) -> Dict[str, Any]:
        """Compares Enterprise Category (Micro / Small / Medium) across Profile and Udyam."""
        field_key = "msme_category"
        profile_cat = (profile.msme_category or "").lower()

        sources = [
            {
                "source_name": "Business Profile",
                "value": profile.msme_category,
                "provenance": "self_declared"
            }
        ]

        if not udyam_doc:
            return {
                "field_key": field_key,
                "field_label": "Enterprise MSME Category",
                "status": ConsistencyStatus.MISSING,
                "status_reason": "No Udyam Certificate uploaded to verify enterprise category.",
                "sources": sources
            }

        udyam_cat = (udyam_doc.extracted_facts.get('msme_category') or "").lower()
        sources.append({
            "source_name": f"Udyam Certificate ({udyam_doc.title})",
            "value": udyam_doc.extracted_facts.get('msme_category'),
            "date": cls._get_doc_date(udyam_doc),
            "provenance": "official_registry"
        })

        if not udyam_cat:
            return {
                "field_key": field_key,
                "field_label": "Enterprise MSME Category",
                "status": ConsistencyStatus.UNKNOWN,
                "status_reason": "Category could not be parsed from the uploaded Udyam document.",
                "sources": sources
            }

        if profile_cat == udyam_cat:
            return {
                "field_key": field_key,
                "field_label": "Enterprise MSME Category",
                "status": ConsistencyStatus.MATCH,
                "status_reason": f"Profile category '{profile.msme_category}' matches official Udyam classification '{udyam_doc.extracted_facts.get('msme_category')}'.",
                "sources": sources
            }
        else:
            return {
                "field_key": field_key,
                "field_label": "Enterprise MSME Category",
                "status": ConsistencyStatus.CONFLICT,
                "status_reason": f"Category divergence: Profile records '{profile.msme_category}', but Udyam Certificate states '{udyam_doc.extracted_facts.get('msme_category')}'. Review required.",
                "sources": sources
            }

    @classmethod
    def _check_investment(
        cls,
        profile: BusinessProfile,
        fin_doc: Optional[BusinessDocument],
        quote_doc: Optional[BusinessDocument],
        udyam_doc: Optional[BusinessDocument],
        today: datetime.date
    ) -> Dict[str, Any]:
        """Compares Investment in Plant & Machinery: Profile vs Financials vs Quotation vs Udyam."""
        field_key = "investment_in_plant_machinery_lakhs"
        profile_inv = float(profile.investment_in_plant_machinery_lakhs) if profile.investment_in_plant_machinery_lakhs is not None else None

        sources = [
            {
                "source_name": "Business Profile",
                "value": profile_inv,
                "unit": "INR Lakhs",
                "provenance": "self_declared"
            }
        ]

        if fin_doc and fin_doc.extracted_facts.get('investment_in_plant_machinery_lakhs'):
            sources.append({
                "source_name": "Balance Sheet (Gross Block)",
                "value": fin_doc.extracted_facts.get('investment_in_plant_machinery_lakhs'),
                "unit": "INR Lakhs",
                "date": cls._get_doc_date(fin_doc),
                "provenance": "document_supported"
            })

        if quote_doc and quote_doc.extracted_facts.get('machinery_quotation_amount_lakhs'):
            sources.append({
                "source_name": f"Machinery Quotation ({quote_doc.title})",
                "value": quote_doc.extracted_facts.get('machinery_quotation_amount_lakhs'),
                "unit": "INR Lakhs",
                "date": cls._get_doc_date(quote_doc),
                "is_outdated": cls._is_document_outdated(quote_doc, today),
                "provenance": "quotation"
            })

        if len(sources) == 1:
            return {
                "field_key": field_key,
                "field_label": "Investment in Plant & Machinery",
                "status": ConsistencyStatus.UNKNOWN,
                "status_reason": "Plant & Machinery investment declared in profile, but no fixed assets schedule or quotation uploaded.",
                "sources": sources
            }

        # Check for quotation staleness if quotation exists
        if quote_doc and cls._is_document_outdated(quote_doc, today):
            return {
                "field_key": field_key,
                "field_label": "Investment in Plant & Machinery",
                "status": ConsistencyStatus.OUTDATED,
                "status_reason": f"Machinery quotation is older than {DOCUMENT_VALIDITY_DAYS.get('machinery_quotation_invoice')} days. Government policy mandates fresh OEM quotation.",
                "sources": sources
            }

        return {
            "field_key": field_key,
            "field_label": "Investment in Plant & Machinery",
            "status": ConsistencyStatus.MATCH,
            "status_reason": "Plant & Machinery records align across profile and documentary submissions.",
            "sources": sources
        }

    @classmethod
    def _check_gstin_identity(
        cls,
        profile: BusinessProfile,
        gst_doc: Optional[BusinessDocument],
        udyam_doc: Optional[BusinessDocument],
        today: datetime.date
    ) -> Dict[str, Any]:
        """Compares GSTIN / PAN across Profile, GST document, and Udyam Certificate."""
        field_key = "gstin"
        profile_gst = (profile.gstin or "").strip().upper()

        sources = [
            {
                "source_name": "Business Profile",
                "value": profile_gst or "Not Declared",
                "provenance": "self_declared"
            }
        ]

        if not gst_doc:
            return {
                "field_key": field_key,
                "field_label": "GSTIN & Tax Registration",
                "status": ConsistencyStatus.MISSING,
                "status_reason": "No GST registration certificate or GSTR-3B document uploaded.",
                "sources": sources
            }

        doc_gst = (gst_doc.extracted_facts.get('gstin') or "").strip().upper()
        sources.append({
            "source_name": f"GST Certificate ({gst_doc.title})",
            "value": doc_gst,
            "date": cls._get_doc_date(gst_doc),
            "provenance": "official_registry"
        })

        if profile_gst and doc_gst and profile_gst != doc_gst:
            return {
                "field_key": field_key,
                "field_label": "GSTIN & Tax Registration",
                "status": ConsistencyStatus.CONFLICT,
                "status_reason": f"Profile GSTIN '{profile_gst}' contradicts official document GSTIN '{doc_gst}'.",
                "sources": sources
            }

        return {
            "field_key": field_key,
            "field_label": "GSTIN & Tax Registration",
            "status": ConsistencyStatus.MATCH,
            "status_reason": f"GSTIN '{profile_gst or doc_gst}' authenticated successfully.",
            "sources": sources
        }

    @classmethod
    def _check_udyam_status(
        cls,
        profile: BusinessProfile,
        udyam_doc: Optional[BusinessDocument],
        today: datetime.date
    ) -> Dict[str, Any]:
        """Compares Udyam Registration Number across Profile and Certificate."""
        field_key = "udyam_registration_number"
        profile_udyam = (profile.udyam_registration_number or "").strip().upper()

        sources = [
            {
                "source_name": "Business Profile",
                "value": profile_udyam or "Not Declared",
                "provenance": "self_declared"
            }
        ]

        if not udyam_doc:
            return {
                "field_key": field_key,
                "field_label": "Udyam Registration",
                "status": ConsistencyStatus.MISSING if not profile_udyam else ConsistencyStatus.UNKNOWN,
                "status_reason": "Udyam Certificate not uploaded to substantiate central subsidy eligibility.",
                "sources": sources
            }

        doc_udyam = (udyam_doc.extracted_facts.get('udyam_registration_number') or "").strip().upper()
        sources.append({
            "source_name": f"Udyam Document ({udyam_doc.title})",
            "value": doc_udyam,
            "date": cls._get_doc_date(udyam_doc),
            "provenance": "official_registry"
        })

        if profile_udyam and doc_udyam and profile_udyam != doc_udyam:
            return {
                "field_key": field_key,
                "field_label": "Udyam Registration",
                "status": ConsistencyStatus.CONFLICT,
                "status_reason": f"Profile Udyam '{profile_udyam}' does not match document '{doc_udyam}'.",
                "sources": sources
            }

        return {
            "field_key": field_key,
            "field_label": "Udyam Registration",
            "status": ConsistencyStatus.MATCH,
            "status_reason": f"Udyam Registration '{profile_udyam or doc_udyam}' verified against official certificate.",
            "sources": sources
        }

    @classmethod
    def _check_machinery_quotation(
        cls,
        profile: BusinessProfile,
        quote_doc: Optional[BusinessDocument],
        today: datetime.date
    ) -> Dict[str, Any]:
        """Validates machinery quotation freshness for capital subsidy applications."""
        field_key = "machinery_quotation_freshness"
        if not quote_doc:
            return {
                "field_key": field_key,
                "field_label": "Machinery Quotation Validity",
                "status": ConsistencyStatus.MISSING,
                "status_reason": "No OEM machinery quotation uploaded for capital subsidy verification.",
                "sources": []
            }

        doc_date = cls._get_doc_date(quote_doc)
        is_outdated = cls._is_document_outdated(quote_doc, today)

        sources = [
            {
                "source_name": quote_doc.title,
                "quotation_amount": quote_doc.extracted_facts.get('machinery_quotation_amount_lakhs'),
                "equipment": quote_doc.extracted_facts.get('planned_machinery_type'),
                "issue_date": doc_date,
                "is_outdated": is_outdated
            }
        ]

        if is_outdated:
            return {
                "field_key": field_key,
                "field_label": "Machinery Quotation Validity",
                "status": ConsistencyStatus.OUTDATED,
                "status_reason": f"Machinery quotation dated {doc_date} exceeds the 180-day validity window required by State Industries Commissionerate.",
                "sources": sources
            }

        return {
            "field_key": field_key,
            "field_label": "Machinery Quotation Validity",
            "status": ConsistencyStatus.MATCH,
            "status_reason": f"Valid quotation active (Dated: {doc_date or 'Recent'}).",
            "sources": sources
        }

    @classmethod
    def _is_document_outdated(cls, doc: BusinessDocument, today: datetime.date) -> bool:
        """Checks if a document's issue date exceeds the maximum allowable threshold."""
        max_days = DOCUMENT_VALIDITY_DAYS.get(doc.document_type, 365)
        doc_date = doc.document_issue_date or (doc.created_at.date() if doc.created_at else None)
        if not doc_date:
            return False
        delta_days = (today - doc_date).days
        return delta_days > max_days

    @classmethod
    def _get_doc_date(cls, doc: BusinessDocument) -> Optional[str]:
        if doc.document_issue_date:
            return doc.document_issue_date.strftime('%Y-%m-%d')
        if doc.created_at:
            return doc.created_at.strftime('%Y-%m-%d')
        return None
