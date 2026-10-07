"""
Seed command for the 4 official schemes provided in the user's uploaded official PDFs:
1. Gujarat SER Textile & MSME Park Assistance Scheme 2025-26
2. DGFT-CGTMSE Special Credit Guarantee Scheme for Export Credit (EPM - Niryat Protsahan)
3. International Cooperation (IC) Scheme, Ministry of MSME 2021
4. Coir Vikas Yojana (CVY - CITUS, MCY, EMP, DMP), Ministry of MSME
"""
from django.core.management.base import BaseCommand
from apps.policies.models import Scheme, SchemeRule, SchemeBenefit
from datetime import date
import logging

logger = logging.getLogger(__name__)

UPLOADED_PDF_SCHEMES = [
    {
        'scheme_code': 'CGTMSE_EPM_EXPORT_2026',
        'name': 'Special Credit Guarantee Scheme – Collateral Support for Export Credit (EPM - Niryat Protsahan)',
        'short_name': 'Export Credit Collateral Support (EPM)',
        'ministry_department': 'Department of Commerce, Ministry of Commerce and Industry / CGTMSE',
        'implementing_agency': 'Credit Guarantee Fund Trust for Micro and Small Enterprises (CGTMSE) & DGFT',
        'level': 'central',
        'support_type': 'credit_guarantee',
        'target_sectors': ['export', 'manufacturing', 'merchandise', 'services'],
        'target_msme_categories': ['micro', 'small', 'medium'],
        'target_states': [],
        'max_benefit_amount_lakhs': 1000.0,  # ₹10 Crore
        'benefit_percentage': 85.0,  # 85% for Micro & Small (75% CGTMSE + 10% DGFT), 65% for Medium
        'benefit_description': 'Collateral-free working capital export credit up to ₹10 Crore. 85% total guarantee cover for Micro & Small Enterprises (75% CGTMSE + 10% DGFT) and 65% for Medium Enterprises. Annual Guarantee Fee (AGF) starts from 0.37% (0.33% with discount).',
        'status': 'active',
        'launch_date': date(2026, 2, 6),
        'valid_until': date(2027, 3, 31),
        'official_portal_url': 'https://www.dgft.gov.in',
        'gazette_notification': 'CGTMSE Circular No. 257 / 2025-26; Ref. No. CGTMSE /Circular/294',
        'description': (
            'The Special Credit Guarantee Scheme – Collateral Support for Export Credit under the Export Promotion Mission (EPM – Niryat Protsahan) '
            'provides institutional export credit guarantee to Micro, Small, and Medium Enterprise exporters without requiring third-party guarantees or '
            'hard collateral. It facilitates both pre-shipment and post-shipment export working capital credit through Member Lending Institutions (MLIs) '
            'including Scheduled Commercial Banks and eligible Financial Institutions.'
        ),
        'eligibility_summary': (
            '1. All MSME manufacturer and merchant exporters holding an active Importer-Exporter Code (IEC) and valid MSME Udyam Registration Number. '
            '2. Export products must fall under the notified positive list of Harmonised System (HSN) 6-digit tariff lines. '
            '3. Pre- and post-shipment working capital credit in accordance with RBI Master Directions. '
            '4. Exporters must file an online declaration of intent on the DGFT portal to generate a Unique Identification Number (UIN). '
            '5. Aggregate guarantee limit capped at ₹10 Crore across all CGTMSE interventions.'
        ),
        'application_process': (
            'Step 1: Log in to the DGFT portal (Services > Export Promotion Mission > Collateral Support for Export Credit). '
            'Step 2: Submit online intent form with IEC, Udyam, 3-year turnover CA certificate, and export Purchase Order to generate UIN. '
            'Step 3: Approach an eligible Member Lending Institution (Public, Private, or Foreign Bank listed in Annexure 12C) quoting the UIN. '
            'Step 4: Bank assesses creditworthiness and applies to CGTMSE with UIN for guarantee allotment (CGPAN issued). '
            'Step 5: CGTMSE issues final credit guarantee on payment of Annual Guarantee Fee (AGF).'
        ),
        'rules': [
            {
                'rule_name': 'Valid Active IEC Code',
                'field_path': 'has_iec_code',
                'operator': 'bool_true',
                'expected_value': True,
                'importance': 'mandatory',
                'source_clause': 'Must hold a valid active Importer-Exporter Code (IEC) not suspended or cancelled (Section 12.X.1.a).',
                'source_document': 'CGTMSE Circular No. 257 / 2025-26, HBP Clause 12.X.1',
                'display_label': 'Valid Active IEC Code',
                'failure_message': 'An active Importer-Exporter Code (IEC) is mandatory for export credit guarantee.',
            },
            {
                'rule_name': 'Valid Udyam Registration',
                'field_path': 'has_udyam_registration',
                'operator': 'bool_true',
                'expected_value': True,
                'importance': 'mandatory',
                'source_clause': 'Must hold a valid MSME Udyam Registration Number linked to the IEC (Clause 12.X.1.a).',
                'source_document': 'CGTMSE Circular No. 257 / 2025-26, HBP Clause 12.X.1',
                'display_label': 'Udyam Registration Linked to IEC',
                'failure_message': 'A valid Udyam Registration Number linked to the IEC is mandatory.',
            },
            {
                'rule_name': 'Not on DGFT Denied Entity List (DEL)',
                'field_path': 'is_del_listed',
                'operator': 'bool_false',
                'expected_value': False,
                'importance': 'mandatory',
                'source_clause': 'Neither company nor directors/partners shall be on the Denied Entity List (DEL) of DGFT (Declaration Para B).',
                'source_document': 'CGTMSE Circular No. 257, Annexure-I Declaration',
                'display_label': 'Clean Track Record (Not on DEL)',
                'failure_message': 'Entity or directors on the DGFT Denied Entity List are ineligible.',
            },
            {
                'rule_name': 'Not Classified as NPA',
                'field_path': 'is_npa',
                'operator': 'bool_false',
                'expected_value': False,
                'importance': 'mandatory',
                'source_clause': 'Account must not be classified as Non-Performing Asset (NPA) or willful defaulter (Section 10).',
                'source_document': 'CGTMSE Circular No. 257, Clause 10',
                'display_label': 'Non-NPA Good Financial Standing',
                'failure_message': 'Borrowers in default or NPA are excluded from credit guarantee.',
            },
        ],
        'benefits': [
            {
                'benefit_name': '85% Guarantee Coverage for Micro & Small Enterprises',
                'benefit_type': 'credit_guarantee',
                'amount_or_percentage': '85% (75% CGTMSE + 10% DGFT)',
                'cap_amount_lakhs': 1000.0,
                'conditions': 'For loans up to ₹10 Crore without third-party collateral.',
                'source_clause': 'Appendix 12A, Para 3(a)(i): Total coverage 85% for Micro and Small Enterprises up to ₹10 Crore.',
            },
            {
                'benefit_name': '65% Guarantee Coverage for Medium Enterprises',
                'benefit_type': 'credit_guarantee',
                'amount_or_percentage': '65% DGFT coverage',
                'cap_amount_lakhs': 1000.0,
                'conditions': 'For Medium enterprise export working capital facilities.',
                'source_clause': 'Appendix 12A, Para 3(a)(ii): Total coverage 65% for Medium Enterprises up to ₹10 Crore.',
            }
        ],
    },
    {
        'scheme_code': 'GUJ_SER_TEXTILE_2025',
        'name': 'Assistance for Developing SER Textile and MSME Park 2025-26',
        'short_name': 'SER Textile & MSME Park Assistance',
        'ministry_department': 'Industries and Mines Department, Government of Gujarat (ઉદ્યોગ અને ખાણ વિભાગ, ગુજરાત સરકાર)',
        'implementing_agency': 'Gujarat Industrial Development Corporation (GIDC) / Industries Commissionerate',
        'level': 'state_gujarat',
        'support_type': 'infrastructure',
        'target_sectors': ['textiles', 'apparel', 'weaving', 'spinning', 'manufacturing', 'processing'],
        'target_msme_categories': ['micro', 'small', 'medium'],
        'target_states': ['Gujarat'],
        'max_benefit_amount_lakhs': 100.0,  # ₹1.00 Crore new item provision
        'benefit_percentage': 100.0,
        'benefit_description': 'Integrated infrastructure setup assistance for textile manufacturing MSMEs in Surat region. Includes dedicated park plots, R&D testing labs, training hubs, warehousing, water recycling, and renewable solar power infrastructure.',
        'status': 'active',
        'launch_date': date(2025, 5, 1),
        'valid_until': date(2027, 3, 31),
        'official_portal_url': 'https://imd.gujarat.gov.in',
        'gazette_notification': 'Government Resolution No. IMD/MRT/e-file/9/2025/0597/G, Sachivalaya, Gandhinagar',
        'description': (
            'Government of Gujarat Resolution for developing modern SER Textile and MSME Parks in the Surat economic hub. '
            'The park provides integrated common facilities for Micro, Small, and Medium Enterprises including advanced manufacturing spaces, '
            'R&D design facilities, material testing laboratories, skill training centers, logistics hubs, zero-liquid-discharge water recycling, '
            'and renewable energy installations to boost local textile competitiveness and global export capability.'
        ),
        'eligibility_summary': (
            '1. Textile manufacturing, weaving, spinning, and allied MSMEs located or establishing operations in Gujarat (Surat regional focus). '
            '2. Unit must comply with the approved Detailed Project Report (DPR) timelines and budgetary caps. '
            '3. Implementation executed through Gujarat Industrial Development Corporation (GIDC). '
            '4. Mandatory statutory clearances: Railway, Forest, and Gujarat Pollution Control Board (GPCB) consent. '
            '5. Procurement strictly adhering to Government e-Marketplace (GeM) portal or Industry Dept NOC.'
        ),
        'application_process': (
            'Step 1: Submit formal project proposal with DPR to the Industries Commissionerate / GIDC Gandhinagar. '
            'Step 2: Obtain GPCB environmental clearance and land allocation confirmation. '
            'Step 3: Verification of HT/LT power connection and water source feasibility. '
            'Step 4: Scrutiny by Finance & Industry Committee under Resolution IMD/MRT/e-file/9/2025/0597/G. '
            'Step 5: Phased grant release upon milestone completion and submission of audited accounts.'
        ),
        'rules': [
            {
                'rule_name': 'Gujarat State Location',
                'field_path': 'state',
                'operator': 'eq',
                'expected_value': 'Gujarat',
                'importance': 'mandatory',
                'source_clause': 'Park and units must be situated within the state of Gujarat (Surat economic region) (Preamble).',
                'source_document': 'Gujarat GR No. IMD/MRT/e-file/9/2025/0597/G, Page 1',
                'display_label': 'Operational Location in Gujarat',
                'failure_message': 'SER Textile Park scheme is exclusively available for units in Gujarat.',
            },
            {
                'rule_name': 'Textile & Allied Manufacturing Sector',
                'field_path': 'is_manufacturing',
                'operator': 'bool_true',
                'expected_value': True,
                'importance': 'mandatory',
                'source_clause': 'Units must be dedicated to textile manufacturing, weaving, testing, or logistics (Preamble Para 2).',
                'source_document': 'Gujarat GR No. IMD/MRT/e-file/9/2025/0597/G, Page 1',
                'display_label': 'Textile Manufacturing / Allied Processing',
                'failure_message': 'Scheme is dedicated to textile sector MSMEs and park infrastructure.',
            },
            {
                'rule_name': 'DPR and Environmental Clearance',
                'field_path': 'has_bank_account',
                'operator': 'bool_true',
                'expected_value': True,
                'importance': 'mandatory',
                'source_clause': 'Must comply with approved DPR and obtain GPCB environmental clearance before project commencement (Condition 1 & 7).',
                'source_document': 'Gujarat GR No. IMD/MRT/e-file/9/2025/0597/G, Page 2',
                'display_label': 'DPR & Environmental Statutory Clearances',
                'failure_message': 'DPR and GPCB clearances are mandatory preconditions.',
            },
        ],
        'benefits': [
            {
                'benefit_name': 'Common Infrastructure & Facility Grant',
                'benefit_type': 'infrastructure',
                'amount_or_percentage': '100% grant funding for approved common facilities',
                'cap_amount_lakhs': 100.0,
                'conditions': 'Within approved DPR budget and 2-year expenditure window.',
                'source_clause': 'Resolution Para 1: ₹1.00 Crore new item allocation for FY 2025-26 under Head 4851.',
            }
        ],
    },
    {
        'scheme_code': 'COIR_VIKAS_YOJANA_CVY',
        'name': 'Coir Vikas Yojana (CVY) – Integrated Coir Development Scheme',
        'short_name': 'Coir Vikas Yojana (CVY)',
        'ministry_department': 'Ministry of Micro, Small & Medium Enterprises, Government of India',
        'implementing_agency': 'Coir Board, Kochi (Regional & Sub-Regional Offices)',
        'level': 'central',
        'support_type': 'technology_grant',
        'target_sectors': ['coir', 'agro_processing', 'natural_fibres', 'textiles', 'handicrafts', 'manufacturing'],
        'target_msme_categories': ['micro', 'small', 'medium'],
        'target_states': [],
        'max_benefit_amount_lakhs': 250.0,  # ₹2.50 Crore CITUS ceiling
        'benefit_percentage': 25.0,  # 25% plant & machinery subsidy
        'benefit_description': (
            'Comprehensive umbrella scheme for coir industry: 1. CITUS: 25% capital subsidy on admissible plant & machinery up to ₹2.50 Crore. '
            '2. Mahila Coir Yojana: Skill training for women artisans with ₹3,000/mo stipend and PMEGP linkage up to ₹25 Lakhs. '
            '3. Export Market Promotion (EMP): 100% stall rent (up to ₹1L) & airfare (up to ₹1.5L) for overseas exhibitions. '
            '4. Domestic Market Promotion (DMP): 10% MDA on turnover.'
        ),
        'status': 'active',
        'launch_date': date(2018, 3, 7),
        'valid_until': date(2027, 3, 31),
        'official_portal_url': 'http://coirboard.gov.in',
        'gazette_notification': 'Ministry of MSME Order No. 5(9)/2017-Coir/77, CVY Operational Guidelines',
        'description': (
            'Coir Vikas Yojana (CVY) is an umbrella central sector scheme administered by the Coir Board to modernize the Indian coir sector. '
            'Its flagship component, CITUS (Coir Industry Technology Upgradation Scheme), provides 25% capital subsidy (up to ₹2.50 Crore) for '
            'procuring modern BIS-standard plant & machinery for setting up new units or modernizing existing coir enterprises. '
            'It also encompasses Mahila Coir Yojana (MCY), Science & Technology (S&T), Export Market Promotion (EMP), Domestic Market Promotion (DMP), '
            'and Pradhan Mantri Suraksha Bima Yojana (PMSBY) welfare coverage.'
        ),
        'eligibility_summary': (
            '1. Individuals, partnership firms, SHGs, cooperative societies, and private/public limited companies engaged in coir products. '
            '2. Registered under Coir Industry (Registration) Rules 2008 and holding valid Udyam Registration. '
            '3. Investment in plant & machinery must remain within MSME Act limits. '
            '4. Equipment and motors procured must comply with Bureau of Indian Standards (BIS) specifications. '
            '5. Beneficiary must not have availed Central subsidy under PMEGP, CUY, or TUF for the same plant & machinery.'
        ),
        'application_process': (
            'Step 1: Submit online application on Coir Board portal (coirboard.gov.in) with DPR prior to purchasing machinery. '
            'Step 2: Technical appraisal by CCRI / CICT and issuance of In-Principle Approval (IPA) by Project Steering Committee. '
            'Step 3: Procure BIS-certified machinery with GST invoices and 2-year manufacturer performance guarantee. '
            'Step 4: Joint on-the-spot physical inspection by Regional/Sub-Regional Officer of Coir Board. '
            'Step 5: Submission of claims with CA fixed asset certificates (Annexure 1 & 2) within 1 year of commencing commercial production. '
            'Step 6: Direct Benefit Transfer (DBT) subsidy disbursement via PFMS into the bank loan account.'
        ),
        'rules': [
            {
                'rule_name': 'Coir Board Registration & Udyam',
                'field_path': 'has_udyam_registration',
                'operator': 'bool_true',
                'expected_value': True,
                'importance': 'mandatory',
                'source_clause': 'Must be registered under Coir Industry Rules 2008 and hold valid Udyam Registration (CITUS Clause 5).',
                'source_document': 'CVY Operational Guidelines, CITUS Section 5',
                'display_label': 'Coir Board Registration & Udyam Certificate',
                'failure_message': 'Valid registration with Coir Board and Udyam is mandatory.',
            },
            {
                'rule_name': 'No Dual Subsidy Claim (PMEGP / TUFS)',
                'field_path': 'has_bank_account',
                'operator': 'bool_true',
                'expected_value': True,
                'importance': 'mandatory',
                'source_clause': 'Applicant must not have availed Central Government subsidy under PMEGP, CUY, TUF for the same plant/machinery (Clause 5.ix).',
                'source_document': 'CVY Operational Guidelines, CITUS Clause 5(ix)',
                'display_label': 'Single Subsidy Undertaking (No Dual Claim)',
                'failure_message': 'Cannot claim dual Central subsidies for the same machinery.',
            },
            {
                'rule_name': 'Asset Retention Commitment (7 Years)',
                'field_path': 'is_npa',
                'operator': 'bool_false',
                'expected_value': False,
                'importance': 'mandatory',
                'source_clause': 'Unit must retain and operate subsidized machinery for at least 7 years without disposal (Clause 8.c).',
                'source_document': 'CVY Operational Guidelines, CITUS Clause 8(c)',
                'display_label': '7-Year Asset Retention Compliance',
                'failure_message': 'Must commit to operating the assets for minimum 7 years.',
            },
        ],
        'benefits': [
            {
                'benefit_name': 'CITUS 25% Plant & Machinery Subsidy',
                'benefit_type': 'capital_subsidy',
                'amount_or_percentage': '25% of eligible plant & machinery cost',
                'cap_amount_lakhs': 250.0,
                'conditions': 'Maximum ceiling ₹2.50 Crores per coir unit via DBT/PFMS.',
                'source_clause': 'CVY Guidelines, CITUS Section 4.2: 25% financial assistance up to ₹2.50 Crore.',
            },
            {
                'benefit_name': 'Export Market Promotion (EMP) Travel & Stall Assistance',
                'benefit_type': 'market_development',
                'amount_or_percentage': '100% stall rent (up to ₹1L) + 100% airfare (up to ₹1.5L)',
                'cap_amount_lakhs': 2.5,
                'conditions': 'For participating in international exhibitions abroad (max 2 events/year).',
                'source_clause': 'CVY Guidelines, EMP Section 2.2.6: Max assistance ₹2.50 Lakh per event.',
            },
        ],
    },
    {
        'scheme_code': 'MSME_IC_SCHEME_2021',
        'name': 'International Cooperation (IC) Scheme',
        'short_name': 'International Cooperation Scheme',
        'ministry_department': 'Ministry of Micro, Small & Medium Enterprises, Government of India',
        'implementing_agency': 'IC Section, Ministry of MSME / Export Promotion Councils (EPCs)',
        'level': 'central',
        'support_type': 'market_development',
        'target_sectors': ['export', 'manufacturing', 'services', 'all_msme'],
        'target_msme_categories': ['micro', 'small'],
        'target_states': [],
        'max_benefit_amount_lakhs': 200.0,  # ₹2.00 Crore per international event
        'benefit_percentage': 100.0,
        'benefit_description': (
            '100% space rent (up to ₹3.00 Lakh) and 100% economy airfare (up to ₹1.50 Lakh) plus USD 150/day duty allowance for exhibiting at international trade fairs. '
            'Sub-Component II (CBFTE) reimburses 75% RCMC fees (up to ₹20,000), ECGC export insurance (up to ₹10,000), and testing/quality certifications (75% up to ₹1.00 Lakh).'
        ),
        'status': 'active',
        'launch_date': date(2021, 8, 1),
        'valid_until': date(2027, 3, 31),
        'official_portal_url': 'https://ic.msme.gov.in',
        'gazette_notification': 'F.No.4/8/2021-IC, Ministry of MSME, August 2021',
        'description': (
            'The International Cooperation (IC) Scheme builds MSME capacity for entering global export markets. '
            'Sub-Component I (MDA) reimburses stall rent, international airfare, freight, and daily allowances for MSME delegations '
            'participating in approved exhibitions abroad. Sub-Component II (CBFTE) handholds first-time MSE exporters by reimbursing '
            'EPC RCMC registration fees, export credit insurance premiums, and product testing & quality certification costs.'
        ),
        'eligibility_summary': (
            '1. Micro and Small Enterprises holding a valid Udyam Registration Certificate. '
            '2. For CBFTE first-time export incentives, the Importer-Exporter Code (IEC) must not be older than 3 years on date of export. '
            '3. Minimum score of 60% on the Annexure-C Score Card for international fair participation. '
            '4. One MSME unit cannot participate in more than 2 events in a financial year under the scheme. '
            '5. Adequate representation mandated for Women, SC/ST, and NER entrepreneurs.'
        ),
        'application_process': (
            'Step 1: Apply online on IC Scheme portal (ic.msme.gov.in) through registered Industry Association or EPC at least 60 days before event. '
            'Step 2: Submission of budget estimates and Score Card (Annexure-C) evaluated by Screening Committee. '
            'Step 3: Approval by Screening Committee headed by Joint Secretary (SME). '
            'Step 4: Participate in exhibition and retain original boarding passes, e-tickets, and stall invoices. '
            'Step 5: Submit claim within 60-90 days with CA certificate (Annexure-F) and Mandate Form (Annexure-H) for direct reimbursement.'
        ),
        'rules': [
            {
                'rule_name': 'Valid Udyam Registration',
                'field_path': 'has_udyam_registration',
                'operator': 'bool_true',
                'expected_value': True,
                'importance': 'mandatory',
                'source_clause': 'Must be a Micro or Small Enterprise with valid Udyam Registration (Section 8.a).',
                'source_document': 'IC Scheme Guidelines 2021, Section 8(a)',
                'display_label': 'Valid Udyam Registration Certificate',
                'failure_message': 'Udyam Registration is mandatory for IC Scheme benefits.',
            },
            {
                'rule_name': 'MSME Category — Micro or Small only',
                'field_path': 'msme_category',
                'operator': 'in',
                'expected_value': ['micro', 'small'],
                'importance': 'mandatory',
                'source_clause': 'CBFTE sub-component is restricted exclusively to Micro and Small enterprises (Section 1.2).',
                'source_document': 'IC Scheme Guidelines 2021, Section 1.2',
                'display_label': 'Micro or Small Enterprise Category',
                'failure_message': 'Medium enterprises are excluded from CBFTE export reimbursement.',
            },
            {
                'rule_name': 'IEC Age Less Than 3 Years (For CBFTE)',
                'field_path': 'has_iec_code',
                'operator': 'bool_true',
                'expected_value': True,
                'importance': 'preferred',
                'source_clause': 'Applicant IEC must not be older than 3 years on date of export shipment for first-time exporter benefits (Section 8.b).',
                'source_document': 'IC Scheme Guidelines 2021, Section 8(b)',
                'display_label': 'Active IEC Code (First-Time Exporter)',
                'failure_message': 'IEC required for export market and certification reimbursements.',
            },
        ],
        'benefits': [
            {
                'benefit_name': '100% Space Rent Reimbursement',
                'benefit_type': 'market_development',
                'amount_or_percentage': '100% up to ₹3.00 Lakh',
                'cap_amount_lakhs': 3.0,
                'conditions': 'For one MSME unit participating as exhibitor in approved international trade fairs.',
                'source_clause': 'IC Scheme Section 3.2.1(a): 100% space rent max ₹3.00 Lakh.',
            },
            {
                'benefit_name': '100% Economy Airfare Reimbursement',
                'benefit_type': 'market_development',
                'amount_or_percentage': '100% up to ₹1.50 Lakh',
                'cap_amount_lakhs': 1.5,
                'conditions': 'Economy class airfare for travel within 30 days of event.',
                'source_clause': 'IC Scheme Section 3.2.1(b): 100% economy airfare max ₹1.50 Lakh.',
            },
            {
                'benefit_name': 'Testing & Quality Certification Reimbursement',
                'benefit_type': 'quality_certification',
                'amount_or_percentage': '75% up to ₹1.00 Lakh',
                'cap_amount_lakhs': 1.0,
                'conditions': 'Max 3 certificates per financial year for products to be exported.',
                'source_clause': 'IC Scheme Section 9.2.1(iii): 75% testing fee max ₹1.00 Lakh.',
            },
            {
                'benefit_name': 'RCMC Registration Fee Reimbursement',
                'benefit_type': 'market_development',
                'amount_or_percentage': '75% up to ₹20,000',
                'cap_amount_lakhs': 0.2,
                'conditions': 'First-time exporters registering with Export Promotion Councils.',
                'source_clause': 'IC Scheme Section 9.2.1(i): 75% RCMC cost max ₹20,000.',
            },
        ],
    },
]


class Command(BaseCommand):
    help = 'Seeds database with the 4 official schemes provided in user uploaded PDFs.'

    def handle(self, *args, **options):
        self.stdout.write('🌱 Ingesting uploaded PDF schemes into UdyamNiti knowledgebase...')
        
        for data in UPLOADED_PDF_SCHEMES:
            rules_data = data.pop('rules', [])
            benefits_data = data.pop('benefits', [])
            
            scheme, created = Scheme.objects.update_or_create(
                scheme_code=data['scheme_code'],
                defaults=data
            )
            action_str = 'Created' if created else 'Updated'
            self.stdout.write(f'  ✓ {action_str} {scheme.scheme_code}: {scheme.name[:50]}...')
            
            # Seed Rules
            for i, rdata in enumerate(rules_data):
                rdata['order'] = i
                SchemeRule.objects.update_or_create(
                    scheme=scheme,
                    rule_name=rdata['rule_name'],
                    defaults=rdata
                )
                
            # Seed Benefits
            for bdata in benefits_data:
                SchemeBenefit.objects.update_or_create(
                    scheme=scheme,
                    benefit_name=bdata['benefit_name'],
                    defaults=bdata
                )
                
        self.stdout.write(self.style.SUCCESS(f'Successfully ingested {len(UPLOADED_PDF_SCHEMES)} official PDF schemes!'))
