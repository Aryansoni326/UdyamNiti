from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework import viewsets, status as http_status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.db.models import Q
from .models import Scheme, SchemeVersion
from apps.accounts.permissions import ReadOnlyOrAdmin
import re

# Comprehensive Document Checklist mapped directly from official uploaded scheme PDFs
SCHEME_DOCUMENTS_MAP = {
    'CGTMSE_EPM_EXPORT_2026': [
        {'id': 'iec', 'name': 'Valid Active Importer-Exporter Code (IEC)', 'desc': 'IEC issued by DGFT, not suspended or cancelled (Clause 4.c.i)', 'category': 'Statutory', 'mandatory': True},
        {'id': 'udyam', 'name': 'MSME Udyam Registration Certificate', 'desc': 'Valid Udyam Certificate linked directly to the IEC (Clause 4.c.ii)', 'category': 'Statutory', 'mandatory': True},
        {'id': 'ca_turnover', 'name': 'Chartered Accountant (CA) Turnover Certificate', 'desc': 'Validating applicant’s annual revenue and export turnover for past 3 FYs (2022-23, 2023-24, 2024-25) (Clause 4.c.iii)', 'category': 'Financial', 'mandatory': True},
        {'id': 'export_po', 'name': 'Self-attested Copy of Export Purchase Order / Contract', 'desc': 'Proof of active export order/shipment contract for goods under notified HSN 6-digit lines (Clause 4.c.iv)', 'category': 'Commercial', 'mandatory': True},
        {'id': 'bank_iec', 'name': 'Validated Bank Account Details from IEC Profile', 'desc': 'Account at an eligible Member Lending Institution (Public/Private/Foreign bank) validated on DGFT portal', 'category': 'Banking', 'mandatory': True},
        {'id': 'declaration', 'name': 'Statutory Declaration & Undertaking', 'desc': 'Certification confirming non-penalty under Customs/Excise/GST/FEMA, not on DEL, and under ₹10 Cr annual cap (Annexure-I)', 'category': 'Compliance', 'mandatory': True},
    ],
    'GUJ_SER_TEXTILE_2025': [
        {'id': 'dpr', 'name': 'Detailed Project Report (DPR)', 'desc': 'Comprehensive technical DPR covering park layout, R&D labs, machinery, and financial projection (Condition 1)', 'category': 'Technical', 'mandatory': True},
        {'id': 'gidc_land', 'name': 'Land Title / GIDC Possession Agreement', 'desc': 'Proof of land acquisition, possession, or long-term lease deed within Surat Economic Region (Condition 4)', 'category': 'Legal', 'mandatory': True},
        {'id': 'gpcb_clearance', 'name': 'GPCB Environmental Clearance (CTE / CTO)', 'desc': 'Consent to Establish/Operate from Gujarat Pollution Control Board with effluent treatment plan (Condition 7)', 'category': 'Regulatory', 'mandatory': True},
        {'id': 'power_water', 'name': 'HT/LT Power Line Feeder & Water Allocation NOC', 'desc': 'Sanction letter from electricity board and local water authority for industrial park supply (Condition 8)', 'category': 'Infrastructure', 'mandatory': True},
        {'id': 'sbd_compliance', 'name': 'Standard Bidding Document (SBD) Compliance', 'desc': 'Road & Building Dept Resolution No. RBD/OAS/e-file/16/2022/0002 certification (Condition 26)', 'category': 'Tender', 'mandatory': True},
        {'id': 'gem_procurement', 'name': 'GeM Procurement Certification / Industry Dept NOC', 'desc': 'Procurement via Government e-Marketplace or No Objection Certificate from Industries Dept (Condition 15)', 'category': 'Procurement', 'mandatory': True},
    ],
    'MSME_IC_SCHEME_2021': [
        {'id': 'ic_form', 'name': 'Prescribed Application Form (Annexure A - D)', 'desc': 'Duly filled application detailing proposed international exhibition, buyer-seller meet, or summit (Para 7.I)', 'category': 'Statutory', 'mandatory': True},
        {'id': 'budget_est', 'name': 'Detailed Budget Estimate (Annexure E)', 'desc': 'Itemized breakdown for space rent, airfare, freight, publicity, and duty allowance (Para 7.I.ii)', 'category': 'Financial', 'mandatory': True},
        {'id': 'udyam_list', 'name': 'Udyam Registration Certificates of Participants', 'desc': 'Valid Udyam certificates for all participating MSME units in the delegation (Para 7.II.iii)', 'category': 'Statutory', 'mandatory': True},
        {'id': 'association_reg', 'name': 'Association Registration & MoA/AoA', 'desc': 'Registration under Companies/Societies Act with past 3 years audited balance sheets (Para 7.I.v)', 'category': 'Legal', 'mandatory': True},
        {'id': 'score_card', 'name': 'MSME Selection Score Card (Annexure C)', 'desc': 'Official score card verifying minimum 60% qualifying score for delegation selection (Para 2.2.vii)', 'category': 'Evaluation', 'mandatory': True},
        {'id': 'cbfte_bills', 'name': 'CBFTE Fee Receipts / Invoices (If claiming First-Time Exporter)', 'desc': 'RCMC fee receipt, ECGC insurance receipt, and ISO/Testing laboratory invoices for reimbursement (Para 11)', 'category': 'Reimbursement', 'mandatory': False},
        {'id': 'non_duplication', 'name': 'Certificate of Non-Duplication (Annexure I)', 'desc': 'Declaration that no financial assistance has been sought or obtained from any other Ministry (Para 7.III.v)', 'category': 'Compliance', 'mandatory': True},
    ],
    'COIR_VIKAS_YOJANA_CVY': [
        {'id': 'cvy_form', 'name': 'CITUS Online Application Form (Part-A & Part-B)', 'desc': 'Complete details of coir production unit, promoter KYC, and Aadhaar/Udyam numbers (Section 5.ii)', 'category': 'Statutory', 'mandatory': True},
        {'id': 'coir_reg', 'name': 'Coir Board Registration & Udyog Aadhaar/Udyam', 'desc': 'Registration under Coir Industry Rules 2008 and active MSME Udyam certificate (CITUS Clause 5)', 'category': 'Statutory', 'mandatory': True},
        {'id': 'ipa_letter', 'name': 'In-Principle Approval (IPA) Letter from Coir Board', 'desc': 'Prior technical appraisal approval issued by Coir Board HQ before procuring machinery (Clause 6.ii)', 'category': 'Approval', 'mandatory': True},
        {'id': 'machinery_invoices', 'name': 'GST Invoices & BIS Compliance Certification', 'desc': 'Attested machinery bills with GST number and BIS standards confirmation from reputed makers (Clause 5.vi)', 'category': 'Commercial', 'mandatory': True},
        {'id': 'perf_guarantee', 'name': '2-Year Manufacturer Performance Guarantee', 'desc': 'Formal warranty & performance guarantee letter from the machinery supplier (Clause 5.vii)', 'category': 'Technical', 'mandatory': True},
        {'id': 'bank_appraisal', 'name': 'Bank Term Loan Sanction Letter / Techno-Financial Appraisal', 'desc': 'Copy of bank credit sanction or certified own-resource audit for machine purchase (Clause 5.x)', 'category': 'Financial', 'mandatory': True},
        {'id': 'ca_fixed_assets', 'name': 'CA Certificate of Fixed Assets (Annexure 1 & 2)', 'desc': 'Breakup of CIF/FOB, customs, freight, and erection costs certified by Chartered Accountant (Clause 5)', 'category': 'Financial', 'mandatory': True},
        {'id': 'non_alienation', 'name': '7-Year Non-Alienation & Operation Undertaking', 'desc': 'Legal undertaking pledging not to sell, transfer, or dispose of subsidized machinery for 7 years (Clause 8.c)', 'category': 'Legal', 'mandatory': True},
    ],
    'PMEGP_MSME_SCHEME': [
        {'id': 'pmegp_app', 'name': 'PMEGP Online Application & Project Report', 'desc': 'Detailed Project Report (DPR) with capital expenditure and working capital estimates (Clause 4)', 'category': 'Statutory', 'mandatory': True},
        {'id': 'aadhaar_pan', 'name': 'Aadhaar Card, PAN & Caste/Special Category Certificate', 'desc': 'Identity and eligibility authentication for 25%-35% margin money subsidy slab (Clause 4.1)', 'category': 'Identity', 'mandatory': True},
        {'id': 'edu_cert', 'name': '8th Standard Pass Certificate / Marksheet', 'desc': 'Mandatory qualification proof for manufacturing projects over ₹10L or service projects over ₹5L (Clause 4.2)', 'category': 'Educational', 'mandatory': True},
        {'id': 'edp_cert', 'name': 'Entrepreneurship Development Programme (EDP) Certificate', 'desc': 'Proof of completing mandatory 10-day EDP training prior to final subsidy adjustment (Clause 5)', 'category': 'Training', 'mandatory': True},
        {'id': 'bank_sanction', 'name': 'Bank Term Loan Sanction & Disbursement Advice', 'desc': 'Sanction letter from financing bank with 90-95% loan component (Clause 6)', 'category': 'Banking', 'mandatory': True},
    ],
    'MSME_ZED_CERTIFICATION': [
        {'id': 'udyam_cert', 'name': 'Valid Udyam Registration Certificate', 'desc': 'NIC manufacturing activity codes authenticated on Udyam portal (Clause 4)', 'category': 'Statutory', 'mandatory': True},
        {'id': 'zed_pledge', 'name': 'Digital ZED Pledge & Self-Assessment Report', 'desc': 'Completed online self-assessment for Bronze, Silver, or Gold level (Clause 5)', 'category': 'Technical', 'mandatory': True},
        {'id': 'pollution_noc', 'name': 'State Pollution Control Board Consent / Exemption', 'desc': 'CTE/CTO or white-category exemption proof for zero effect verification (Clause 5.2)', 'category': 'Compliance', 'mandatory': True},
        {'id': 'fee_receipt', 'name': 'Accredited Assessment Agency Payment Receipt', 'desc': 'Proof of payment for desktop assessment or onsite audit for DBT reimbursement (Clause 6)', 'category': 'Financial', 'mandatory': True},
    ],
    'SFURTI_CLUSTER_SCHEME': [
        {'id': 'spv_reg', 'name': 'Cluster SPV Registration & MoA/AoA', 'desc': 'Registration under Sec 8 Company or Societies Act representing minimum 250 artisans (Clause 5.1)', 'category': 'Legal', 'mandatory': True},
        {'id': 'dpr_ta', 'name': 'Detailed Project Report (DPR) Vetted by Technical Agency', 'desc': 'Vetted business plan, machine layout, civil estimates, and revenue projections (Clause 5.3)', 'category': 'Technical', 'mandatory': True},
        {'id': 'land_lease', 'name': 'Land Possession Deed / 15-Year Lease Agreement', 'desc': 'Encumbrance-free title or registered minimum 15-year lease for Common Facility Centre (Clause 5.4)', 'category': 'Legal', 'mandatory': True},
    ],
    'TREDS_CGTMSE_CIRCULAR_262': [
        {'id': 'treds_profile', 'name': 'Registered Profile on TReDS Platform (RXIL/M1x/Invoicemart)', 'desc': 'Active supplier registration with verified Udyam number (Clause 3)', 'category': 'Statutory', 'mandatory': True},
        {'id': 'digital_invoice', 'name': 'Corporate Buyer Accepted Digital Invoice & Goods Receipt', 'desc': 'Factored invoice verified with acceptance certificate from buyer (Clause 4)', 'category': 'Commercial', 'mandatory': True},
        {'id': 'cgtmse_agreement', 'name': 'Member Financier Guarantee Undertaking', 'desc': 'Bank/NBFC factor agreement registering under CGTMSE Circular 262 (Clause 6)', 'category': 'Banking', 'mandatory': True},
    ],
    'MSE_CDP_CLUSTER_DEV': [
        {'id': 'spv_mou', 'name': 'SPV Formation & Member Resolution (Min 20 MSEs)', 'desc': 'Formal SPV with minimum 20 MSE members and 10% equity commitment (Clause 4.1)', 'category': 'Legal', 'mandatory': True},
        {'id': 'state_dpr', 'name': 'Detailed Project Report Approved by State Govt & SIDBI', 'desc': 'DPR with comprehensive technical, financial, and environmental appraisal (Clause 5)', 'category': 'Technical', 'mandatory': True},
        {'id': 'land_clearance', 'name': 'Industrial Estate Land Title & GIDC/State Allotment', 'desc': 'Clean title deed or state allotment letter for CFC/Industrial Estate (Clause 4.4)', 'category': 'Infrastructure', 'mandatory': True},
    ],
    'PMS_MARKETING_SUPPORT': [
        {'id': 'pms_application', 'name': 'Online Application on PMS Portal (my.msme.gov.in)', 'desc': 'Submitted at least 30 days prior to domestic exhibition or trade fair (Clause 3)', 'category': 'Statutory', 'mandatory': True},
        {'id': 'udyam_cert', 'name': 'MSME Udyam Registration Certificate', 'desc': 'Proof of micro/small manufacturing or service unit (Clause 3.1)', 'category': 'Statutory', 'mandatory': True},
        {'id': 'stall_bill', 'name': 'Exhibition Organizer Stall Rent Invoice & Payment Proof', 'desc': 'Receipt for stall rent, layout plan, and photo proof for 100% reimbursement up to ₹1.5L (Clause 4)', 'category': 'Financial', 'mandatory': True},
    ],
    'NSSH_SPECIAL_CLCSS': [
        {'id': 'scst_caste_cert', 'name': 'SC/ST Caste Certificate & 51%+ Shareholding Proof', 'desc': 'Government-issued community certificate and CA shareholding audit (Clause 4.1)', 'category': 'Identity', 'mandatory': True},
        {'id': 'udyam_scst', 'name': 'Udyam Certificate Authenticated under SC/ST Category', 'desc': 'Active Udyam registration mapped to SC/ST Hub database (Clause 4.2)', 'category': 'Statutory', 'mandatory': True},
        {'id': 'bank_machinery_loan', 'name': 'Term Loan Sanction Letter for New Machinery', 'desc': 'Sanction letter from scheduled bank for purchase of BIS/modern machinery (Clause 5)', 'category': 'Financial', 'mandatory': True},
    ],
}

DEFAULT_DOCUMENTS = [
    {'id': 'udyam_cert', 'name': 'MSME Udyam Registration Certificate', 'desc': 'Valid certificate issued by the Ministry of MSME', 'category': 'Statutory', 'mandatory': True},
    {'id': 'pan_gst', 'name': 'PAN Card & GST Registration Certificate', 'desc': 'Entity proof and tax registration active filing records', 'category': 'Taxation', 'mandatory': True},
    {'id': 'bank_statements', 'name': 'Audited Financial Statements & Bank Statements', 'desc': 'Past 2-3 years P&L, Balance Sheet, and 6 months bank statement', 'category': 'Financial', 'mandatory': True},
    {'id': 'project_report', 'name': 'Detailed Project Report (DPR) / Quotations', 'desc': 'Cost estimates, vendor quotations, and business viability projections', 'category': 'Technical', 'mandatory': True},
]

BEST_DEALS = {
    'CGTMSE_EPM_EXPORT_2026': {
        'is_best_deal': True,
        'tag': '⭐ BEST DEAL: 85% Collateral-Free Export Credit up to ₹10 Cr',
        'highlight': 'Highest guarantee ratio nationwide. Zero hard collateral needed. DGFT + CGTMSE joint initiative.',
        'score': 98,
        'deadline_text': 'Rolling Annual Window (Valid till 31 March 2027)',
    },
    'PMEGP_MSME_SCHEME': {
        'is_best_deal': True,
        'tag': '⭐ BEST DEAL: 15% - 35% Margin Money Capital Subsidy up to ₹50 Lakh',
        'highlight': 'Direct subsidy into bank account. Up to ₹17.5L subsidy for rural/women/special category; 2nd loan up to ₹1 Cr.',
        'score': 96,
        'deadline_text': 'Open Year-Round on KVIC Portal',
    },
    'COIR_VIKAS_YOJANA_CVY': {
        'is_best_deal': True,
        'tag': '⭐ BEST DEAL: 25% Capital Subsidy on Machinery up to ₹2.50 Cr',
        'highlight': 'Direct Benefit Transfer (DBT) via PFMS. Covers modernization and new plant setup with BIS machinery.',
        'score': 95,
        'deadline_text': 'Apply within 12 months of machinery commissioning',
    },
    'GUJ_SER_TEXTILE_2025': {
        'is_best_deal': True,
        'tag': '⭐ BEST DEAL: ₹1.00 Cr Dedicated Textile & MSME Infrastructure Grant',
        'highlight': '100% grant for common testing labs, logistics hubs, zero-liquid discharge recycling in Surat hub.',
        'score': 93,
        'deadline_text': 'Valid till 31 March 2027 (2-Year Utilization Cap)',
    },
    'MSE_CDP_CLUSTER_DEV': {
        'is_best_deal': True,
        'tag': '⭐ BEST DEAL: Up to ₹21.00 Cr GoI Grant for Common Facility Centers',
        'highlight': '70% Central grant on ₹30 Crore CFC projects and 60-70% for establishing new industrial estates.',
        'score': 93,
        'deadline_text': 'Quarterly Steering Committee Review',
    },
    'TREDS_CGTMSE_CIRCULAR_262': {
        'is_best_deal': True,
        'tag': '⭐ BEST DEAL: 85% Factoring Guarantee on TReDS Invoices up to ₹5 Cr',
        'highlight': 'Instant working capital within 24 hours without collateral. Eliminates 45-day delayed payment risks.',
        'score': 92,
        'deadline_text': 'Daily Real-Time Invoice Factoring',
    },
    'MSME_IC_SCHEME_2021': {
        'is_best_deal': True,
        'tag': '⭐ BEST DEAL: 100% Stall Space & Economy Airfare for Global Expos',
        'highlight': 'Up to ₹3.00 Lakh space rent + ₹1.50 Lakh airfare reimbursement + 75% testing & RCMC fee coverage.',
        'score': 91,
        'deadline_text': 'Submit min 60 days before foreign trade event',
    },
    'SFURTI_CLUSTER_SCHEME': {
        'is_best_deal': True,
        'tag': '⭐ BEST DEAL: 90% - 95% Grant up to ₹5.00 Cr for Traditional Clusters',
        'highlight': 'High grant funding for CFCs, modern machinery, and packaging units for artisan groups.',
        'score': 90,
        'deadline_text': 'Open for Vetted DPR Proposals',
    },
    'MSME_ZED_CERTIFICATION': {
        'is_best_deal': True,
        'tag': '⭐ BEST DEAL: Up to 80% Subsidy on ZED Certification + ₹5L Consulting',
        'highlight': 'Zero Defect Zero Effect certification, interest subvention from banks, and ₹3L technology grant.',
        'score': 89,
        'deadline_text': 'Continuous Digital Enrollment on ZED Portal',
    },
    'NSSH_SPECIAL_CLCSS': {
        'is_best_deal': True,
        'tag': '⭐ BEST DEAL: 25% Capital Subsidy up to ₹25 Lakh for SC/ST MSEs',
        'highlight': 'Upfront subsidy on plant and machinery term loans plus 100% fee waiver on testing and tenders.',
        'score': 88,
        'deadline_text': 'Rolling Annual Window (Valid till 31 March 2027)',
    },
    'PMS_MARKETING_SUPPORT': {
        'is_best_deal': True,
        'tag': '⭐ BEST DEAL: 100% Domestic Expo Stall Reimbursement up to ₹1.5L',
        'highlight': 'Free stalls at national exhibitions, ₹50,000 barcode support, and e-commerce packaging grants.',
        'score': 87,
        'deadline_text': 'Apply min 30 days prior to exhibition',
    },
}


class SchemeViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [ReadOnlyOrAdmin]
    queryset = Scheme.objects.filter(status='active')

    def _ensure_pdf_schemes_seeded(self):
        """Auto-seed uploaded PDF schemes on first lookup if not all 11 schemes are in DB."""
        if Scheme.objects.count() < 11 or not Scheme.objects.filter(scheme_code='CGTMSE_EPM_EXPORT_2026').exists():
            try:
                from django.core.management import call_command
                call_command('seed_uploaded_pdf_schemes')
            except Exception:
                pass
            try:
                from django.core.management import call_command
                call_command('seed_uploaded_pdf_schemes')
            except Exception:
                pass

    def list(self, request):
        self._ensure_pdf_schemes_seeded()
        qs = Scheme.objects.filter(status='active')
        
        search = request.query_params.get('search') or request.query_params.get('q')
        level = request.query_params.get('level')
        support_type = request.query_params.get('support_type')
        category = request.query_params.get('category')
        
        if search:
            search_terms = search.strip().split()
            q_obj = Q()
            for term in search_terms:
                q_obj |= (
                    Q(name__icontains=term) |
                    Q(short_name__icontains=term) |
                    Q(scheme_code__icontains=term) |
                    Q(description__icontains=term) |
                    Q(benefit_description__icontains=term) |
                    Q(ministry_department__icontains=term) |
                    Q(target_sectors__icontains=term)
                )
            qs = qs.filter(q_obj)

        if level and level != 'all':
            qs = qs.filter(level=level)

        if support_type and support_type != 'all':
            qs = qs.filter(support_type=support_type)

        if category and category != 'all':
            qs = qs.filter(target_msme_categories__contains=[category])

        # Prioritize the official uploaded PDF schemes
        priority_codes = [
            'CGTMSE_EPM_EXPORT_2026',
            'PMEGP_MSME_SCHEME',
            'GUJ_SER_TEXTILE_2025',
            'COIR_VIKAS_YOJANA_CVY',
            'MSE_CDP_CLUSTER_DEV',
            'TREDS_CGTMSE_CIRCULAR_262',
            'MSME_IC_SCHEME_2021',
            'SFURTI_CLUSTER_SCHEME',
            'MSME_ZED_CERTIFICATION',
            'NSSH_SPECIAL_CLCSS',
            'PMS_MARKETING_SUPPORT',
        ]
        
        schemes_list = list(qs)
        schemes_list.sort(key=lambda s: (0 if s.scheme_code in priority_codes else 1, s.name))

        data = []
        for s in schemes_list:
            deal_info = BEST_DEALS.get(s.scheme_code, {})
            docs = SCHEME_DOCUMENTS_MAP.get(s.scheme_code, DEFAULT_DOCUMENTS)
            deadline = (
                deal_info.get('deadline_text')
                or (s.valid_until.strftime('%d %b %Y') if s.valid_until else 'March 31, 2027 (Annual Rolling)')
            )
            data.append({
                'id': str(s.id),
                'scheme_code': s.scheme_code,
                'name': s.name,
                'short_name': s.short_name or s.name,
                'ministry': s.ministry_department,
                'implementing_agency': s.implementing_agency,
                'level': s.level,
                'support_type': s.support_type,
                'max_benefit_lakhs': float(s.max_benefit_amount_lakhs) if s.max_benefit_amount_lakhs else None,
                'benefit_percentage': float(s.benefit_percentage) if s.benefit_percentage else None,
                'benefit_description': s.benefit_description,
                'status': s.status,
                'official_portal_url': s.official_portal_url,
                'gazette_notification': s.gazette_notification,
                'deadline': deadline,
                'is_best_deal': deal_info.get('is_best_deal', False),
                'best_deal_tag': deal_info.get('tag'),
                'best_deal_highlight': deal_info.get('highlight'),
                'target_msme_categories': s.target_msme_categories,
                'target_sectors': s.target_sectors,
                'document_count': len(docs),
                'required_documents': docs,
            })

        return Response({'count': len(data), 'results': data})

    def retrieve(self, request, pk=None):
        self._ensure_pdf_schemes_seeded()
        try:
            s = Scheme.objects.get(pk=pk)
        except (Scheme.DoesNotExist, ValueError):
            s = Scheme.objects.filter(scheme_code=pk).first()
            if not s:
                return Response({'error': 'Scheme not found'}, status=http_status.HTTP_404_NOT_FOUND)
        
        rules = [{
            'rule_name': r.rule_name,
            'display_label': r.display_label or r.rule_name,
            'importance': r.importance,
            'source_clause': r.source_clause,
            'source_document': r.source_document,
            'source_page': r.source_page,
            'failure_message': r.failure_message,
        } for r in s.rules.filter(is_active=True)]
        
        benefits = [{
            'benefit_name': b.benefit_name,
            'amount_or_percentage': b.amount_or_percentage,
            'cap_amount_lakhs': float(b.cap_amount_lakhs) if b.cap_amount_lakhs else None,
            'conditions': b.conditions,
            'source_clause': b.source_clause,
        } for b in s.benefits.all()]

        docs = SCHEME_DOCUMENTS_MAP.get(s.scheme_code, DEFAULT_DOCUMENTS)
        deal_info = BEST_DEALS.get(s.scheme_code, {})
        deadline = (
            deal_info.get('deadline_text')
            or (s.valid_until.strftime('%d %b %Y') if s.valid_until else 'March 31, 2027 (Annual Rolling)')
        )

        steps = []
        if s.application_process:
            raw_steps = re.split(r'Step \d+:|\d+\.\s+', s.application_process)
            for st in raw_steps:
                if st.strip():
                    steps.append(st.strip())
        if not steps:
            steps = [
                'Verify MSME Udyam Registration & IEC Status.',
                'Compile all statutory CA certificates & required documents from the checklist.',
                'Submit online declaration or application on the designated government portal.',
                'Coordinate with Member Lending Institution / District Industries Centre for appraisal.',
                'Receive sanction, unique identification number (UIN/CGPAN), and grant disbursement.',
            ]

        return Response({
            'id': str(s.id),
            'scheme_code': s.scheme_code,
            'name': s.name,
            'short_name': s.short_name or s.name,
            'ministry': s.ministry_department,
            'implementing_agency': s.implementing_agency,
            'level': s.level,
            'support_type': s.support_type,
            'target_msme_categories': s.target_msme_categories,
            'target_states': s.target_states,
            'target_sectors': s.target_sectors,
            'max_benefit_lakhs': float(s.max_benefit_amount_lakhs) if s.max_benefit_amount_lakhs else None,
            'benefit_percentage': float(s.benefit_percentage) if s.benefit_percentage else None,
            'benefit_description': s.benefit_description,
            'description': s.description,
            'eligibility_summary': s.eligibility_summary,
            'application_process': s.application_process,
            'application_steps': steps,
            'official_portal_url': s.official_portal_url,
            'gazette_notification': s.gazette_notification,
            'deadline': deadline,
            'is_best_deal': deal_info.get('is_best_deal', False),
            'best_deal_tag': deal_info.get('tag'),
            'best_deal_highlight': deal_info.get('highlight'),
            'required_documents': docs,
            'rules': rules,
            'benefits': benefits,
            'status': s.status,
        })


class SchemeRagRecommendView(APIView):
    """
    RAG-driven Scheme Recommendation Engine.
    Analyzes business context/query and returns ranked schemes with "Best Deal" tags,
    benefit justification, and required documents.
    """
    def post(self, request):
        query = request.data.get('query', '').strip().lower()
        sector = request.data.get('sector', '').strip().lower()

        # Retrieve active schemes
        schemes = list(Scheme.objects.filter(status='active'))
        if not schemes:
            try:
                from django.core.management import call_command
                call_command('seed_uploaded_pdf_schemes')
                schemes = list(Scheme.objects.filter(status='active'))
            except Exception:
                pass

        results = []
        for s in schemes:
            score = 65
            reasons = []
            
            text_corpus = f"{s.name} {s.short_name} {s.description} {s.benefit_description} {s.scheme_code} {' '.join(s.target_sectors)}".lower()
            
            if 'export' in query or 'foreign' in query or 'trade' in query:
                if 'export' in text_corpus or 'epm' in text_corpus or 'ic' in text_corpus:
                    score += 24
                    reasons.append('Directly matches export promotion & foreign trade mission')
            if 'credit' in query or 'loan' in query or 'guarantee' in query or 'collateral' in query or 'working capital' in query:
                if s.support_type in ['credit_guarantee', 'collateral_free_loan', 'capital_subsidy']:
                    score += 20
                    reasons.append('Provides institutional credit guarantee without collateral')
            if 'textile' in query or 'fabric' in query or 'surat' in query or 'park' in query:
                if 'textile' in text_corpus or 'ser' in text_corpus:
                    score += 28
                    reasons.append('Tailored for textile manufacturing & park infrastructure')
            if 'coir' in query or 'machinery' in query or 'equipment' in query or 'plant' in query:
                if 'coir' in text_corpus or 'citus' in text_corpus or 'cvy' in text_corpus or 'machinery' in text_corpus:
                    score += 25
                    reasons.append('Offers up to 25% capital subsidy on BIS machinery procurement')
            if 'subsidy' in query or 'grant' in query:
                if s.support_type in ['capital_subsidy', 'technology_grant', 'infrastructure']:
                    score += 15
                    reasons.append('Delivers non-repayable capital subsidy and infrastructure grants')

            if sector and any(sector in sec.lower() for sec in s.target_sectors):
                score += 12
                reasons.append(f'Aligned with target sector: {sector}')

            is_deal = s.scheme_code in BEST_DEALS
            if is_deal:
                score += 8

            score = min(score, 99)
            deal_data = BEST_DEALS.get(s.scheme_code, {})
            docs = SCHEME_DOCUMENTS_MAP.get(s.scheme_code, DEFAULT_DOCUMENTS)
            deadline = deal_data.get('deadline_text') or (s.valid_until.strftime('%d %b %Y') if s.valid_until else 'March 31, 2027')

            results.append({
                'id': str(s.id),
                'scheme_code': s.scheme_code,
                'name': s.name,
                'short_name': s.short_name or s.name,
                'ministry': s.ministry_department,
                'support_type': s.support_type,
                'level': s.level,
                'match_score': score,
                'is_best_deal': is_deal,
                'best_deal_tag': deal_data.get('tag'),
                'best_deal_highlight': deal_data.get('highlight'),
                'max_benefit_lakhs': float(s.max_benefit_amount_lakhs) if s.max_benefit_amount_lakhs else None,
                'benefit_description': s.benefit_description,
                'deadline': deadline,
                'recommendation_rationale': reasons if reasons else ['Eligible based on general MSME classification & sector guidelines.'],
                'required_documents_count': len(docs),
                'required_documents': docs[:4],
                'official_portal_url': s.official_portal_url,
            })

        results.sort(key=lambda x: (1 if x['is_best_deal'] else 0, x['match_score']), reverse=True)

        return Response({
            'query': query,
            'total_matches': len(results),
            'top_deal': results[0] if results else None,
            'recommendations': results[:6],
        })


router = DefaultRouter()
router.register('schemes', SchemeViewSet, basename='scheme')

from rest_framework.views import APIView
from apps.policies.policy_agent import PolicyAgent


class PolicyAgentResearchAPIView(APIView):
    """
    Constrained Policy Research Agent Endpoint.
    Translates structured business goals into discovery filters,
    invokes statutory tools with prompt-injection defense, and packages
    candidate schemes & evidence bundles for the Eligibility Engine.
    """
    def post(self, request):
        goal_summary = request.data.get('goal_summary', {})
        profile_facts = request.data.get('business_profile_facts', {})

        if not goal_summary and not profile_facts:
            return Response({'error': 'goal_summary or business_profile_facts is required'}, status=400)

        agent = PolicyAgent()
        bundle = agent.research_policy_opportunities(goal_summary, profile_facts)
        return Response(bundle.to_dict())


from apps.policies.versioning_models import PolicyVersion
from apps.policies.versioning_service import PolicyVersioningService
from rest_framework import status
import datetime


class PolicyVersionListView(APIView):
    """List all temporal versions of a scheme with bitemporal dates and checksums."""
    def get(self, request):
        scheme_code = request.query_params.get('scheme_code')
        qs = PolicyVersion.objects.select_related('scheme').all()
        if scheme_code:
            qs = qs.filter(scheme__scheme_code=scheme_code)

        data = [{
            "id": str(v.id),
            "scheme_code": v.scheme.scheme_code,
            "version_tag": v.version_tag,
            "version_number": v.version_number,
            "effective_from": str(v.effective_from),
            "effective_until": str(v.effective_until) if v.effective_until else None,
            "source_authority": v.source_authority,
            "source_document": v.source_document,
            "document_checksum": v.document_checksum,
            "clause_or_page": v.clause_or_page,
            "is_active": v.is_active,
            "is_immutable": v.is_immutable,
            "change_summary": v.change_summary,
            "rule_count": len(v.rules_snapshot),
            "last_verified": v.last_verified.isoformat()
        } for v in qs]
        return Response(data, status=status.HTTP_200_OK)


class PolicyVersionCompareView(APIView):
    """Compare two policy versions at the field and rule level."""
    def get(self, request):
        scheme_code = request.query_params.get('scheme_code')
        v1_tag = request.query_params.get('v1')
        v2_tag = request.query_params.get('v2')

        if not scheme_code or not v1_tag or not v2_tag:
            return Response(
                {"error": "scheme_code, v1, and v2 query parameters are required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        v1 = PolicyVersion.objects.filter(scheme__scheme_code=scheme_code, version_tag=v1_tag).first()
        v2 = PolicyVersion.objects.filter(scheme__scheme_code=scheme_code, version_tag=v2_tag).first()

        if not v1 or not v2:
            return Response(
                {"error": f"One or both versions ({v1_tag}, {v2_tag}) not found for scheme '{scheme_code}'."},
                status=status.HTTP_404_NOT_FOUND
            )

        diff = PolicyVersioningService.compare_versions(v1, v2)
        return Response(diff, status=status.HTTP_200_OK)


class PolicyVersionDemoUpdateView(APIView):
    """Execute a controlled hackathon demo policy update with immutable version supersession."""
    def post(self, request):
        scheme_code = request.data.get('scheme_code')
        new_version_tag = request.data.get('new_version_tag')
        effective_from_str = request.data.get('effective_from')
        new_rules_snapshot = request.data.get('new_rules_snapshot', [])
        change_summary = request.data.get('change_summary', 'Controlled policy amendment')
        source_authority = request.data.get('source_authority', 'Official Industries Commissionerate')
        source_document = request.data.get('source_document', 'Statutory Amendment Resolution')
        document_text = request.data.get('document_text', 'Official Gazette Content')
        clause_or_page = request.data.get('clause_or_page', 'Clause 4.1 Amendment')
        new_benefits = request.data.get('new_benefits_snapshot', {})

        if not scheme_code or not new_version_tag:
            return Response({"error": "scheme_code and new_version_tag are required."}, status=status.HTTP_400_BAD_REQUEST)

        effective_from = datetime.date.fromisoformat(effective_from_str) if effective_from_str else datetime.date.today()

        try:
            old_v, new_v = PolicyVersioningService.publish_version_update(
                scheme_code=scheme_code,
                new_version_tag=new_version_tag,
                effective_from=effective_from,
                new_rules_snapshot=new_rules_snapshot,
                change_summary=change_summary,
                source_authority=source_authority,
                source_document=source_document,
                document_text_or_bytes=document_text,
                clause_or_page=clause_or_page,
                new_benefits_snapshot=new_benefits
            )
            return Response({
                "message": f"Successfully published policy update for {scheme_code}.",
                "superseded_version": old_v.version_tag if old_v else None,
                "new_active_version": new_v.version_tag,
                "document_checksum": new_v.document_checksum,
                "effective_from": str(new_v.effective_from)
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


urlpatterns = [
    path('schemes/rag-recommend/', SchemeRagRecommendView.as_view(), name='scheme-rag-recommend'),
    path('policy-agent/research/', PolicyAgentResearchAPIView.as_view(), name='policy-agent-research'),
    path('policies/versions/', PolicyVersionListView.as_view(), name='policy-versions-list'),
    path('policies/versions/compare/', PolicyVersionCompareView.as_view(), name='policy-versions-compare'),
    path('policies/versions/demo-update/', PolicyVersionDemoUpdateView.as_view(), name='policy-versions-demo-update'),
    path('', include(router.urls))
]
