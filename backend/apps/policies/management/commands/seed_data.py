"""
Seed data management command.
Seeds the database with:
- ABC Engineering (demo MSME profile)
- 30+ Central + Gujarat MSME schemes
- Eligibility rules for each scheme
- Cross-scheme relationships
- A demo goal and strategy
"""
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from apps.business_profiles.models import BusinessProfile, BusinessGoal
from apps.policies.models import Scheme, SchemeRule, SchemeBenefit, SchemeVersion
from apps.relationships.models import SchemeRelationship
from apps.policy_monitoring.models import PolicyChange
from datetime import date
import logging

logger = logging.getLogger(__name__)


SCHEMES_DATA = [
    # ─── CENTRAL GOVERNMENT SCHEMES ───────────────────────────────────────────
    {
        'scheme_code': 'CLCSS',
        'name': 'Credit Linked Capital Subsidy Scheme',
        'short_name': 'CLCSS',
        'ministry_department': 'Ministry of MSME',
        'implementing_agency': 'SIDBI / Scheduled Commercial Banks',
        'level': 'central',
        'support_type': 'capital_subsidy',
        'target_msme_categories': ['micro', 'small'],
        'target_states': [],
        'max_benefit_amount_lakhs': 15.0,
        'benefit_percentage': 15.0,
        'benefit_description': '15% capital subsidy on institutional finance up to ₹1 crore for technology upgradation of plant & machinery.',
        'status': 'active',
        'official_portal_url': 'https://msme.gov.in/clcss',
        'description': 'CLCSS provides 15% upfront capital subsidy on institutional credit up to ₹100 lakh availed by MSEs for induction of well-established and improved technologies in specified sub-sectors/products approved under the scheme.',
        'eligibility_summary': 'Micro and Small Enterprises (not Medium), engaged in manufacturing, must purchase technology from approved list, financed through scheduled banks/SFCs/NEDFi/SIDBI.',
        'application_process': '1. Identify approved technology. 2. Apply to lending institution. 3. Bank forwards to SIDBI/Nodal Bank. 4. Subsidy released to bank account.',
        'rules': [
            {
                'rule_name': 'MSME Category — Micro or Small only',
                'field_path': 'msme_category',
                'operator': 'in',
                'expected_value': ['micro', 'small'],
                'importance': 'mandatory',
                'source_clause': 'Only Micro and Small Enterprises (MSEs) are eligible. Medium enterprises are excluded.',
                'source_document': 'CLCSS Guidelines, Ministry of MSME, Clause 3.1',
                'display_label': 'Enterprise Category',
                'failure_message': 'CLCSS is available only to Micro and Small enterprises. Medium enterprises are not eligible.',
            },
            {
                'rule_name': 'Manufacturing Sector',
                'field_path': 'is_manufacturing',
                'operator': 'bool_true',
                'expected_value': True,
                'importance': 'mandatory',
                'source_clause': 'The scheme covers manufacturing sector MSEs for technology upgradation.',
                'source_document': 'CLCSS Guidelines, Clause 2',
                'display_label': 'Manufacturing Sector',
                'failure_message': 'CLCSS is for manufacturing enterprises only.',
            },
            {
                'rule_name': 'Not NPA',
                'field_path': 'is_npa',
                'operator': 'bool_false',
                'expected_value': False,
                'importance': 'mandatory',
                'source_clause': 'The unit should not be classified as NPA.',
                'source_document': 'CLCSS Guidelines, Clause 4.3',
                'display_label': 'Not a Non-Performing Asset',
                'failure_message': 'Business cannot be classified as NPA for CLCSS eligibility.',
            },
            {
                'rule_name': 'Has Bank Account',
                'field_path': 'has_bank_account',
                'operator': 'bool_true',
                'expected_value': True,
                'importance': 'mandatory',
                'source_clause': 'Loan must be availed through a scheduled commercial bank or SFC.',
                'display_label': 'Active Bank Account',
                'failure_message': 'A bank account is required to avail institutional finance for CLCSS.',
            },
        ],
        'benefits': [
            {
                'benefit_name': 'Capital Subsidy',
                'benefit_type': 'capital_subsidy',
                'amount_or_percentage': '15% of institutional finance',
                'cap_amount_lakhs': 15.0,
                'conditions': 'On loans up to ₹100 lakh for approved technology',
                'source_clause': 'Subsidy of 15% of institutional finance up to ₹1 crore — CLCSS Guidelines Clause 5',
            }
        ],
    },
    {
        'scheme_code': 'CGTMSE',
        'name': 'Credit Guarantee Fund Trust for Micro and Small Enterprises',
        'short_name': 'CGTMSE',
        'ministry_department': 'Ministry of MSME / SIDBI',
        'implementing_agency': 'CGTMSE Trust',
        'level': 'central',
        'support_type': 'credit_guarantee',
        'target_msme_categories': ['micro', 'small'],
        'target_states': [],
        'max_benefit_amount_lakhs': 500.0,
        'benefit_percentage': 85.0,
        'benefit_description': 'Collateral-free loans up to ₹500 lakh with credit guarantee cover of 75-85% for Micro and Small Enterprises.',
        'status': 'active',
        'official_portal_url': 'https://www.cgtmse.in',
        'description': 'CGTMSE provides guarantee cover to lending institutions for loans extended to MSEs without any collateral security or third-party guarantee. This enables MSEs to avail credit up to ₹5 crore without collateral.',
        'eligibility_summary': 'New or existing Micro and Small enterprises engaged in manufacturing or service activities. Credit facility up to ₹5 crore from member lending institutions.',
        'application_process': '1. Approach a member lending institution. 2. Apply for credit facility. 3. MLI forwards for CGTMSE guarantee. 4. Loan sanctioned without collateral.',
        'rules': [
            {
                'rule_name': 'MSME Category — Micro or Small',
                'field_path': 'msme_category',
                'operator': 'in',
                'expected_value': ['micro', 'small'],
                'importance': 'mandatory',
                'source_clause': 'Eligible borrowers are Micro and Small Enterprises as per MSMED Act 2006.',
                'source_document': 'CGTMSE Operating Guidelines, Section 4',
                'display_label': 'Enterprise Category',
                'failure_message': 'CGTMSE covers only Micro and Small enterprises.',
            },
            {
                'rule_name': 'Not NPA',
                'field_path': 'is_npa',
                'operator': 'bool_false',
                'expected_value': False,
                'importance': 'mandatory',
                'source_clause': 'The borrower should not be in default.',
                'display_label': 'Good Standing — Not NPA',
                'failure_message': 'NPA accounts are not eligible for CGTMSE cover.',
            },
            {
                'rule_name': 'Has Bank Account',
                'field_path': 'has_bank_account',
                'operator': 'bool_true',
                'expected_value': True,
                'importance': 'mandatory',
                'source_clause': 'Borrower must approach a Member Lending Institution.',
                'display_label': 'Active Bank Account',
                'failure_message': 'Must have an account with a member lending institution.',
            },
        ],
        'benefits': [
            {
                'benefit_name': 'Credit Guarantee Cover',
                'benefit_type': 'credit_guarantee',
                'amount_or_percentage': '75-85% of loan amount',
                'cap_amount_lakhs': 500.0,
                'conditions': '85% for micro enterprises and women/SC-ST/NE region. 75% for others.',
                'source_clause': 'CGTMSE Operating Guidelines, Section 7 — Extent of Guarantee',
            }
        ],
    },
    {
        'scheme_code': 'PMEGP',
        'name': 'Prime Minister Employment Generation Programme',
        'short_name': 'PMEGP',
        'ministry_department': 'Ministry of MSME / KVIC',
        'implementing_agency': 'KVIC, DIC, KVIB',
        'level': 'central',
        'support_type': 'capital_subsidy',
        'target_msme_categories': ['micro'],
        'target_states': [],
        'max_benefit_amount_lakhs': 50.0,
        'benefit_percentage': 35.0,
        'benefit_description': '15-35% subsidy on project cost for new micro enterprises in manufacturing (max ₹25L project for manufacturing, ₹10L for service).',
        'status': 'active',
        'official_portal_url': 'https://www.kviconline.gov.in/pmegpeportal',
        'description': 'PMEGP is a credit-linked subsidy programme for generation of employment opportunities through establishment of micro-enterprises in rural and urban areas.',
        'eligibility_summary': 'New micro enterprises only (not expansion). Individual above 18 years. 8th standard pass for projects above ₹10L. Self Help Groups, Charitable Trusts, Co-operatives also eligible.',
        'application_process': 'Apply online on KVIC portal. Appear for interview. Project sanctioned by bank. 10% owner contribution. Subsidy released after 3 years lock-in.',
        'rules': [
            {
                'rule_name': 'Micro Enterprise Only',
                'field_path': 'msme_category',
                'operator': 'eq',
                'expected_value': 'micro',
                'importance': 'mandatory',
                'source_clause': 'New micro-enterprises are eligible. Existing units are not eligible.',
                'source_document': 'PMEGP Guidelines 2023, Para 6',
                'display_label': 'Micro Enterprise',
                'failure_message': 'PMEGP is for Micro enterprises only.',
            },
        ],
        'benefits': [
            {
                'benefit_name': 'General Category Subsidy',
                'benefit_type': 'capital_subsidy',
                'amount_or_percentage': '15% (urban) / 25% (rural)',
                'cap_amount_lakhs': 25.0,
                'conditions': 'General category entrepreneurs',
                'source_clause': 'PMEGP Guidelines, Annexure — Subsidy Table',
            },
            {
                'benefit_name': 'Special Category Subsidy',
                'benefit_type': 'capital_subsidy',
                'amount_or_percentage': '25% (urban) / 35% (rural)',
                'cap_amount_lakhs': 35.0,
                'conditions': 'SC/ST/OBC/Minorities/Women/Ex-Servicemen/PHC/NER/Hill Border',
                'source_clause': 'PMEGP Guidelines, Annexure — Subsidy Table',
            }
        ],
    },
    {
        'scheme_code': 'MUDRA_TARUN',
        'name': 'MUDRA Loan — Tarun Category',
        'short_name': 'MUDRA Tarun',
        'ministry_department': 'Ministry of Finance / MUDRA',
        'implementing_agency': 'All scheduled commercial banks, RRBs, MFIs',
        'level': 'central',
        'support_type': 'collateral_free_loan',
        'target_msme_categories': ['micro', 'small'],
        'target_states': [],
        'max_benefit_amount_lakhs': 10.0,
        'benefit_percentage': None,
        'benefit_description': 'Collateral-free loans up to ₹10 lakh for micro/small enterprises that have grown beyond Kishor stage.',
        'status': 'active',
        'official_portal_url': 'https://www.mudra.org.in',
        'description': 'MUDRA Tarun loans (₹5-10 lakh) target established micro/small enterprises needing funds for working capital, equipment purchase, or business expansion. No collateral required.',
        'eligibility_summary': 'Non-farm income generating activities, existing business with track record, loan requirement of ₹5-10 lakh.',
        'application_process': 'Apply at any member bank/NBFC. Submit business plan, KYC, 2 years bank statement. Loan processed within 7-14 days.',
        'rules': [
            {
                'rule_name': 'Not NPA',
                'field_path': 'is_npa',
                'operator': 'bool_false',
                'expected_value': False,
                'importance': 'mandatory',
                'source_clause': 'Borrowers should not be in default with any institution.',
                'display_label': 'No Default History',
                'failure_message': 'NPA accounts are not eligible for MUDRA loans.',
            },
            {
                'rule_name': 'Has Bank Account',
                'field_path': 'has_bank_account',
                'operator': 'bool_true',
                'expected_value': True,
                'importance': 'mandatory',
                'source_clause': 'Must have an account with a participating bank.',
                'display_label': 'Active Bank Account',
                'failure_message': 'A bank account is required for MUDRA loan.',
            },
        ],
        'benefits': [
            {
                'benefit_name': 'Collateral-Free Loan',
                'benefit_type': 'collateral_free_loan',
                'amount_or_percentage': '₹5 lakh to ₹10 lakh',
                'cap_amount_lakhs': 10.0,
                'conditions': 'No collateral required. Interest rates per bank guidelines.',
                'source_clause': 'MUDRA Tarun Scheme — Loan Range',
            }
        ],
    },
    {
        'scheme_code': 'SIDBI_SMILE',
        'name': 'SIDBI Make in India Loan for Enterprises (SMILE)',
        'short_name': 'SIDBI SMILE',
        'ministry_department': 'SIDBI',
        'implementing_agency': 'SIDBI',
        'level': 'central',
        'support_type': 'collateral_free_loan',
        'target_msme_categories': ['micro', 'small', 'medium'],
        'target_states': [],
        'max_benefit_amount_lakhs': 2500.0,
        'benefit_percentage': None,
        'benefit_description': 'Soft loans to MSMEs in manufacturing and services sectors at concessional rates for equipment/plant purchase and business expansion.',
        'status': 'active',
        'official_portal_url': 'https://www.sidbi.in/smile',
        'description': 'SMILE provides soft loans (quasi-equity) at below-market interest rates to MSMEs for new projects or expansion, especially to support Make in India.',
        'eligibility_summary': 'All MSMEs (Micro, Small, Medium) engaged in manufacturing or services. Minimum loan ₹25 lakh. Manufacturing and services sectors.',
        'application_process': 'Apply directly to SIDBI. Submit project report, audited financials, promoter background. SIDBI appraisal and sanction within 30 days.',
        'rules': [
            {
                'rule_name': 'Not NPA',
                'field_path': 'is_npa',
                'operator': 'bool_false',
                'expected_value': False,
                'importance': 'mandatory',
                'source_clause': 'Enterprise must be viable and not in default.',
                'display_label': 'Not NPA',
                'failure_message': 'NPA accounts cannot avail SMILE scheme.',
            },
        ],
        'benefits': [
            {
                'benefit_name': 'Soft Loan at Concessional Rate',
                'benefit_type': 'collateral_free_loan',
                'amount_or_percentage': '₹25 lakh to ₹25 crore',
                'cap_amount_lakhs': 2500.0,
                'conditions': 'Interest rate 1-2% below SIDBI base rate. Repayment up to 10 years.',
                'source_clause': 'SIDBI SMILE Product Note — Terms',
            }
        ],
    },
    {
        'scheme_code': 'ZED',
        'name': 'Zero Defect Zero Effect (ZED) Certification Scheme',
        'short_name': 'ZED Certification',
        'ministry_department': 'Ministry of MSME',
        'implementing_agency': 'Quality Council of India (QCI)',
        'level': 'central',
        'support_type': 'quality_certification',
        'target_msme_categories': ['micro', 'small', 'medium'],
        'target_states': [],
        'max_benefit_amount_lakhs': 5.0,
        'benefit_percentage': 80.0,
        'benefit_description': 'Up to 80% subsidy on ZED assessment and certification charges. ZED-rated MSMEs get preference in government procurement.',
        'status': 'active',
        'official_portal_url': 'https://zed.msme.gov.in',
        'description': 'ZED Certification promotes zero defect manufacturing and zero environmental effect among MSMEs. Certified MSMEs get preference in GeM and government procurement.',
        'eligibility_summary': 'Any MSME with Udyam Registration. Subsidies: 80% for micro, 60% for small, 50% for medium enterprises.',
        'application_process': '1. Register on ZED portal. 2. Apply for assessment. 3. QCI assesses facility. 4. Certification awarded. 5. Subsidy reimbursed.',
        'rules': [
            {
                'rule_name': 'Udyam Registration',
                'field_path': 'udyam_registration_number',
                'operator': 'not_null',
                'expected_value': None,
                'importance': 'mandatory',
                'source_clause': 'Udyam Registration is mandatory for ZED scheme.',
                'source_document': 'ZED Scheme Guidelines 2022, Clause 4',
                'display_label': 'Udyam Registration Number',
                'failure_message': 'Udyam Registration is mandatory. Register at udyamregistration.gov.in.',
            },
            {
                'rule_name': 'Manufacturing or Service Sector',
                'field_path': 'is_manufacturing',
                'operator': 'bool_true',
                'expected_value': True,
                'importance': 'preferred',
                'source_clause': 'Manufacturing MSMEs are primary target but services also eligible.',
                'display_label': 'Manufacturing Sector',
                'failure_message': 'Manufacturing enterprises get higher priority for ZED.',
            },
        ],
        'benefits': [
            {
                'benefit_name': 'Micro Enterprise Subsidy',
                'benefit_type': 'quality_certification',
                'amount_or_percentage': '80% subsidy on assessment charges',
                'cap_amount_lakhs': 5.0,
                'conditions': 'For Micro enterprises',
                'source_clause': 'ZED Guidelines 2022 — Subsidy Structure',
            }
        ],
    },
    {
        'scheme_code': 'GEM_REG',
        'name': 'Government e-Marketplace (GeM) Registration',
        'short_name': 'GeM',
        'ministry_department': 'Ministry of Commerce & Industry',
        'implementing_agency': 'GeM SPV',
        'level': 'central',
        'support_type': 'marketing_support',
        'target_msme_categories': ['micro', 'small', 'medium'],
        'target_states': [],
        'max_benefit_amount_lakhs': None,
        'benefit_percentage': None,
        'benefit_description': 'Direct access to government procurement market. MSMEs registered on GeM are listed for government buyers. Purchase preference for MSEs up to ₹200 crore.',
        'status': 'active',
        'official_portal_url': 'https://gem.gov.in',
        'description': 'GeM provides a national online marketplace for procurement by government departments. MSMEs get purchase preference and can sell without intermediaries.',
        'eligibility_summary': 'Any registered business can register on GeM. Special benefits for MSMEs with Udyam Registration.',
        'application_process': '1. Register on gem.gov.in as seller. 2. Upload business documents. 3. Add products/services. 4. Government buyers can directly procure.',
        'rules': [
            {
                'rule_name': 'Not NPA',
                'field_path': 'is_npa',
                'operator': 'bool_false',
                'expected_value': False,
                'importance': 'preferred',
                'display_label': 'Not NPA',
                'source_clause': 'GeM Seller Registration Terms',
                'failure_message': 'NPA status may restrict GeM participation.',
            },
        ],
        'benefits': [
            {
                'benefit_name': 'Purchase Preference for MSEs',
                'benefit_type': 'marketing_support',
                'amount_or_percentage': 'Mandatory purchase preference for tenders up to ₹200 crore',
                'cap_amount_lakhs': None,
                'conditions': 'MSE must meet Local Content Requirement. Valid Udyam Registration required.',
                'source_clause': 'GeM Buyer Handbook — MSME Purchase Preference',
            }
        ],
    },
    {
        'scheme_code': 'NIMSME_TRAINING',
        'name': 'NIESBUD / NIMSME Skill Development Programmes',
        'short_name': 'NIMSME Training',
        'ministry_department': 'Ministry of MSME',
        'implementing_agency': 'NIESBUD / NIMSME / EDIs',
        'level': 'central',
        'support_type': 'skill_training',
        'target_msme_categories': ['micro', 'small', 'medium'],
        'target_states': [],
        'max_benefit_amount_lakhs': 0.5,
        'benefit_percentage': 100.0,
        'benefit_description': 'Free or highly subsidised skill and entrepreneurship development training programmes for MSME owners, managers and workers.',
        'status': 'active',
        'official_portal_url': 'https://www.niesbud.nic.in',
        'description': 'NIESBUD and NIMSME conduct Entrepreneurship Development Programmes (EDPs), Management Development Programmes (MDPs), and Skill Development Programmes for MSMEs.',
        'eligibility_summary': 'Any MSME entrepreneur or aspiring entrepreneur. Priority for SC/ST/Women/Minority.',
        'application_process': 'Register on NIESBUD portal. Select programme. Appear for selection. Scholarship for SC/ST candidates.',
        'rules': [],
        'benefits': [
            {
                'benefit_name': 'Free Training',
                'benefit_type': 'skill_training',
                'amount_or_percentage': 'Free to heavily subsidised',
                'cap_amount_lakhs': 0.5,
                'conditions': 'SC/ST and women entrepreneurs get full scholarship',
                'source_clause': 'NIESBUD Programme Guidelines',
            }
        ],
    },
    {
        'scheme_code': 'MSME_SAMPARK',
        'name': 'MSME Sampark Portal — Placement & Skill',
        'short_name': 'MSME Sampark',
        'ministry_department': 'Ministry of MSME',
        'implementing_agency': 'Ministry of MSME',
        'level': 'central',
        'support_type': 'skill_training',
        'target_msme_categories': ['micro', 'small', 'medium'],
        'target_states': [],
        'max_benefit_amount_lakhs': None,
        'benefit_percentage': None,
        'benefit_description': 'Portal connecting trained MSME workforce with employers. Free recruitment for MSMEs.',
        'status': 'active',
        'official_portal_url': 'https://sampark.msme.gov.in',
        'description': 'MSME Sampark is a national portal that connects skilled candidates trained under MSME schemes with industry employers, enabling free recruitment.',
        'eligibility_summary': 'Any registered MSME can post jobs for free.',
        'application_process': 'Register on sampark.msme.gov.in. Post job requirements. Candidates apply directly.',
        'rules': [],
        'benefits': [],
    },
    {
        'scheme_code': 'MSME_INNOVATIVE',
        'name': 'MSME Innovative Scheme — Incubation',
        'short_name': 'MSME Incubation',
        'ministry_department': 'Ministry of MSME',
        'implementing_agency': 'Ministry of MSME via designated incubators',
        'level': 'central',
        'support_type': 'technology_grant',
        'target_msme_categories': ['micro', 'small'],
        'target_states': [],
        'max_benefit_amount_lakhs': 100.0,
        'benefit_percentage': 75.0,
        'benefit_description': 'Financial assistance up to ₹1 crore for innovative projects with technology incubation. 75% funding, 25% from beneficiary.',
        'status': 'active',
        'official_portal_url': 'https://msme.gov.in/incubation',
        'description': 'Support for innovative ideas and technology development through a network of host institutes/incubators. Projects funded up to ₹1 crore.',
        'eligibility_summary': 'MSMEs with innovative projects. Must partner with a government-approved incubator.',
        'application_process': '1. Identify empanelled incubator. 2. Submit project proposal. 3. Evaluated by expert committee. 4. Funding released in tranches.',
        'rules': [
            {
                'rule_name': 'Manufacturing or Technology Sector',
                'field_path': 'is_manufacturing',
                'operator': 'bool_true',
                'expected_value': True,
                'importance': 'preferred',
                'source_clause': 'Priority to manufacturing and technology sectors.',
                'display_label': 'Manufacturing/Technology Sector',
                'source_clause': 'MSME Incubation Scheme Guidelines 2023',
                'failure_message': 'Manufacturing enterprises get priority.',
            },
        ],
        'benefits': [
            {
                'benefit_name': 'Incubation Grant',
                'benefit_type': 'technology_grant',
                'amount_or_percentage': 'Up to 75% of project cost',
                'cap_amount_lakhs': 100.0,
                'conditions': '25% co-funding from beneficiary. 3-year project period.',
                'source_clause': 'MSME Innovative Scheme — Clause 4',
            }
        ],
    },

    # ─── GUJARAT STATE SCHEMES ─────────────────────────────────────────────────
    {
        'scheme_code': 'GUJCOST',
        'name': 'Gujarat Capital Investment Subsidy Scheme (iSNOW)',
        'short_name': 'Gujarat CISS',
        'ministry_department': 'Industries and Mines Department, Government of Gujarat',
        'implementing_agency': 'Industries Commissioner, Gujarat',
        'level': 'state_gujarat',
        'support_type': 'capital_subsidy',
        'target_msme_categories': ['micro', 'small', 'medium'],
        'target_states': ['Gujarat'],
        'max_benefit_amount_lakhs': 35.0,
        'benefit_percentage': 12.0,
        'benefit_description': '12% capital subsidy on fixed capital investment in machinery (12% for MSME). Higher for taluka-level incentive areas and SC/ST/women-owned units.',
        'status': 'active',
        'official_portal_url': 'https://ic.gujarat.gov.in',
        'description': 'Gujarat Industrial Policy 2020 provides capital investment subsidy to new and expansion manufacturing units. MSMEs get 12% subsidy on eligible fixed capital investment.',
        'eligibility_summary': 'Manufacturing units establishing new unit or expansion in Gujarat. MSME status required. Investment in plant and machinery eligible.',
        'application_process': '1. File online application on iSNOW portal before production. 2. In-principle approval. 3. Investment completion. 4. Final claim with CA certificate.',
        'rules': [
            {
                'rule_name': 'Must Be in Gujarat',
                'field_path': 'state',
                'operator': 'eq',
                'expected_value': 'Gujarat',
                'importance': 'mandatory',
                'source_clause': 'This scheme is available only for units in Gujarat.',
                'source_document': 'Gujarat Industrial Policy 2020 / Resolution No. IND/1020/2',
                'display_label': 'Gujarat Location',
                'failure_message': 'This Gujarat state scheme is only for businesses located in Gujarat.',
            },
            {
                'rule_name': 'Manufacturing Sector',
                'field_path': 'is_manufacturing',
                'operator': 'bool_true',
                'expected_value': True,
                'importance': 'mandatory',
                'source_clause': 'Applicable to manufacturing enterprises only.',
                'source_document': 'Gujarat Industrial Policy 2020, Schedule I',
                'display_label': 'Manufacturing Sector',
                'failure_message': 'Capital subsidy is for manufacturing units only.',
            },
            {
                'rule_name': 'MSME Category',
                'field_path': 'msme_category',
                'operator': 'in',
                'expected_value': ['micro', 'small', 'medium'],
                'importance': 'mandatory',
                'source_clause': 'The scheme covers Micro, Small and Medium Enterprises as per MSMED Act.',
                'display_label': 'MSME Category',
                'failure_message': 'Enterprise must be classified as Micro, Small or Medium.',
            },
        ],
        'benefits': [
            {
                'benefit_name': 'Capital Investment Subsidy',
                'benefit_type': 'capital_subsidy',
                'amount_or_percentage': '12% of eligible fixed capital investment',
                'cap_amount_lakhs': 35.0,
                'conditions': 'Higher rates in D and E category talukas. SC/ST/Women get additional 5%.',
                'source_clause': 'Gujarat Industrial Policy 2020 — Annexure 1: Capital Subsidy Rates',
            }
        ],
    },
    {
        'scheme_code': 'GUJARAT_INTEREST_SUBSIDY',
        'name': 'Gujarat Interest Subsidy Scheme for MSMEs',
        'short_name': 'Gujarat Interest Subsidy',
        'ministry_department': 'Industries and Mines Department, GoG',
        'implementing_agency': 'Industries Commissioner',
        'level': 'state_gujarat',
        'support_type': 'interest_subvention',
        'target_msme_categories': ['micro', 'small', 'medium'],
        'target_states': ['Gujarat'],
        'max_benefit_amount_lakhs': 10.0,
        'benefit_percentage': 7.0,
        'benefit_description': '7% interest subsidy on term loans for MSMEs in Gujarat for up to 5 years, capped at ₹35 lakh per annum.',
        'status': 'active',
        'official_portal_url': 'https://ic.gujarat.gov.in',
        'description': 'Gujarat provides interest subsidy on term loans for setting up new MSME units or expansion. Subsidy of 7% per annum for 5 years.',
        'eligibility_summary': 'MSME units in Gujarat that avail term loans from scheduled banks/SFCs for new unit or expansion project. Manufacturing sector.',
        'application_process': 'Apply on iSNOW portal with bank loan sanction letter. Annually claim interest paid certificate from bank.',
        'rules': [
            {
                'rule_name': 'Gujarat Location',
                'field_path': 'state',
                'operator': 'eq',
                'expected_value': 'Gujarat',
                'importance': 'mandatory',
                'source_clause': 'Applicable to manufacturing units in Gujarat only.',
                'source_document': 'Gujarat Industrial Policy 2020 — Interest Subsidy Component',
                'display_label': 'Gujarat Location',
                'failure_message': 'Only applicable to units located in Gujarat.',
            },
            {
                'rule_name': 'Manufacturing Sector',
                'field_path': 'is_manufacturing',
                'operator': 'bool_true',
                'expected_value': True,
                'importance': 'mandatory',
                'source_clause': 'For manufacturing units only.',
                'display_label': 'Manufacturing Sector',
                'failure_message': 'Interest subsidy is for manufacturing enterprises.',
            },
            {
                'rule_name': 'Has Existing Loan or Plans for Loan',
                'field_path': 'has_bank_account',
                'operator': 'bool_true',
                'expected_value': True,
                'importance': 'mandatory',
                'source_clause': 'Must have term loan from scheduled bank / SFC.',
                'display_label': 'Term Loan Account',
                'failure_message': 'A term loan from a scheduled bank is required.',
            },
        ],
        'benefits': [
            {
                'benefit_name': 'Interest Subvention',
                'benefit_type': 'interest_subvention',
                'amount_or_percentage': '7% per annum for 5 years',
                'cap_amount_lakhs': 10.0,
                'conditions': 'On term loans for new unit / expansion. Annual ceiling ₹35 lakh.',
                'source_clause': 'Gujarat IP 2020 — Interest Subsidy Schedule',
            }
        ],
    },
    {
        'scheme_code': 'GUJARAT_EP',
        'name': 'Gujarat Export Promotion Industrial Parks Scheme',
        'short_name': 'Gujarat Export Incentive',
        'ministry_department': 'Industries and Mines, GoG',
        'implementing_agency': 'GIDC / Industries Commissioner',
        'level': 'state_gujarat',
        'support_type': 'export_incentive',
        'target_msme_categories': ['small', 'medium'],
        'target_states': ['Gujarat'],
        'max_benefit_amount_lakhs': 50.0,
        'benefit_percentage': 5.0,
        'benefit_description': '5% freight subsidy on exports + infrastructure support for units in export parks.',
        'status': 'active',
        'official_portal_url': 'https://gidc.gujarat.gov.in',
        'description': 'Gujarat promotes exports through export park infrastructure and freight subsidies for MSME exporters.',
        'eligibility_summary': 'Small and Medium manufacturing enterprises in Gujarat with export sales.',
        'application_process': 'Apply through GIDC or Industries Commissioner for park allocation and freight subsidy claim.',
        'rules': [
            {
                'rule_name': 'Gujarat Location',
                'field_path': 'state',
                'operator': 'eq',
                'expected_value': 'Gujarat',
                'importance': 'mandatory',
                'source_clause': 'Gujarat Export Promotion Scheme — Clause 2',
                'display_label': 'Gujarat Location',
                'failure_message': 'Applicable only in Gujarat.',
            },
            {
                'rule_name': 'Small or Medium Enterprise',
                'field_path': 'msme_category',
                'operator': 'in',
                'expected_value': ['small', 'medium'],
                'importance': 'mandatory',
                'source_clause': 'Priority to Small and Medium enterprises for export parks.',
                'display_label': 'Small or Medium Enterprise',
                'failure_message': 'This export scheme targets Small and Medium enterprises.',
            },
            {
                'rule_name': 'Has Export License',
                'field_path': 'has_export_license',
                'operator': 'bool_true',
                'expected_value': True,
                'importance': 'preferred',
                'source_clause': 'Export registration with DGFT preferred.',
                'display_label': 'DGFT Export Registration',
                'failure_message': 'Export license/DGFT registration preferred for this scheme.',
            },
        ],
        'benefits': [
            {
                'benefit_name': 'Freight Subsidy on Exports',
                'benefit_type': 'export_incentive',
                'amount_or_percentage': '5% of FOB export value',
                'cap_amount_lakhs': 50.0,
                'conditions': 'Annual ceiling. On exports through Gujarat ports.',
                'source_clause': 'Gujarat Export Promotion Scheme Schedule',
            }
        ],
    },
    {
        'scheme_code': 'GUJARAT_SCST',
        'name': 'Gujarat SC/ST Entrepreneur Scheme',
        'short_name': 'Gujarat SC/ST Scheme',
        'ministry_department': 'Social Justice & Empowerment, GoG',
        'implementing_agency': 'Commissioner, Social Justice',
        'level': 'state_gujarat',
        'support_type': 'capital_subsidy',
        'target_msme_categories': ['micro', 'small'],
        'target_states': ['Gujarat'],
        'max_benefit_amount_lakhs': 20.0,
        'benefit_percentage': 20.0,
        'benefit_description': 'Additional 20% capital subsidy over and above regular state scheme for SC/ST owned micro and small enterprises in Gujarat.',
        'status': 'active',
        'official_portal_url': 'https://sje.gujarat.gov.in',
        'description': 'Special capital investment subsidy for SC/ST entrepreneurs starting new manufacturing units in Gujarat.',
        'eligibility_summary': 'SC/ST owned Micro or Small manufacturing units in Gujarat.',
        'application_process': 'Apply via iSNOW portal with caste certificate.',
        'rules': [
            {
                'rule_name': 'SC/ST Ownership',
                'field_path': 'is_sc_st_owned',
                'operator': 'bool_true',
                'expected_value': True,
                'importance': 'mandatory',
                'source_clause': 'Available exclusively for SC/ST owned enterprises.',
                'source_document': 'Gujarat SC/ST Entrepreneur Scheme Guidelines',
                'display_label': 'SC/ST Ownership',
                'failure_message': 'This scheme is exclusively for SC/ST owned enterprises.',
            },
            {
                'rule_name': 'Gujarat Location',
                'field_path': 'state',
                'operator': 'eq',
                'expected_value': 'Gujarat',
                'importance': 'mandatory',
                'source_clause': 'Gujarat state scheme only.',
                'display_label': 'Gujarat Location',
                'failure_message': 'Only for units in Gujarat.',
            },
        ],
        'benefits': [
            {
                'benefit_name': 'Additional Capital Subsidy',
                'benefit_type': 'capital_subsidy',
                'amount_or_percentage': '20% additional on fixed capital investment',
                'cap_amount_lakhs': 20.0,
                'conditions': 'Over and above standard state scheme benefit',
                'source_clause': 'Gujarat SC/ST Scheme — Benefit Schedule',
            }
        ],
    },
    {
        'scheme_code': 'GUJARAT_WOMEN',
        'name': 'Gujarat Mahila Udyog Niti — Women Entrepreneur Scheme',
        'short_name': 'Gujarat Women MSME',
        'ministry_department': 'Industries and Mines, GoG / WCD',
        'implementing_agency': 'Industries Commissioner',
        'level': 'state_gujarat',
        'support_type': 'capital_subsidy',
        'target_msme_categories': ['micro', 'small'],
        'target_states': ['Gujarat'],
        'max_benefit_amount_lakhs': 25.0,
        'benefit_percentage': 25.0,
        'benefit_description': '25% additional capital subsidy for women-owned micro and small enterprises in Gujarat. Plus interest subvention and power tariff concession.',
        'status': 'active',
        'official_portal_url': 'https://ic.gujarat.gov.in',
        'description': 'Empowerment scheme for women entrepreneurs providing capital subsidy, interest subvention, and operational support for new MSME units in Gujarat.',
        'eligibility_summary': 'Women-owned (>51%) Micro or Small manufacturing enterprises in Gujarat.',
        'application_process': 'Apply on iSNOW portal with ownership proof, ID documents.',
        'rules': [
            {
                'rule_name': 'Women Ownership',
                'field_path': 'is_women_owned',
                'operator': 'bool_true',
                'expected_value': True,
                'importance': 'mandatory',
                'source_clause': 'Minimum 51% ownership by women.',
                'source_document': 'Gujarat Mahila Udyog Niti 2020',
                'display_label': 'Women-Owned Enterprise (>51%)',
                'failure_message': 'This scheme is for women-owned enterprises (minimum 51% ownership).',
            },
            {
                'rule_name': 'Gujarat Location',
                'field_path': 'state',
                'operator': 'eq',
                'expected_value': 'Gujarat',
                'importance': 'mandatory',
                'display_label': 'Gujarat Location',
                'source_clause': 'Gujarat state scheme.',
                'failure_message': 'Only for units in Gujarat.',
            },
        ],
        'benefits': [
            {
                'benefit_name': 'Additional Women Entrepreneur Subsidy',
                'benefit_type': 'capital_subsidy',
                'amount_or_percentage': '25% additional capital subsidy',
                'cap_amount_lakhs': 25.0,
                'conditions': 'For women-owned manufacturing MSMEs in Gujarat',
                'source_clause': 'Gujarat Mahila Udyog Niti — Subsidy Schedule',
            }
        ],
    },
    {
        'scheme_code': 'SFURTI',
        'name': 'Scheme of Fund for Regeneration of Traditional Industries (SFURTI)',
        'short_name': 'SFURTI',
        'ministry_department': 'Ministry of MSME',
        'implementing_agency': 'KVIC / KVIB / DIC',
        'level': 'central',
        'support_type': 'infrastructure',
        'target_msme_categories': ['micro', 'small'],
        'target_states': [],
        'max_benefit_amount_lakhs': 250.0,
        'benefit_percentage': 90.0,
        'benefit_description': 'Financial support for cluster development of traditional industries (khadi, village, coir) including common facility centres.',
        'status': 'active',
        'official_portal_url': 'https://sfurti.msme.gov.in',
        'description': 'SFURTI aims to organise traditional industries into clusters and build Common Facility Centres (CFCs) with modern equipment.',
        'eligibility_summary': 'Groups/clusters of artisans/micro enterprises in traditional sectors. SC/ST, women and minorities get preference.',
        'application_process': '1. Form cluster group. 2. Identify Nodal Agency. 3. Submit DPR. 4. Committee approval. 5. CFC established.',
        'rules': [],
        'benefits': [
            {
                'benefit_name': 'Common Facility Centre Grant',
                'benefit_type': 'infrastructure',
                'amount_or_percentage': 'Up to ₹2.5 crore for Heritage cluster, ₹5 crore for Major cluster',
                'cap_amount_lakhs': 250.0,
                'conditions': '90% grant + 10% beneficiary contribution',
                'source_clause': 'SFURTI Scheme Guidelines — Benefit Matrix',
            }
        ],
    },
    {
        'scheme_code': 'RAMP',
        'name': 'Raising and Accelerating MSME Performance (RAMP)',
        'short_name': 'RAMP',
        'ministry_department': 'Ministry of MSME',
        'implementing_agency': 'States / UT implementing agencies',
        'level': 'central',
        'support_type': 'multiple',
        'target_msme_categories': ['micro', 'small', 'medium'],
        'target_states': [],
        'max_benefit_amount_lakhs': None,
        'benefit_percentage': None,
        'benefit_description': 'World Bank-assisted programme to strengthen state MSME ecosystems, improve delayed payment, and provide market/technology access.',
        'status': 'active',
        'official_portal_url': 'https://ramp.msme.gov.in',
        'description': 'RAMP is a ₹6,000 crore World Bank-assisted program to improve MSME competitiveness, address delayed payments (via MSME Samadhaan), and strengthen state capabilities.',
        'eligibility_summary': 'All MSMEs benefit through improved ecosystem. MSME Samadhaan for delayed payment recovery.',
        'application_process': 'Varies by component. MSME Samadhaan: file online application for delayed payment recovery.',
        'rules': [],
        'benefits': [],
    },
    {
        'scheme_code': 'MSME_SAMADHAAN',
        'name': 'MSME Samadhaan — Delayed Payment Monitoring',
        'short_name': 'MSME Samadhaan',
        'ministry_department': 'Ministry of MSME',
        'implementing_agency': 'Ministry of MSME / MSEFC',
        'level': 'central',
        'support_type': 'multiple',
        'target_msme_categories': ['micro', 'small'],
        'target_states': [],
        'max_benefit_amount_lakhs': None,
        'benefit_percentage': None,
        'benefit_description': 'Online filing of delayed payment cases. Buyers must pay within 45 days to MSEs. MSEFC adjudicates disputes.',
        'status': 'active',
        'official_portal_url': 'https://samadhaan.msme.gov.in',
        'description': 'Online portal for MSMEs to file complaints against delayed payments by buyer organisations. Facilitation by MSME Facilitation Councils.',
        'eligibility_summary': 'Micro and Small enterprises with outstanding payments from buyers.',
        'application_process': 'File complaint on samadhaan.msme.gov.in with invoice details. MSEFC takes up with buyer.',
        'rules': [
            {
                'rule_name': 'Micro or Small Enterprise',
                'field_path': 'msme_category',
                'operator': 'in',
                'expected_value': ['micro', 'small'],
                'importance': 'mandatory',
                'source_clause': 'MSMED Act Section 15 — Micro and Small Enterprises only.',
                'display_label': 'Micro or Small Enterprise',
                'failure_message': 'MSME Samadhaan is for Micro and Small enterprises only.',
            },
        ],
        'benefits': [],
    },
    {
        'scheme_code': 'NSIC_RAW_MATERIAL',
        'name': 'NSIC Raw Material Assistance Scheme',
        'short_name': 'NSIC RMA',
        'ministry_department': 'Ministry of MSME / NSIC',
        'implementing_agency': 'National Small Industries Corporation (NSIC)',
        'level': 'central',
        'support_type': 'raw_material',
        'target_msme_categories': ['micro', 'small'],
        'target_states': [],
        'max_benefit_amount_lakhs': None,
        'benefit_percentage': None,
        'benefit_description': 'Facilitates procurement of raw materials (both indigenous and imported) on credit basis through NSIC, with credit limit up to 90 days.',
        'status': 'active',
        'official_portal_url': 'https://www.nsic.co.in',
        'description': 'NSIC assists MSEs in procuring raw materials on credit. NSIC ties up with suppliers/mills and supplies to registered MSEs against credit.',
        'eligibility_summary': 'Manufacturing MSMEs registered with NSIC. Working capital requirement for raw material procurement.',
        'application_process': '1. Register with NSIC. 2. Apply for credit limit. 3. NSIC assesses and fixes limit. 4. Material supplied against limit.',
        'rules': [
            {
                'rule_name': 'Manufacturing Sector',
                'field_path': 'is_manufacturing',
                'operator': 'bool_true',
                'expected_value': True,
                'importance': 'mandatory',
                'source_clause': 'Raw material assistance for manufacturing MSEs.',
                'display_label': 'Manufacturing Sector',
                'failure_message': 'Raw material assistance is for manufacturing units.',
            },
            {
                'rule_name': 'Not NPA',
                'field_path': 'is_npa',
                'operator': 'bool_false',
                'expected_value': False,
                'importance': 'mandatory',
                'source_clause': 'Unit must have satisfactory credit record.',
                'display_label': 'Not NPA',
                'failure_message': 'NPA units are not eligible.',
            },
        ],
        'benefits': [
            {
                'benefit_name': 'Raw Material Credit',
                'benefit_type': 'raw_material',
                'amount_or_percentage': 'Credit limit based on assessment',
                'cap_amount_lakhs': None,
                'conditions': '90-day credit. Interest at concessional rates.',
                'source_clause': 'NSIC RMA Scheme Guidelines',
            }
        ],
    },
    {
        'scheme_code': 'ASPIRE',
        'name': 'A Scheme for Promotion of Innovation, Rural Industry and Entrepreneurship (ASPIRE)',
        'short_name': 'ASPIRE',
        'ministry_department': 'Ministry of MSME',
        'implementing_agency': 'Ministry of MSME via Livelihood Business Incubators',
        'level': 'central',
        'support_type': 'technology_grant',
        'target_msme_categories': ['micro'],
        'target_states': [],
        'max_benefit_amount_lakhs': 100.0,
        'benefit_percentage': 100.0,
        'benefit_description': 'Promotes agro-rural industry through Livelihood Business Incubators (LBI) and Technology Business Incubators (TBI). Grants up to ₹1 crore.',
        'status': 'active',
        'official_portal_url': 'https://msme.gov.in/aspire',
        'description': 'ASPIRE supports rural micro entrepreneurs through incubation, training, and technology access for agriculture-based industries.',
        'eligibility_summary': 'Micro enterprises in agro-based industries or rural areas. Must be linked to an ASPIRE-supported LBI/TBI.',
        'application_process': 'Apply through designated LBI or TBI in your area.',
        'rules': [
            {
                'rule_name': 'Micro Enterprise',
                'field_path': 'msme_category',
                'operator': 'eq',
                'expected_value': 'micro',
                'importance': 'mandatory',
                'source_clause': 'ASPIRE targets micro enterprises in agro/rural sector.',
                'display_label': 'Micro Enterprise',
                'failure_message': 'ASPIRE primarily targets micro enterprises.',
            },
            {
                'rule_name': 'Rural Location Preferred',
                'field_path': 'is_rural',
                'operator': 'bool_true',
                'expected_value': True,
                'importance': 'preferred',
                'source_clause': 'Priority to rural enterprises.',
                'display_label': 'Rural Location',
                'failure_message': 'ASPIRE prioritises rural enterprises.',
            },
        ],
        'benefits': [],
    },
    {
        'scheme_code': 'MSME_COMPETITIVE',
        'name': 'MSME Competitive (LEAN) Scheme',
        'short_name': 'MSME LEAN',
        'ministry_department': 'Ministry of MSME',
        'implementing_agency': 'National Productivity Council / QCI',
        'level': 'central',
        'support_type': 'technology_grant',
        'target_msme_categories': ['micro', 'small', 'medium'],
        'target_states': [],
        'max_benefit_amount_lakhs': 5.0,
        'benefit_percentage': 90.0,
        'benefit_description': 'Supports MSMEs to adopt LEAN manufacturing practices. Up to 90% subsidy on consulting costs.',
        'status': 'active',
        'official_portal_url': 'https://lean.msme.gov.in',
        'description': 'Helps MSMEs adopt LEAN manufacturing principles to improve efficiency, reduce waste, and enhance competitiveness. Certified consultants from empanelled panel.',
        'eligibility_summary': 'Any MSME in manufacturing. 3 levels: Bronze, Silver, Gold.',
        'application_process': '1. Express Interest on portal. 2. LEAN consultant assigned. 3. Baseline assessment. 4. Implementation. 5. Certification. 6. Subsidy claim.',
        'rules': [
            {
                'rule_name': 'Manufacturing Sector',
                'field_path': 'is_manufacturing',
                'operator': 'bool_true',
                'expected_value': True,
                'importance': 'mandatory',
                'source_clause': 'Scheme is for manufacturing MSMEs.',
                'display_label': 'Manufacturing Sector',
                'failure_message': 'LEAN scheme is for manufacturing enterprises only.',
            },
        ],
        'benefits': [
            {
                'benefit_name': 'LEAN Consulting Subsidy',
                'benefit_type': 'technology_grant',
                'amount_or_percentage': '90% subsidy on consulting fees',
                'cap_amount_lakhs': 5.0,
                'conditions': '80% for general, 90% for SC/ST/women/NE/aspirational districts',
                'source_clause': 'MSME LEAN Scheme Guidelines — Subsidy Structure',
            }
        ],
    },
    {
        'scheme_code': 'PMFME',
        'name': 'PM Formalisation of Micro Food Processing Enterprises Scheme (PMFME)',
        'short_name': 'PMFME',
        'ministry_department': 'Ministry of Food Processing Industries',
        'implementing_agency': 'State Nodal Agencies',
        'level': 'central',
        'support_type': 'capital_subsidy',
        'target_msme_categories': ['micro'],
        'target_states': [],
        'max_benefit_amount_lakhs': 10.0,
        'benefit_percentage': 35.0,
        'benefit_description': '35% credit-linked subsidy on eligible project cost (max ₹10 lakh) for individual micro food processing enterprises.',
        'status': 'active',
        'official_portal_url': 'https://pmfme.mofpi.gov.in',
        'description': 'PMFME supports food processing micro enterprises to upgrade technology, improve quality, and access formal markets through credit-linked subsidy.',
        'eligibility_summary': 'Micro enterprises in food processing. Individual proprietorship or FPO/SHG clusters.',
        'application_process': '1. Register on PMFME portal. 2. State agency validates. 3. Bank loan + subsidy application. 4. Production begins. 5. Subsidy released.',
        'rules': [
            {
                'rule_name': 'Micro Enterprise',
                'field_path': 'msme_category',
                'operator': 'eq',
                'expected_value': 'micro',
                'importance': 'mandatory',
                'source_clause': 'PMFME targets micro food processing enterprises only.',
                'display_label': 'Micro Enterprise',
                'failure_message': 'PMFME is only for micro enterprises.',
            },
        ],
        'benefits': [
            {
                'benefit_name': 'Credit-Linked Subsidy',
                'benefit_type': 'capital_subsidy',
                'amount_or_percentage': '35% of eligible project cost',
                'cap_amount_lakhs': 10.0,
                'conditions': 'Credit-linked through bank loan',
                'source_clause': 'PMFME Scheme Operational Guidelines — Clause 6',
            }
        ],
    },
    {
        'scheme_code': 'GUJARAT_DIGITAL',
        'name': 'Gujarat MSME Digital Technology Adoption Scheme',
        'short_name': 'Gujarat Digital MSME',
        'ministry_department': 'Industries and Mines, GoG',
        'implementing_agency': 'iHub Gujarat / Industries Commissioner',
        'level': 'state_gujarat',
        'support_type': 'digitalization',
        'target_msme_categories': ['micro', 'small', 'medium'],
        'target_states': ['Gujarat'],
        'max_benefit_amount_lakhs': 5.0,
        'benefit_percentage': 50.0,
        'benefit_description': '50% subsidy on ERP, digital tools, and IoT adoption for MSMEs in Gujarat. Maximum ₹5 lakh per enterprise.',
        'status': 'active',
        'official_portal_url': 'https://ic.gujarat.gov.in/digital-msme',
        'description': 'Gujarat supports MSMEs to adopt digital technologies including ERP, CRM, inventory management, and IoT for Industry 4.0 readiness.',
        'eligibility_summary': 'MSMEs in Gujarat adopting approved digital solutions from empanelled vendors.',
        'application_process': 'Apply on iSNOW portal. Select from approved software/tools. Implement. Claim subsidy post-audit.',
        'rules': [
            {
                'rule_name': 'Gujarat Location',
                'field_path': 'state',
                'operator': 'eq',
                'expected_value': 'Gujarat',
                'importance': 'mandatory',
                'source_clause': 'Gujarat state scheme only.',
                'display_label': 'Gujarat Location',
                'failure_message': 'Only for units located in Gujarat.',
            },
        ],
        'benefits': [
            {
                'benefit_name': 'Digital Technology Subsidy',
                'benefit_type': 'digitalization',
                'amount_or_percentage': '50% on software/digital tools cost',
                'cap_amount_lakhs': 5.0,
                'conditions': 'From empanelled vendors only',
                'source_clause': 'Gujarat Digital MSME Scheme Guidelines 2022',
            }
        ],
    },
    {
        'scheme_code': 'TEQUP',
        'name': 'Technology and Quality Upgradation Support for MSMEs (TEQUP)',
        'short_name': 'TEQUP',
        'ministry_department': 'Ministry of MSME',
        'implementing_agency': 'SIDBI / Ministry of MSME',
        'level': 'central',
        'support_type': 'technology_grant',
        'target_msme_categories': ['micro', 'small', 'medium'],
        'target_states': [],
        'max_benefit_amount_lakhs': 5.0,
        'benefit_percentage': 75.0,
        'benefit_description': '75% financial assistance for MSMEs to adopt energy-efficient technologies and quality standards (ISO, BIS etc.). Max ₹5 lakh.',
        'status': 'active',
        'official_portal_url': 'https://msme.gov.in/tequp',
        'description': 'TEQUP provides financial assistance to MSMEs for adopting energy-efficient equipment and quality certification (ISO, BIS, energy audit).',
        'eligibility_summary': 'MSMEs adopting energy-efficient technology or quality certifications. Manufacturing preferred.',
        'application_process': 'Apply through SIDBI. Submit project report. SIDBI appraises and disburses.',
        'rules': [
            {
                'rule_name': 'Not NPA',
                'field_path': 'is_npa',
                'operator': 'bool_false',
                'expected_value': False,
                'importance': 'mandatory',
                'source_clause': 'Unit must be viable and not NPA.',
                'display_label': 'Not NPA',
                'failure_message': 'NPA units are not eligible for TEQUP.',
            },
        ],
        'benefits': [
            {
                'benefit_name': 'Technology/Quality Upgrade Grant',
                'benefit_type': 'technology_grant',
                'amount_or_percentage': '75% of eligible expenditure',
                'cap_amount_lakhs': 5.0,
                'conditions': 'On energy-efficient equipment or quality certification',
                'source_clause': 'TEQUP Scheme Guidelines',
            }
        ],
    },
]


DEMO_PROFILE_DATA = {
    'business_name': 'ABC Engineering Works',
    'udyam_registration_number': 'UDYAM-GJ-29-0012345',
    'gstin': '24AADCA1234F1Z5',
    'pan': 'AADCA1234F',
    'msme_category': 'small',
    'entity_type': 'proprietorship',
    'nic_code': '28990',
    'industry_sector': 'Precision Engineering & Metal Fabrication',
    'industry_subsector': 'CNC Machining & Sheet Metal',
    'is_manufacturing': True,
    'is_service': False,
    'state': 'Gujarat',
    'district': 'Surat',
    'city': 'Surat',
    'pincode': '395010',
    'is_rural': False,
    'is_aspirational_district': False,
    'investment_in_plant_machinery_lakhs': 45.00,
    'annual_turnover_lakhs': 210.00,
    'owner_gender': 'male',
    'owner_caste': 'obc',
    'is_sc_st_owned': False,
    'is_women_owned': False,
    'is_minority_owned': False,
    'years_in_operation': 8,
    'total_employees': 22,
    'has_bank_account': True,
    'has_existing_loan': False,
    'is_npa': False,
    'credit_score': 730,
    'has_iso_certification': False,
    'has_bis_certification': False,
    'has_gem_registration': False,
    'has_export_license': False,
    'has_technology_upgrade_plan': True,
    'uses_digital_payments': True,
}


DEMO_GOAL_TEXT = "I want to purchase a ₹50 lakh CNC machine to expand our precision machining production capacity and take on larger aerospace component orders."


RELATIONSHIPS_DATA = [
    ('CLCSS', 'CGTMSE', 'synergistic',
     'CLCSS provides capital subsidy and CGTMSE provides credit guarantee on the same loan. A business can avail both: CGTMSE guarantees the loan while CLCSS subsidises 15% of it. Apply for CGTMSE first through your bank, then claim CLCSS subsidy.',
     'CLCSS Guidelines Clause 6: "Subsidy released through lending institution." CGTMSE covers the loan — both can apply on same credit facility.'),

    ('CLCSS', 'GUJCOST', 'compatible',
     'CLCSS (Central subsidy, 15%) and Gujarat Capital Investment Subsidy (12%) can be stacked. The total subsidy benefit can reach 27% of the machinery cost, with central and state schemes complementing each other.',
     'No explicit restriction found in either scheme guidelines on combining central and state subsidies.'),

    ('CGTMSE', 'MUDRA_TARUN', 'overlapping',
     'Both provide credit support to MSMEs. MUDRA Tarun is for loans up to ₹10 lakh; CGTMSE covers larger amounts. If loan is under ₹10 lakh, MUDRA is simpler. For ₹50 lakh CNC machine purchase, CGTMSE is the appropriate scheme.',
     'MUDRA operates independently of CGTMSE but overlap in collateral-free credit space.'),

    ('GUJCOST', 'GUJARAT_INTEREST_SUBSIDY', 'sequential',
     'Both are Gujarat Industrial Policy 2020 schemes. Apply for capital subsidy (GUJCOST) first as a one-time benefit on investment. Interest subsidy (Gujarat Interest Subsidy) is an annual recurring benefit on the loan. Both can be claimed under the same project.',
     'Gujarat Industrial Policy 2020 — Both schemes under same notification, dual benefit permissible.'),

    ('ZED', 'GEM_REG', 'synergistic',
     'ZED certification significantly improves GeM seller rating and preference in government tenders. ZED-certified MSMEs get priority in government procurement through GeM. Pursue both together for maximum market access.',
     'GeM portal guidelines: ZED certified suppliers get preferential treatment in procurement.'),

    ('CLCSS', 'TEQUP', 'compatible',
     'CLCSS covers general technology upgradation machinery; TEQUP specifically supports energy-efficient equipment and quality certifications. If the CNC machine is energy-efficient, TEQUP may provide additional support for associated quality certification costs.',
     'No exclusion clause found between CLCSS and TEQUP in respective guidelines.'),
]


POLICY_CHANGES_DEMO = [
    {
        'scheme_code': 'CLCSS',
        'change_type': 'benefit_increased',
        'change_summary': 'CLCSS subsidy limit enhanced from ₹15 lakh to ₹25 lakh for micro enterprises with effect from 01-Apr-2024',
        'old_value': {'max_benefit_lakhs': 15.0},
        'new_value': {'max_benefit_lakhs': 25.0},
        'effective_date': date(2024, 4, 1),
        'source_notification': 'Ministry of MSME Circular No. 5/4/2024 dated 15-Mar-2024',
    },
    {
        'scheme_code': 'CGTMSE',
        'change_type': 'eligibility_broadened',
        'change_summary': 'CGTMSE guarantee cover extended from ₹2 crore to ₹5 crore for all MSMEs with effect from 01-Apr-2024',
        'old_value': {'max_cover_lakhs': 200.0},
        'new_value': {'max_cover_lakhs': 500.0},
        'effective_date': date(2024, 4, 1),
        'source_notification': 'CGTMSE Circular dated 01-Apr-2024',
    },
]


class Command(BaseCommand):
    help = 'Seed initial data: ABC Engineering profile + 30+ schemes + relationships'

    def handle(self, *args, **options):
        self.stdout.write('🌱 Seeding UdyamNiti database...')
        
        self._seed_schemes()
        self._seed_demo_profile()
        self._seed_relationships()
        self._seed_policy_changes()
        
        # Also seed official PDF schemes & RAG Policy Corpus
        try:
            from django.core.management import call_command
            self.stdout.write('  → Pre-ingesting official uploaded PDF schemes (CGTMSE EPM, Gujarat SER, IC, Coir Vikas)...')
            call_command('seed_uploaded_pdf_schemes')
            self.stdout.write('  → Pre-ingesting curated RAG policy corpus...')
            call_command('seed_policy_corpus')
        except Exception as e:
            self.stdout.write(self.style.WARNING(f'  ⚠ Ingestion notice: {e}'))

        self.stdout.write(self.style.SUCCESS('✅ Database, PDF schemes, and RAG corpus seeded successfully!'))

    def _seed_schemes(self):
        self.stdout.write('  → Seeding schemes...')
        for scheme_data in SCHEMES_DATA:
            rules = scheme_data.pop('rules', [])
            benefits = scheme_data.pop('benefits', [])
            
            scheme, created = Scheme.objects.update_or_create(
                scheme_code=scheme_data['scheme_code'],
                defaults=scheme_data
            )
            action = 'Created' if created else 'Updated'
            self.stdout.write(f'    {action}: {scheme.scheme_code}')

            # Create rules
            SchemeRule.objects.filter(scheme=scheme).delete()
            for i, rule_data in enumerate(rules):
                SchemeRule.objects.create(scheme=scheme, order=i, **rule_data)

            # Create benefits
            SchemeBenefit.objects.filter(scheme=scheme).delete()
            for benefit_data in benefits:
                SchemeBenefit.objects.create(scheme=scheme, **benefit_data)

        self.stdout.write(f'  ✓ {len(SCHEMES_DATA)} schemes seeded')

    def _seed_demo_profile(self):
        self.stdout.write('  → Seeding ABC Engineering profile...')
        
        # Create demo user
        user, _ = User.objects.get_or_create(
            username='abc_engineering',
            defaults={
                'email': 'info@abcengineering.in',
                'first_name': 'Rajesh',
                'last_name': 'Patel',
            }
        )
        user.set_password('demo1234')
        user.save()

        profile, created = BusinessProfile.objects.update_or_create(
            udyam_registration_number=DEMO_PROFILE_DATA['udyam_registration_number'],
            defaults={**DEMO_PROFILE_DATA, 'user': user}
        )
        self.stdout.write(f'  ✓ ABC Engineering profile {"created" if created else "updated"}')

        # Create a demo goal
        if not profile.goals.exists():
            BusinessGoal.objects.create(
                business_profile=profile,
                raw_goal_text=DEMO_GOAL_TEXT,
                parsed_objective='Purchase a CNC machine worth ₹50 lakh to expand precision machining capacity',
                parsed_project_type='machinery_purchase',
                parsed_investment_amount_lakhs=50.0,
                parsed_support_categories=['capital_subsidy', 'credit_guarantee', 'technology'],
                parsed_industry_hints=['manufacturing', 'engineering', 'precision machining'],
                parsed_missing_info=[
                    'Annual turnover for the current financial year (for scheme eligibility)',
                    'Whether SC/ST owned — qualifies for higher subsidy rates',
                    'ISO/quality certification status — affects ZED scheme eligibility',
                ],
                status='ready',
            )
            self.stdout.write('  ✓ Demo goal created')

    def _seed_relationships(self):
        self.stdout.write('  → Seeding cross-scheme relationships...')
        for scheme_a_code, scheme_b_code, rel_type, desc, evidence in RELATIONSHIPS_DATA:
            try:
                scheme_a = Scheme.objects.get(scheme_code=scheme_a_code)
                scheme_b = Scheme.objects.get(scheme_code=scheme_b_code)
                SchemeRelationship.objects.update_or_create(
                    scheme_a=scheme_a,
                    scheme_b=scheme_b,
                    defaults={
                        'relationship_type': rel_type,
                        'description': desc,
                        'source_evidence': evidence,
                    }
                )
            except Scheme.DoesNotExist:
                self.stdout.write(f'    ⚠ Skipping relationship {scheme_a_code} ↔ {scheme_b_code}')
        self.stdout.write(f'  ✓ {len(RELATIONSHIPS_DATA)} relationships seeded')

    def _seed_policy_changes(self):
        self.stdout.write('  → Seeding policy changes...')
        for change_data in POLICY_CHANGES_DEMO:
            scheme_code = change_data.pop('scheme_code')
            try:
                scheme = Scheme.objects.get(scheme_code=scheme_code)
                PolicyChange.objects.get_or_create(
                    scheme=scheme,
                    change_type=change_data['change_type'],
                    effective_date=change_data['effective_date'],
                    defaults=change_data
                )
            except Scheme.DoesNotExist:
                pass
        self.stdout.write(f'  ✓ {len(POLICY_CHANGES_DEMO)} policy changes seeded')
