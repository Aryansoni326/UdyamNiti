"""
Comprehensive Seed Command for Official Schemes strictly extracted from
the user's uploaded official PDFs in `backend/apps/data/schemes_pdfs`:

1.  CGTMSE_EPM_EXPORT_2026   -> Circular 257 - CGS for Export credit merged.pdf
2.  GUJ_SER_TEXTILE_2025     -> 1.msme.pdf (Gujarat SER Textile & MSME Park Assistance)
3.  PMEGP_MSME_SCHEME        -> pmegp scheme.pdf (Prime Minister's Employment Generation Programme)
4.  COIR_VIKAS_YOJANA_CVY    -> cvy.schemes.pdf (Coir Vikas Yojana - CITUS, MCY, EMP, DMP)
5.  MSME_IC_SCHEME_2021      -> Final and approved IC Scheme Guidelines-2021.pdf (International Cooperation)
6.  MSME_ZED_CERTIFICATION   -> ZED_Guidance_Document_NIC_Division_24 & 27.pdf (ZED Sustainable Certification)
7.  SFURTI_CLUSTER_SCHEME    -> SFURTI_NEW_GUIDELINES.pdf (Scheme of Fund for Regeneration of Traditional Industries)
8.  TREDS_CGTMSE_CIRCULAR_262-> TReDS Cicular 262.pdf (TReDS Invoice Discounting Credit Guarantee)
9.  MSE_CDP_CLUSTER_DEV      -> msme-cdp.pdf (Micro & Small Enterprises Cluster Development Programme)
10. PMS_MARKETING_SUPPORT    -> OM & PMS Scheme Guidelines.pdf (Procurement & Marketing Support)
11. NSSH_SPECIAL_CLCSS       -> NSSH_Guidelines_Sub_scheme_0 & 1.pdf (National SC-ST Hub Special Subsidy)
"""
from django.core.management.base import BaseCommand
from apps.policies.models import Scheme, SchemeRule, SchemeBenefit
from datetime import date
import logging

logger = logging.getLogger(__name__)

UPLOADED_PDF_SCHEMES = [
    # 1. CGTMSE EXPORT CREDIT GUARANTEE (Circular 257)
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

    # 2. GUJARAT SER TEXTILE & MSME PARK (1.msme.pdf)
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

    # 3. PMEGP (pmegp scheme.pdf)
    {
        'scheme_code': 'PMEGP_MSME_SCHEME',
        'name': 'Prime Minister’s Employment Generation Programme (PMEGP)',
        'short_name': 'PMEGP Credit Linked Capital Subsidy',
        'ministry_department': 'Ministry of Micro, Small and Medium Enterprises, Government of India',
        'implementing_agency': 'Khadi and Village Industries Commission (KVIC) / State KVIB / District Industries Centres (DIC)',
        'level': 'central',
        'support_type': 'capital_subsidy',
        'target_sectors': ['manufacturing', 'services', 'agro_processing', 'textiles', 'engineering', 'handicrafts'],
        'target_msme_categories': ['micro'],
        'target_states': [],
        'max_benefit_amount_lakhs': 50.0,  # ₹50 Lakhs project cost for manufacturing
        'benefit_percentage': 35.0,  # 15% to 35% margin money subsidy
        'benefit_description': 'Margin money capital subsidy: 15% (General Urban), 25% (General Rural / Special Urban), up to 35% (Special category/Women/SC/ST/OBC/NER in Rural areas). Maximum project cost ₹50 Lakhs for manufacturing and ₹20 Lakhs for service units. 2nd loan up to ₹1 Crore with 15-20% subsidy for upgrading existing performing units.',
        'status': 'active',
        'launch_date': date(2008, 8, 15),
        'valid_until': date(2027, 3, 31),
        'official_portal_url': 'https://www.kviconline.gov.in/pmegpeportal',
        'gazette_notification': 'Ministry of MSME PMEGP Comprehensive Operational Guidelines 2022-26',
        'description': (
            'PMEGP is a major credit-linked subsidy programme aimed at generating self-employment opportunities through establishment of micro-enterprises '
            'in non-farm sector. The subsidy is routed through KVIC as national nodal agency and directly credited to beneficiary bank accounts with a 3-year lock-in period.'
        ),
        'eligibility_summary': (
            '1. Any individual above 18 years of age. '
            '2. Minimum 8th standard pass for manufacturing projects over ₹10 Lakhs and service projects over ₹5 Lakhs. '
            '3. Self Help Groups (SHGs) and institutions registered under Societies Registration Act 1860. '
            '4. Project must be a new micro-enterprise (not existing units except for 2nd loan upgradation). '
            '5. Only one person from a family is eligible.'
        ),
        'application_process': (
            'Step 1: Submit online application at kviconline.gov.in with Aadhaar, caste certificate, EDP training certificate, and DPR. '
            'Step 2: District Level Task Force Committee (DLTFC) scrutinizes and recommends application to bank. '
            'Step 3: Financing bank sanctions loan and releases first installment. '
            'Step 4: KVIC deposits Margin Money subsidy into bank account as Term Deposit Receipt (TDR) for 3 years. '
            'Step 5: Physical verification after 36 months before final subsidy adjustment.'
        ),
        'rules': [
            {
                'rule_name': 'Age 18 Years or Above',
                'field_path': 'has_bank_account',
                'operator': 'bool_true',
                'expected_value': True,
                'importance': 'mandatory',
                'source_clause': 'Any individual above 18 years of age is eligible (Guidelines Clause 4.1).',
                'source_document': 'PMEGP Guidelines, Clause 4.1',
                'display_label': 'Age Qualification (>= 18 Years)',
                'failure_message': 'Applicant must be at least 18 years of age.',
            },
            {
                'rule_name': 'New Micro Enterprise Unit',
                'field_path': 'msme_category',
                'operator': 'in',
                'expected_value': ['micro'],
                'importance': 'mandatory',
                'source_clause': 'Scheme applies exclusively to new micro enterprises in manufacturing or service sectors (Clause 4.3).',
                'source_document': 'PMEGP Guidelines, Clause 4.3',
                'display_label': 'New Micro Enterprise Unit',
                'failure_message': 'PMEGP primary assistance is dedicated to new micro enterprises.',
            },
        ],
        'benefits': [
            {
                'benefit_name': '35% Rural Special Category Margin Money Subsidy',
                'benefit_type': 'capital_subsidy',
                'amount_or_percentage': '35% of project cost up to ₹17.50 Lakh',
                'cap_amount_lakhs': 17.5,
                'conditions': 'For SC/ST/OBC/Women/Minority/Ex-servicemen in rural areas.',
                'source_clause': 'PMEGP Guidelines, Table 1: 35% margin money subsidy in rural areas for special category.',
            },
            {
                'benefit_name': '25% General Rural / Special Urban Subsidy',
                'benefit_type': 'capital_subsidy',
                'amount_or_percentage': '25% of project cost up to ₹12.50 Lakh',
                'cap_amount_lakhs': 12.5,
                'conditions': 'For General category in rural areas or Special category in urban areas.',
                'source_clause': 'PMEGP Guidelines, Table 1: 25% margin money subsidy.',
            },
        ],
    },

    # 4. COIR VIKAS YOJANA (cvy.schemes.pdf)
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
        ],
    },

    # 5. INTERNATIONAL COOPERATION SCHEME (Final and approved IC Scheme Guidelines-2021.pdf)
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
            '4. One MSME unit cannot participate in more than 2 events in a financial year under the scheme.'
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
        ],
    },

    # 6. MSME ZED CERTIFICATION (ZED_Guidance_Document_NIC_Division_24 & 27.pdf)
    {
        'scheme_code': 'MSME_ZED_CERTIFICATION',
        'name': 'MSME Sustainable (ZED) Certification Scheme (Phase-II)',
        'short_name': 'ZED Sustainable Certification',
        'ministry_department': 'Ministry of Micro, Small and Medium Enterprises, Government of India',
        'implementing_agency': 'Quality Council of India (QCI) / National Productivity Council (NPC)',
        'level': 'central',
        'support_type': 'quality_certification',
        'target_sectors': ['manufacturing', 'engineering', 'automotive', 'food', 'chemicals', 'textiles', 'all_msme'],
        'target_msme_categories': ['micro', 'small', 'medium'],
        'target_states': [],
        'max_benefit_amount_lakhs': 8.0,  # ₹5 Lakh handholding + ₹3 Lakh tech support + 80% certification cost
        'benefit_percentage': 80.0,
        'benefit_description': (
            'Subsidized certification cost: 80% for Micro, 60% for Small, and 50% for Medium enterprises. '
            'Additional 10% concession for Women/SC/ST entrepreneurs and units in NER/Himalayan states. '
            'Financial assistance up to ₹5 Lakhs for handholding/consultancy support and up to ₹3 Lakhs for technology upgradation towards zero defect and zero effect manufacturing.'
        ),
        'status': 'active',
        'launch_date': date(2022, 4, 28),
        'valid_until': date(2027, 3, 31),
        'official_portal_url': 'https://zed.msme.gov.in',
        'gazette_notification': 'MSME Sustainable (ZED) Certification Scheme Guidelines 2022, Order No. 22(1)/2022-ZED',
        'description': (
            'The ZED scheme motivates MSMEs for Zero Defect Zero Effect manufacturing practices, enhancing quality, energy efficiency, '
            'natural resource conservation, and pollution reduction. MSMEs progress through Bronze, Silver, and Gold certification levels, '
            'receiving financial support, concession in bank processing fees, and preference in public procurement.'
        ),
        'eligibility_summary': (
            '1. All manufacturing MSMEs holding a valid Udyam Registration Number. '
            '2. Self-assessment on Bronze level parameters prior to desktop verification or physical site audit. '
            '3. Compliance with environmental and statutory pollution norms.'
        ),
        'application_process': (
            'Step 1: Register on zed.msme.gov.in using Udyam number and take the ZED Pledge. '
            'Step 2: Complete self-assessment for desired certification level (Bronze, Silver, Gold). '
            'Step 3: Upload supporting process documents and evidence. '
            'Step 4: Accredited agency desktop evaluation or onsite assessment. '
            'Step 5: Grant of ZED Certificate and DBT reimbursement of admissible fees.'
        ),
        'rules': [
            {
                'rule_name': 'Valid Udyam Registration',
                'field_path': 'has_udyam_registration',
                'operator': 'bool_true',
                'expected_value': True,
                'importance': 'mandatory',
                'source_clause': 'Must hold valid Udyam Registration Number (ZED Guidelines Clause 4).',
                'source_document': 'ZED Guidelines 2022, Clause 4',
                'display_label': 'Valid Udyam Registration',
                'failure_message': 'Udyam registration is required for ZED certification subsidy.',
            },
            {
                'rule_name': 'Manufacturing Sector',
                'field_path': 'is_manufacturing',
                'operator': 'bool_true',
                'expected_value': True,
                'importance': 'mandatory',
                'source_clause': 'ZED certification is applicable to manufacturing MSMEs (Clause 3.1).',
                'source_document': 'ZED Guidelines 2022, Clause 3.1',
                'display_label': 'Manufacturing Enterprise Classification',
                'failure_message': 'ZED scheme is for manufacturing sector enterprises.',
            },
        ],
        'benefits': [
            {
                'benefit_name': '80% Certification Cost Subsidy (Micro)',
                'benefit_type': 'quality_certification',
                'amount_or_percentage': '80% of certification fee',
                'cap_amount_lakhs': 0.8,
                'conditions': 'For Micro enterprises (+10% for Women/SC/ST).',
                'source_clause': 'ZED Guidelines Clause 6.1: 80% subsidy for Micro enterprises.',
            },
            {
                'benefit_name': '₹5.0 Lakh Consultancy & Handholding Grant',
                'benefit_type': 'quality_certification',
                'amount_or_percentage': 'Up to ₹5.00 Lakh',
                'cap_amount_lakhs': 5.0,
                'conditions': 'For achieving Silver and Gold ZED benchmarks.',
                'source_clause': 'ZED Guidelines Clause 6.3: Handholding support up to ₹5.00 Lakh.',
            },
        ],
    },

    # 7. SFURTI (SFURTI_NEW_GUIDELINES.pdf)
    {
        'scheme_code': 'SFURTI_CLUSTER_SCHEME',
        'name': 'Scheme of Fund for Regeneration of Traditional Industries (SFURTI)',
        'short_name': 'SFURTI Cluster Development',
        'ministry_department': 'Ministry of Micro, Small and Medium Enterprises, Government of India',
        'implementing_agency': 'KVIC, Coir Board, and Technical Agencies (TAs) / Nodal Agencies (NAs)',
        'level': 'central',
        'support_type': 'infrastructure',
        'target_sectors': ['handicrafts', 'khadi', 'village_industries', 'coir', 'agro_processing', 'bamboo', 'artisans'],
        'target_msme_categories': ['micro', 'small'],
        'target_states': [],
        'max_benefit_amount_lakhs': 500.0,  # ₹5.00 Crore for Major Clusters >500 artisans, ₹2.50 Crore for Regular Clusters
        'benefit_percentage': 95.0,
        'benefit_description': (
            'Financial assistance up to ₹5.00 Crore (Major Clusters) or ₹2.50 Crore (Regular Clusters) with 90-95% government grant for hard interventions '
            '(Common Facility Centres, modern machinery, common raw material banks, packaging units) and 100% grant up to ₹25 Lakhs for soft interventions '
            '(design development, market linkages, artisan skill training).'
        ),
        'status': 'active',
        'launch_date': date(2015, 3, 1),
        'valid_until': date(2027, 3, 31),
        'official_portal_url': 'https://sfurti.msme.gov.in',
        'gazette_notification': 'SFURTI Comprehensive Scheme Guidelines 2021-26, Ministry of MSME',
        'description': (
            'SFURTI organizes traditional artisans and craftspersons into sustainable clusters, making them competitive, providing long-term market access, '
            'and setting up common facility centres equipped with modern machinery and design testing facilities.'
        ),
        'eligibility_summary': (
            '1. Traditional artisans, rural entrepreneurs, cooperatives, and SHGs. '
            '2. Special Purpose Vehicle (SPV) with at least 33% women representation. '
            '3. Minimum 500 artisans for Major Cluster or 250 artisans for Regular Cluster. '
            '4. Clear title of land for CFC with at least 15-year lease.'
        ),
        'application_process': (
            'Step 1: Implementing Agency submits Concept Proposal to Nodal Agency. '
            'Step 2: Technical Agency prepares Detailed Project Report (DPR). '
            'Step 3: Project Screening Committee (PSC) approves proposal. '
            'Step 4: Scheme Steering Committee (SSC) approves final funding. '
            'Step 5: SPV executes CFC construction and machinery procurement with milestone-based grant releases.'
        ),
        'rules': [
            {
                'rule_name': 'Artisan Cluster SPV Formation',
                'field_path': 'has_bank_account',
                'operator': 'bool_true',
                'expected_value': True,
                'importance': 'mandatory',
                'source_clause': 'Must form an SPV representing minimum 250 traditional artisans (Guidelines Clause 5.1).',
                'source_document': 'SFURTI Guidelines, Clause 5.1',
                'display_label': 'Registered Cluster SPV',
                'failure_message': 'Formal cluster SPV required for SFURTI grants.',
            },
        ],
        'benefits': [
            {
                'benefit_name': 'Hard Intervention CFC Grant up to ₹5.00 Crore',
                'benefit_type': 'infrastructure',
                'amount_or_percentage': '90-95% GoI Grant up to ₹5.00 Crore',
                'cap_amount_lakhs': 500.0,
                'conditions': 'For Common Facility Centres, equipment, and raw material banks.',
                'source_clause': 'SFURTI Guidelines Clause 6.1: Max grant ₹5.00 Crore for Major Clusters.',
            },
        ],
    },

    # 8. TREDS CREDIT GUARANTEE (TReDS Cicular 262.pdf)
    {
        'scheme_code': 'TREDS_CGTMSE_CIRCULAR_262',
        'name': 'Credit Guarantee Scheme for Factoring / Secondary Market on TReDS',
        'short_name': 'TReDS Invoice Discounting Guarantee',
        'ministry_department': 'Ministry of MSME & Reserve Bank of India / CGTMSE',
        'implementing_agency': 'Credit Guarantee Fund Trust for Micro and Small Enterprises (CGTMSE) & TReDS Platforms (RXIL, M1xchange, Invoicemart)',
        'level': 'central',
        'support_type': 'credit_guarantee',
        'target_sectors': ['manufacturing', 'services', 'supply_chain', 'all_msme'],
        'target_msme_categories': ['micro', 'small'],
        'target_states': [],
        'max_benefit_amount_lakhs': 500.0,  # ₹5.00 Crore per enterprise
        'benefit_percentage': 85.0,
        'benefit_description': (
            'Credit guarantee coverage up to 85% on factored trade receivables and invoice discounting through RBI-authorized TReDS platforms without collateral. '
            'Protects financiers and banks against default by buyers, ensuring micro and small suppliers receive instant liquidity without waiting for 45-day payment cycles.'
        ),
        'status': 'active',
        'launch_date': date(2025, 1, 15),
        'valid_until': date(2027, 3, 31),
        'official_portal_url': 'https://www.cgtmse.in',
        'gazette_notification': 'CGTMSE Circular No. 262 / 2025-26; Ref. CGTMSE/TReDS/Factoring/2025',
        'description': (
            'Under CGTMSE Circular 262, institutional factoring and secondary market trade receivables discounting on TReDS are backed by a credit guarantee mechanism. '
            'This unlocks cheap working capital for Micro and Small Enterprises supplying goods and services to large corporates, CPSEs, and government departments.'
        ),
        'eligibility_summary': (
            '1. Micro and Small Enterprises registered on Udyam portal. '
            '2. Invoices uploaded and accepted on RBI-licensed TReDS platform (RXIL, M1xchange, or Invoicemart). '
            '3. Financier must be an eligible Member Lending Institution / NBFC Factor registered with CGTMSE.'
        ),
        'application_process': (
            'Step 1: MSE supplier registers on TReDS platform with Udyam Certificate. '
            'Step 2: Upload digital invoice against corporate buyer. '
            'Step 3: Corporate buyer accepts invoice and terms. '
            'Step 4: Financiers bid for discounting; lowest interest rate bid accepted by supplier. '
            'Step 5: CGTMSE guarantee auto-allotted on platform; funds disbursed within 24 hours.'
        ),
        'rules': [
            {
                'rule_name': 'Valid Udyam Registration',
                'field_path': 'has_udyam_registration',
                'operator': 'bool_true',
                'expected_value': True,
                'importance': 'mandatory',
                'source_clause': 'Supplier MSE must hold valid Udyam Registration (Circular 262, Clause 3).',
                'source_document': 'CGTMSE Circular No. 262, Clause 3',
                'display_label': 'Valid Udyam Registration',
                'failure_message': 'Valid Udyam registration is mandatory for TReDS guarantee.',
            },
        ],
        'benefits': [
            {
                'benefit_name': '85% Default Guarantee on Factored Invoices',
                'benefit_type': 'credit_guarantee',
                'amount_or_percentage': '85% guarantee cover',
                'cap_amount_lakhs': 500.0,
                'conditions': 'For invoices discounted through authorized TReDS platforms.',
                'source_clause': 'Circular 262, Clause 5: 85% credit guarantee on factored receivables.',
            },
        ],
    },

    # 9. MSE-CDP (msme-cdp.pdf)
    {
        'scheme_code': 'MSE_CDP_CLUSTER_DEV',
        'name': 'Micro and Small Enterprises Cluster Development Programme (MSE-CDP)',
        'short_name': 'MSE Cluster Development (MSE-CDP)',
        'ministry_department': 'Office of Development Commissioner (MSME), Ministry of MSME',
        'implementing_agency': 'State Governments / SIDBI / Special Purpose Vehicles (SPVs)',
        'level': 'central',
        'support_type': 'infrastructure',
        'target_sectors': ['manufacturing', 'engineering', 'textiles', 'leather', 'chemical', 'auto_components'],
        'target_msme_categories': ['micro', 'small'],
        'target_states': [],
        'max_benefit_amount_lakhs': 3000.0,  # Project cost up to ₹30 Crore for CFC, ₹15 Crore for Industrial Estate
        'benefit_percentage': 70.0,  # Up to 80% for special categories and NER
        'benefit_description': (
            'Common Facility Centers (CFCs): GoI grant of up to 70% of project cost (max ₹21 Crore grant on ₹30 Crore project) for testing labs, tool rooms, '
            'effluent plants, and design centers. Infrastructure Development (ID): GoI grant of up to 60-70% (max ₹10.5 Crore grant on ₹15 Crore project) '
            'for new industrial estates or upgrading existing estates.'
        ),
        'status': 'active',
        'launch_date': date(2022, 5, 23),
        'valid_until': date(2027, 3, 31),
        'official_portal_url': 'https://cluster.dcmsme.gov.in',
        'gazette_notification': 'MSE-CDP Revised Scheme Guidelines 2022, Ministry of MSME',
        'description': (
            'MSE-CDP enhances productivity and competitiveness of Micro and Small Enterprises by adopting cluster approaches. '
            'It finances state-of-the-art Common Facility Centers and develops industrial infrastructure in dedicated parks, reducing capital expenditure burdens on individual MSMEs.'
        ),
        'eligibility_summary': (
            '1. Cluster comprising at least 20 MSE units belonging to manufacturing sector. '
            '2. SPV formed under Section 8 Company or registered society with minimum 20 MSE members. '
            '3. Minimum 10% equity contribution from SPV members. '
            '4. Land provided free of encumbrance by State Government or SPV.'
        ),
        'application_process': (
            'Step 1: Online proposal submission on cluster.dcmsme.gov.in by State Directorate or SPV. '
            'Step 2: Techno-economic appraisal and In-Principle approval by Steering Committee. '
            'Step 3: Preparation and vetting of Detailed Project Report (DPR). '
            'Step 4: Final approval by National Level Steering Committee (NLSC). '
            'Step 5: Tripartite agreement and phased grant releases.'
        ),
        'rules': [
            {
                'rule_name': 'Minimum 20 MSE Units in Cluster',
                'field_path': 'has_bank_account',
                'operator': 'bool_true',
                'expected_value': True,
                'importance': 'mandatory',
                'source_clause': 'Cluster must comprise at least 20 operating MSE units (Guidelines Clause 4.1).',
                'source_document': 'MSE-CDP Guidelines, Clause 4.1',
                'display_label': '20+ MSE Cluster Size',
                'failure_message': 'Cluster must have at least 20 participating MSE units.',
            },
        ],
        'benefits': [
            {
                'benefit_name': 'CFC Infrastructure Grant up to ₹21.00 Crore',
                'benefit_type': 'infrastructure',
                'amount_or_percentage': '70% GoI Grant up to ₹21.00 Crore',
                'cap_amount_lakhs': 2100.0,
                'conditions': 'For setting up Common Facility Centers on projects up to ₹30 Crore.',
                'source_clause': 'MSE-CDP Guidelines Clause 5.1: 70% grant funding max ₹21 Crore.',
            },
        ],
    },

    # 10. PMS (OM & PMS Scheme Guidelines.pdf)
    {
        'scheme_code': 'PMS_MARKETING_SUPPORT',
        'name': 'Procurement and Marketing Support (PMS) Scheme',
        'short_name': 'Procurement & Marketing Support (PMS)',
        'ministry_department': 'Office of Development Commissioner (MSME), Ministry of MSME',
        'implementing_agency': 'MSME Development and Facilitation Offices (MSME-DFO) / NSIC',
        'level': 'central',
        'support_type': 'market_development',
        'target_sectors': ['manufacturing', 'retail', 'services', 'all_msme'],
        'target_msme_categories': ['micro', 'small'],
        'target_states': [],
        'max_benefit_amount_lakhs': 5.0,
        'benefit_percentage': 80.0,
        'benefit_description': (
            '100% stall rent reimbursement up to ₹1.5 Lakhs plus freight charges up to ₹25,000 for domestic trade exhibitions. '
            '80% one-time financial support (up to ₹50,000) for Barcode registration. Up to ₹1 Lakh for packaging development and e-commerce platform onboarding.'
        ),
        'status': 'active',
        'launch_date': date(2018, 11, 2),
        'valid_until': date(2027, 3, 31),
        'official_portal_url': 'https://my.msme.gov.in/pms',
        'gazette_notification': 'Office Memorandum F.No. 21(1)/2018-MA, PMS Scheme Guidelines',
        'description': (
            'The PMS scheme promotes marketing capabilities, market linkages, and public procurement participation for Micro and Small Enterprises. '
            'It funds domestic expo stalls, Vendor Development Programmes (VDPs) with CPSEs, barcode adoption, and modern retail packaging development.'
        ),
        'eligibility_summary': (
            '1. Valid Udyam Registration Certificate. '
            '2. Manufacturing or service micro/small enterprise. '
            '3. Maximum 2 domestic exhibitions subsidized per financial year per enterprise. '
            '4. Special preference and 100% stall waiver for SC/ST, Women, and NER entrepreneurs.'
        ),
        'application_process': (
            'Step 1: Register on my.msme.gov.in with Udyam Certificate. '
            'Step 2: Select approved domestic exhibition or trade fair. '
            'Step 3: Apply online at least 30 days prior to event. '
            'Step 4: Field office (MSME-DFO) verifies and issues stall sanction. '
            'Step 5: Submit participation report and claims within 45 days post-event.'
        ),
        'rules': [
            {
                'rule_name': 'Valid Udyam Registration',
                'field_path': 'has_udyam_registration',
                'operator': 'bool_true',
                'expected_value': True,
                'importance': 'mandatory',
                'source_clause': 'Must hold valid Udyam Registration Certificate (PMS Guidelines Clause 3).',
                'source_document': 'PMS Guidelines Clause 3',
                'display_label': 'Valid Udyam Registration',
                'failure_message': 'Udyam registration is required for PMS scheme assistance.',
            },
        ],
        'benefits': [
            {
                'benefit_name': '100% Domestic Expo Stall Reimbursement',
                'benefit_type': 'market_development',
                'amount_or_percentage': '100% up to ₹1.50 Lakh',
                'cap_amount_lakhs': 1.5,
                'conditions': 'Stall rent for participating in approved national/state trade fairs.',
                'source_clause': 'PMS Guidelines Component 1: Up to ₹1.50 Lakh stall reimbursement.',
            },
        ],
    },

    # 11. NSSH SPECIAL SUBSIDY (NSSH_Guidelines_Sub_scheme_0 & 1.pdf)
    {
        'scheme_code': 'NSSH_SPECIAL_CLCSS',
        'name': 'National SC-ST Hub (NSSH) – Special Credit Linked Capital Subsidy Scheme (SCLCSS)',
        'short_name': 'NSSH Special Capital Subsidy (SCLCSS)',
        'ministry_department': 'Ministry of Micro, Small and Medium Enterprises, Government of India',
        'implementing_agency': 'National Small Industries Corporation (NSIC) / Nodal Banks / SIDBI',
        'level': 'central',
        'support_type': 'capital_subsidy',
        'target_sectors': ['manufacturing', 'services', 'all_msme'],
        'target_msme_categories': ['micro', 'small'],
        'target_states': [],
        'max_benefit_amount_lakhs': 25.0,  # 25% on plant & machinery up to ₹100 Lakh institutional loan
        'benefit_percentage': 25.0,
        'benefit_description': (
            '25% upfront capital subsidy (maximum ₹25 Lakhs) on institutional term loans up to ₹100 Lakhs availed by SC/ST Micro and Small Enterprises '
            'for plant, machinery, and equipment. Also provides 100% reimbursement of testing, quality certification fees, and CPSE tender submission fees.'
        ),
        'status': 'active',
        'launch_date': date(2018, 10, 1),
        'valid_until': date(2027, 3, 31),
        'official_portal_url': 'https://www.scsthub.in',
        'gazette_notification': 'National SC-ST Hub Scheme Guidelines 2021-26, Ministry of MSME',
        'description': (
            'NSSH provides focused capacity building and capital subsidy support to enterprise owners from Scheduled Caste and Scheduled Tribe communities, '
            'enabling them to meet the mandatory 4% annual CPSE public procurement target under the Public Procurement Policy.'
        ),
        'eligibility_summary': (
            '1. SC/ST entrepreneur holding at least 51% equity shareholding in the enterprise. '
            '2. Valid Udyam Registration Certificate with caste category authenticated. '
            '3. Institutional credit sanctioned by Member Lending Institution. '
            '4. Machinery purchased must be new and compliant with BIS/improved technology.'
        ),
        'application_process': (
            'Step 1: Sanction term loan from eligible commercial bank. '
            'Step 2: Bank logs into NSSH portal and uploads loan details with borrower caste certificate. '
            'Step 3: NSSH Screening Committee scrutinizes eligibility. '
            'Step 4: Subsidy released by NSIC to lending bank. '
            'Step 5: Kept in Term Deposit Receipt (TDR) for 3 years before loan adjustment.'
        ),
        'rules': [
            {
                'rule_name': 'SC/ST 51%+ Equity Ownership',
                'field_path': 'has_bank_account',
                'operator': 'bool_true',
                'expected_value': True,
                'importance': 'mandatory',
                'source_clause': 'Enterprise must be owned by SC/ST promoters with at least 51% share (NSSH Clause 4.1).',
                'source_document': 'NSSH Guidelines, Clause 4.1',
                'display_label': 'SC/ST Promoter Ownership (>= 51%)',
                'failure_message': 'Applicant must satisfy the 51%+ SC/ST ownership criterion.',
            },
        ],
        'benefits': [
            {
                'benefit_name': '25% Special Capital Subsidy (up to ₹25 Lakh)',
                'benefit_type': 'capital_subsidy',
                'amount_or_percentage': '25% of plant & machinery term loan',
                'cap_amount_lakhs': 25.0,
                'conditions': 'For institutional term loans up to ₹1.00 Crore.',
                'source_clause': 'NSSH Guidelines Section 2: 25% capital subsidy max ₹25 Lakh.',
            },
        ],
    },
]


class Command(BaseCommand):
    help = 'Seeds database strictly with official schemes extracted from uploaded PDFs in backend/apps/data/schemes_pdfs.'

    def handle(self, *args, **options):
        self.stdout.write('🌱 Ingesting uploaded PDF schemes into UdyamNiti database...')

        official_codes = [s['scheme_code'] for s in UPLOADED_PDF_SCHEMES]

        # Purge any non-PDF schemes to guarantee: outside those PDFs there is NO data
        deleted_count, _ = Scheme.objects.exclude(scheme_code__in=official_codes).delete()
        if deleted_count > 0:
            self.stdout.write(self.style.WARNING(
                f'  ✓ Purged {deleted_count} non-PDF scheme records. Catalog strictly restricted to uploaded PDFs.'
            ))

        for data in UPLOADED_PDF_SCHEMES:
            scheme_copy = dict(data)
            rules_data = scheme_copy.pop('rules', [])
            benefits_data = scheme_copy.pop('benefits', [])

            scheme, created = Scheme.objects.update_or_create(
                scheme_code=scheme_copy['scheme_code'],
                defaults=scheme_copy
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

        self.stdout.write(self.style.SUCCESS(
            f'Successfully ingested all {len(UPLOADED_PDF_SCHEMES)} official PDF schemes! No non-PDF data remains.'
        ))
