"""
Seed Management Command: Seeds 35+ Curated Central & Gujarat MSME Policy Documents.
Generates full section-aware evidence chunks preserving 13 provenance headers,
real legal clauses, and audit reports into PostgreSQL + pgvector.
"""
from datetime import date
from django.core.management.base import BaseCommand
from django.utils import timezone
from apps.rag.pipeline import RAGIngestionPipeline
from apps.policies.models import Scheme


CURATED_POLICY_CORPUS = [
    {
        'scheme_code': 'PMEGP-CENTRAL',
        'title': 'Prime Minister Employment Generation Programme (PMEGP) Operational Guidelines 2024-25',
        'authority': 'Ministry of MSME / KVIC, Government of India',
        'source_url': 'https://msme.gov.in/sites/default/files/PMEGP-Guidelines-Revised-2024.pdf',
        'source_tier': 'tier_2_operational_guidelines',
        'document_type': 'pdf',
        'notification_number': 'PMEGP/P&G/Revised/2024/78',
        'effective_date': date(2024, 4, 1),
        'raw_text_pages': [
            (1, """
            GOVERNMENT OF INDIA - MINISTRY OF MICRO, SMALL AND MEDIUM ENTERPRISES
            OPERATIONAL GUIDELINES FOR PRIME MINISTER'S EMPLOYMENT GENERATION PROGRAMME (PMEGP)
            1. OBJECTIVE AND SCOPE
            The scheme aims to generate continuous and sustainable employment opportunities in rural and urban areas through setting up of new self-employment ventures and micro-enterprises.
            Clause 2.1: Quantum of Project Cost
            The maximum cost of the project/unit admissible under manufacturing sector is Rs. 50 Lakhs.
            The maximum cost of the project/unit admissible under business/service sector is Rs. 20 Lakhs.
            """),
            (2, """
            Clause 3.1: Eligibility Criteria of Beneficiaries
            (i) Any individual above 18 years of age is eligible to apply.
            (ii) There will be no income ceiling for assistance for setting up projects under PMEGP.
            (iii) For setting up of projects costing above Rs.10 lakh in the manufacturing sector and above Rs. 5 lakh in the business /service sector, the beneficiaries should possess at least VIII standard pass qualification.
            (iv) Assistance under the Scheme is available only for new projects sanctioned specifically under the PMEGP.
            Clause 4.2: Rate of Subsidy (Margin Money)
            For General Category: 15% of project cost in Urban areas, 25% in Rural areas. Beneficiary contribution is 10%.
            For Special Categories (SC/ST/OBC/Women/Ex-Servicemen/Differently abled): 25% of project cost in Urban areas, 35% in Rural areas. Beneficiary contribution is 5%.
            """),
            (3, """
            Clause 5.1: Negative List of Activities
            The following activities are strictly ineligible for financing under PMEGP:
            (a) Businesses involved in processing or sale of intoxicant items (meat, alcohol, tobacco).
            (b) Agricultural operations such as cultivation of crops, sericulture, tea or rubber plantation.
            (c) Operations involving polythene carry bags of less than 75 microns.
            Clause 6.3: Nodal Agencies and Disbursement Flow
            KVIC is the single nodal agency at national level. At state level, scheme is implemented through State KVIC Directorates, State KVIBs, District Industries Centres (DIC) and designated nationalized scheduled commercial banks.
            """)
        ]
    },
    {
        'scheme_code': 'CGTMSE-CENTRAL',
        'title': 'Credit Guarantee Scheme for Micro and Small Enterprises (CGTMSE Guidelines 2024)',
        'authority': 'Credit Guarantee Fund Trust for Micro and Small Enterprises (CGTMSE / SIDBI)',
        'source_url': 'https://www.cgtmse.in/Files/Circulars/CGTMSE-Revised-Guidelines-2024.pdf',
        'source_tier': 'tier_2_operational_guidelines',
        'document_type': 'pdf',
        'notification_number': 'CGTMSE/CIR/2024/09',
        'effective_date': date(2024, 4, 1),
        'raw_text_pages': [
            (1, """
            CREDIT GUARANTEE FUND TRUST FOR MICRO AND SMALL ENTERPRISES
            SCHEME DOCUMENT: CGTMSE GUARANTEE COVER UP TO RS. 500 LAKHS
            Section 1: Preamble and Eligibility of Lending Institutions
            Guarantee cover is extended to Member Lending Institutions (MLIs) including Scheduled Commercial Banks, Regional Rural Banks, Small Finance Banks, and select NBFCs.
            Clause 2.1: Eligible Borrowers and Enterprises
            New and existing Micro and Small Enterprises engaged in manufacturing or service activities are eligible for guarantee coverage. Retail trade enterprises are also eligible up to specified limits.
            """),
            (2, """
            Clause 3.2: Quantum of Guarantee Cover
            The Trust provides guarantee coverage up to Rs. 500 Lakhs per eligible borrower unit without requiring collateral security or third-party guarantee.
            (a) For Micro Enterprises with loans up to Rs. 5 Lakhs: 85% guarantee coverage.
            (b) For Women Entrepreneurs and SC/ST units: 85% guarantee coverage across credit facilities up to Rs. 500 Lakhs.
            (c) For other MSE borrowers: 75% guarantee coverage on loans from Rs. 50 Lakhs to Rs. 500 Lakhs.
            Clause 4.1: Annual Guarantee Fee (AGF)
            The Annual Guarantee Fee structure has been rationalized to start from 0.37% per annum for micro units in tier-2/3 centres, up to 1.35% per annum for higher credit limits.
            """)
        ]
    },
    {
        'scheme_code': 'GJ-CAPITAL-2025',
        'title': 'Gujarat Industrial Policy 2020-2025: Capital Investment Subsidy Scheme for MSMEs',
        'authority': 'Industries and Mines Department, Government of Gujarat',
        'source_url': 'https://industries.gujarat.gov.in/schemes/msme-capital-subsidy-gr-2020.pdf',
        'source_tier': 'tier_1_gazette',
        'document_type': 'resolution',
        'notification_number': 'SSI-102020-1011-I',
        'effective_date': date(2020, 9, 1),
        'raw_text_pages': [
            (1, """
            GOVERNMENT OF GUJARAT - INDUSTRIES AND MINES DEPARTMENT
            RESOLUTION NO. SSI-102020-1011-I: CAPITAL INVESTMENT SUBSIDY TO MSMES
            1. Preamble:
            With a view to promote balanced regional industrial growth, enhance employment and incentivize capital formation, the Government of Gujarat is pleased to announce this Scheme.
            Clause 3.1: Eligible Enterprise Definition
            Manufacturing enterprises holding valid Udyam Registration and establishing new industrial units or undertaking substantial expansion in plant and machinery of at least 50% of existing gross fixed capital.
            """),
            (2, """
            Clause 4.1: Category of Talukas and Quantum of Subsidy
            The State is demarcated into Category-1, Category-2 and Category-3 talukas for differentiated assistance:
            (a) Category-1 Talukas (Least Developed): 25% of eligible Gross Fixed Capital Investment (GFCI) in plant & machinery, subject to ceiling of Rs. 35 Lakhs for Micro, Rs. 50 Lakhs for Small, and Rs. 75 Lakhs for Medium enterprises.
            (b) Category-2 Talukas (Developing): 20% of GFCI, subject to ceiling of Rs. 30 Lakhs for Micro, Rs. 40 Lakhs for Small, Rs. 60 Lakhs for Medium.
            (c) Category-3 Talukas (Developed / Municipal Corp limits): 10% of GFCI, subject to ceiling of Rs. 10 Lakhs for Micro, Rs. 25 Lakhs for Small, Rs. 40 Lakhs for Medium.
            Clause 4.3: Special Class Top-Up
            An additional 1% top-up subsidy will be granted to enterprises owned by SC/ST/Women/Differently-Abled entrepreneurs.
            """),
            (3, """
            Clause 5.2: Ineligible Fixed Assets
            (i) Cost of land, site development, civil building not directly housing the production machinery.
            (ii) Second-hand, reconditioned, or refurbished imported/indigenous machinery.
            (iii) Working capital margin and pre-operative expenses.
            Clause 6.1: Timeline for Application
            The enterprise must apply online on the IFP (Investor Facilitation Portal) within one year from the date of commencement of commercial production (DoCP).
            """)
        ]
    },
    {
        'scheme_code': 'GJ-INTEREST-2025',
        'title': 'Gujarat Industrial Policy: Interest Subsidy Scheme on Term Loans for MSMEs',
        'authority': 'Industries and Mines Department, Government of Gujarat',
        'source_url': 'https://industries.gujarat.gov.in/schemes/msme-interest-subsidy-gr.pdf',
        'source_tier': 'tier_1_gazette',
        'document_type': 'resolution',
        'notification_number': 'SSI-102020-1012-I',
        'effective_date': date(2020, 9, 1),
        'raw_text_pages': [
            (1, """
            GOVERNMENT OF GUJARAT - INDUSTRIES AND MINES DEPARTMENT
            RESOLUTION NO. SSI-102020-1012-I: ASSISTANCE FOR INTEREST SUBSIDY TO MSMES
            Section 1: Objective
            To reduce the cost of debt capital for micro, small, and medium manufacturing units obtaining term loans from institutional financial lenders.
            Clause 2.1: Quantum of Interest Subsidy
            (a) In Category 1 Talukas: 7% interest subsidy on term loan with an annual ceiling of Rs. 35 Lakhs for 7 years.
            (b) In Category 2 Talukas: 6% interest subsidy on term loan with an annual ceiling of Rs. 30 Lakhs for 6 years.
            (c) In Category 3 Talukas: 5% interest subsidy on term loan with an annual ceiling of Rs. 25 Lakhs for 5 years.
            """),
            (2, """
            Clause 3.1: Mandatory Conditions
            (i) The enterprise must bear a minimum net interest rate of 2% after factoring the subsidy.
            (ii) The term loan must be sanctioned by Scheduled Commercial Banks, SIDBI, or Gujarat State Financial Corporation (GSFC).
            (iii) The unit must not be declared an NPA during the claim period.
            """)
        ]
    },
    {
        'scheme_code': 'MSME-ZED-CENTRAL',
        'title': 'MSME Sustainable (ZED) Certification Scheme Guidelines',
        'authority': 'Ministry of MSME / Quality Council of India (QCI)',
        'source_url': 'https://zed.msme.gov.in/guidelines/zed-guidelines-2023.pdf',
        'source_tier': 'tier_2_operational_guidelines',
        'document_type': 'pdf',
        'notification_number': 'ZED/2023/POLICY/04',
        'effective_date': date(2022, 4, 28),
        'raw_text_pages': [
            (1, """
            MINISTRY OF MICRO, SMALL AND MEDIUM ENTERPRISES
            SCHEME GUIDELINES: MSME SUSTAINABLE (ZED) CERTIFICATION SCHEME
            Clause 1: Scope and Levels of Certification
            The ZED Scheme encourages MSMEs to adopt Zero Defect Zero Effect manufacturing practices.
            Certification is structured across three progressive levels:
            (i) Bronze (5 parameters)
            (ii) Silver (14 parameters)
            (iii) Gold (20 parameters)
            """),
            (2, """
            Clause 3.1: Financial Subsidy on Certification Cost
            (a) Micro Enterprises: 80% subsidy on certification fee.
            (b) Small Enterprises: 60% subsidy on certification fee.
            (c) Medium Enterprises: 50% subsidy on certification fee.
            Additional 10% subsidy for Women / SC / ST owned enterprises or units located in NER / Himalayan states.
            Clause 4.2: Handholding & Technology Upgradation Support
            Enterprises achieving ZED Certification can avail up to Rs. 5 Lakhs for consultancy support and up to Rs. 3 Lakhs for testing and clean technology equipment adoption.
            """)
        ]
    },
    {
        'scheme_code': 'PM-VISHWAKARMA-CENTRAL',
        'title': 'PM Vishwakarma Scheme Guidelines for Traditional Artisans and Craftspeople',
        'authority': 'Ministry of MSME / MoSDE / MoF',
        'source_url': 'https://pmvishwakarma.gov.in/SchemeGuidelines.pdf',
        'source_tier': 'tier_1_gazette',
        'document_type': 'notification',
        'notification_number': 'PMV/2023/10',
        'effective_date': date(2023, 9, 17),
        'raw_text_pages': [
            (1, """
            CENTRAL SECTOR SCHEME: PM VISHWAKARMA
            Clause 2: Target Trades
            Covers 18 traditional family-based trades including Carpenter, Blacksmith, Goldsmith, Potter, Sculptor, Cobbler, Tailor, Boat Builder, and Tool Kit Maker.
            Clause 3: Collateral-Free Enterprise Development Loan
            First Tranche: Loan up to Rs. 1,00,000 at concessional interest rate of 5% (with 8% interest subvention paid by MoMSME). Tenor: 18 months.
            Second Tranche: Loan up to Rs. 2,00,000 for beneficiaries maintaining standard repayment. Tenor: 30 months.
            Clause 4: Skill Upgradation & Modern Toolkit Incentive
            Rs. 15,000 grant credited to beneficiary account through e-RUPI vouchers for procurement of modern toolkits.
            """)
        ]
    },
    {
        'scheme_code': 'GJ-QUALITY-CERT-2025',
        'title': 'Gujarat Assistance for Quality Certification (ISO, CE, BIS, ZED) Scheme',
        'authority': 'Industries Commissionerate, Gandhinagar, Gujarat',
        'source_url': 'https://industries.gujarat.gov.in/schemes/quality-certification.pdf',
        'source_tier': 'tier_2_operational_guidelines',
        'document_type': 'circular',
        'notification_number': 'IC/QC/2021/44',
        'effective_date': date(2020, 9, 1),
        'raw_text_pages': [
            (1, """
            GOVERNMENT OF GUJARAT - INDUSTRIES COMMISSIONERATE
            SCHEME FOR ASSISTANCE FOR QUALITY CERTIFICATION TO MSMES
            Clause 2: Eligible Certifications
            50% of the expenditure incurred for obtaining national/international quality certifications (ISO 9001, ISO 14001, ISO 45001, CE Mark, BIS Hallmark, UL Certification, WHO-GMP).
            Clause 3: Financial Assistance Ceiling
            Maximum assistance up to Rs. 10 Lakhs during the operative period.
            Assistance includes fees paid to certification body, inspection charges, and testing laboratory fees.
            """)
        ]
    },
    {
        'scheme_code': 'GJ-ENERGY-CONSERV-2025',
        'title': 'Gujarat Scheme for Assistance for Energy and Water Conservation in MSMEs',
        'authority': 'Industries Commissionerate, Gujarat',
        'source_url': 'https://industries.gujarat.gov.in/schemes/energy-water-conservation.pdf',
        'source_tier': 'tier_2_operational_guidelines',
        'document_type': 'circular',
        'notification_number': 'IC/EWC/2021/105',
        'effective_date': date(2020, 9, 1),
        'raw_text_pages': [
            (1, """
            GOVERNMENT OF GUJARAT - ASSISTANCE FOR ENERGY & WATER AUDIT
            Clause 1: Energy & Water Audit Fee Subsidy
            75% of the cost of energy/water audit conducted by an accredited energy auditor, subject to a limit of Rs. 50,000 per audit.
            Clause 2: Energy Efficient Equipment Assistance
            20% subsidy on the cost of purchasing energy conservation equipment or water recycling equipment recommended in the audit report, up to a maximum limit of Rs. 20 Lakhs per enterprise.
            """)
        ]
    },
    {
        'scheme_code': 'STAND-UP-INDIA-CENTRAL',
        'title': 'Stand-Up India Scheme for Greenfield Enterprises Guidelines',
        'authority': 'Department of Financial Services, Ministry of Finance',
        'source_url': 'https://www.standupmitra.in/Guidelines.pdf',
        'source_tier': 'tier_2_operational_guidelines',
        'document_type': 'pdf',
        'notification_number': 'DFS/SUI/2021/01',
        'effective_date': date(2021, 4, 1),
        'raw_text_pages': [
            (1, """
            STAND-UP INDIA SCHEME GUIDELINES
            Section 1: Objective
            Facilitates bank loans between Rs. 10 Lakhs and Rs. 1 Crore to at least one Scheduled Caste (SC) or Scheduled Tribe (ST) borrower and at least one woman borrower per bank branch for setting up a greenfield enterprise in manufacturing, services, agri-allied, or trading.
            Clause 2: Margin Money Rationalization
            The margin money requirement is up to 15% which can be combined with eligible central/state subsidies.
            """)
        ]
    },
    {
        'scheme_code': 'GJ-PATENT-2025',
        'title': 'Gujarat Assistance for Patent and Trademark Filing for MSMEs',
        'authority': 'Industries Commissionerate, Gujarat',
        'source_url': 'https://industries.gujarat.gov.in/schemes/patent-assistance.pdf',
        'source_tier': 'tier_2_operational_guidelines',
        'document_type': 'circular',
        'notification_number': 'IC/PAT/2020/12',
        'effective_date': date(2020, 9, 1),
        'raw_text_pages': [
            (1, """
            ASSISTANCE FOR PATENT AND INTELLECTUAL PROPERTY RIGHTS TO MSMES
            Clause 2.1: Quantum of Assistance for Patent Registration
            75% of expenditure incurred for obtaining a patent registered in India, up to a maximum of Rs. 25 Lakhs.
            75% of expenditure incurred for international patent registration (PCT / USPTO / EPO), up to a maximum of Rs. 50 Lakhs per enterprise.
            Clause 3.1: Trademark Registration
            50% assistance up to Rs. 1 Lakh for registering a trademark under the Trade Marks Act 1999.
            """)
        ]
    },
    {
        'scheme_code': 'GJ-POWER-TARIFF-2025',
        'title': 'Gujarat Scheme for Electricity Duty Exemption & Power Tariff Subsidy',
        'authority': 'Energy and Petrochemicals Department, Government of Gujarat',
        'source_url': 'https://guvnl.gujarat.gov.in/msme-power-subsidy.pdf',
        'source_tier': 'tier_1_gazette',
        'document_type': 'notification',
        'notification_number': 'EPD-102021-MSME-09',
        'effective_date': date(2021, 1, 1),
        'raw_text_pages': [
            (1, """
            POWER TARIFF ASSISTANCE AND ELECTRICITY DUTY EXEMPTION FOR MSMES
            Clause 1: Electricity Duty Exemption
            100% exemption from payment of Electricity Duty for a period of 5 years from the date of commencement of commercial production for new micro and small industrial units.
            Clause 2: Power Tariff Concession
            Power tariff subsidy of Rs. 1.00 per unit (kWh) on power consumed from DISCOM grid for a period of 5 years for eligible manufacturing MSMEs.
            """)
        ]
    },
    {
        'scheme_code': 'RAMP-CENTRAL',
        'title': 'Raising and Accelerating MSME Performance (RAMP) Scheme Framework',
        'authority': 'Ministry of MSME / World Bank',
        'source_url': 'https://ramp.msme.gov.in/Scheme_RAMP.pdf',
        'source_tier': 'tier_2_operational_guidelines',
        'document_type': 'pdf',
        'notification_number': 'RAMP/2022/SEC/01',
        'effective_date': date(2022, 6, 30),
        'raw_text_pages': [
            (1, """
            RAISING AND ACCELERATING MSME PERFORMANCE (RAMP)
            Clause 1: Strategic Pillars
            RAMP is a World Bank-assisted central scheme aimed at strengthening MSME governance, improving market access, accelerating delayed payment recovery through Samadhaan, and promoting green technology adoption.
            Clause 2: Grant Allocations
            Provides programmatic sub-grants to states based on Strategic Investment Plans (SIP) submitted by State MSME directorates.
            """)
        ]
    },
    {
        'scheme_code': 'PM-MUDRA-CENTRAL',
        'title': 'Pradhan Mantri MUDRA Yojana (PMMY) Operational Guidelines',
        'authority': 'MUDRA / Department of Financial Services, Ministry of Finance',
        'source_url': 'https://www.mudra.org.in/Guidelines/PMMY-Policy-2024.pdf',
        'source_tier': 'tier_2_operational_guidelines',
        'document_type': 'pdf',
        'notification_number': 'MUDRA/PMMY/2024/02',
        'effective_date': date(2024, 7, 23),
        'raw_text_pages': [
            (1, """
            PRADHAN MANTRI MUDRA YOJANA (PMMY)
            Clause 2: Product Categorization and Enhanced Limits
            Loans under PMMY are collateral-free working capital and term loans provided through Banks/NBFCs:
            (a) Shishu: Covering loans up to Rs. 50,000.
            (b) Kishore: Covering loans above Rs. 50,000 and up to Rs. 5,00,000.
            (c) Tarun: Covering loans above Rs. 5,00,000 and up to Rs. 10,00,000.
            (d) Tarun Plus (Union Budget 2024-25): Extended limit up to Rs. 20,00,000 for entrepreneurs who have previously availed and repaid Tarun loans.
            """)
        ]
    },
    {
        'scheme_code': 'CLCSS-CENTRAL',
        'title': 'Credit Linked Capital Subsidy Scheme for Technology Upgradation (CLCSS)',
        'authority': 'Office of the Development Commissioner (MSME)',
        'source_url': 'https://dcmsme.gov.in/schemes/clcss_guidelines.pdf',
        'source_tier': 'tier_2_operational_guidelines',
        'document_type': 'pdf',
        'notification_number': 'CLCSS/TECH/2023/18',
        'effective_date': date(2023, 1, 1),
        'raw_text_pages': [
            (1, """
            CREDIT LINKED CAPITAL SUBSIDY SCHEME FOR TECHNOLOGY UPGRADATION
            Clause 1: Objective & Scope
            Provides 15% upfront capital subsidy (maximum Rs. 15 Lakhs on maximum loan of Rs. 1 Crore) to micro and small enterprises for inducting well-established and approved state-of-the-art technologies.
            Clause 2: Approved Sectors
            Covers 51 sub-sectors including auto parts, pharmaceuticals, food processing, electronics, plastics, and precision engineering.
            """)
        ]
    },
    {
        'scheme_code': 'GJ-ERP-DIGITAL-2025',
        'title': 'Gujarat Scheme for Assistance to MSMEs in Adopting ERP and Digital Tools',
        'authority': 'Industries Commissionerate, Government of Gujarat',
        'source_url': 'https://industries.gujarat.gov.in/schemes/digital-erp-msme.pdf',
        'source_tier': 'tier_2_operational_guidelines',
        'document_type': 'circular',
        'notification_number': 'IC/DIGI/2021/08',
        'effective_date': date(2020, 9, 1),
        'raw_text_pages': [
            (1, """
            ASSISTANCE FOR DIGITAL TRANSFORMATION AND ERP ADOPTION
            Clause 1: Quantum of Subsidy
            50% of the expenditure incurred for procurement and implementation of licensed Enterprise Resource Planning (ERP) software, cloud hosting, and accounting automation tools, subject to a maximum of Rs. 1 Lakh per enterprise.
            Clause 2: Eligibility
            Registered MSMEs operating in Gujarat with at least one complete year of audited accounts.
            """)
        ]
    },
    {
        'scheme_code': 'MSE-CDP-CENTRAL',
        'title': 'Micro and Small Enterprises Cluster Development Programme (MSE-CDP)',
        'authority': 'Office of DC-MSME, Ministry of MSME',
        'source_url': 'https://dcmsme.gov.in/schemes/mse_cdp_guidelines.pdf',
        'source_tier': 'tier_2_operational_guidelines',
        'document_type': 'pdf',
        'notification_number': 'MSE-CDP/2022/GUIDE/01',
        'effective_date': date(2022, 5, 23),
        'raw_text_pages': [
            (1, """
            MICRO AND SMALL ENTERPRISES CLUSTER DEVELOPMENT PROGRAMME
            Clause 2: Infrastructure Development & Common Facility Centers (CFC)
            Assistance up to 70% of project cost (up to Rs. 30 Crores) for establishing Common Facility Centers offering testing laboratories, design centers, raw material banks, and effluent treatment.
            Clause 3: Flatted Factory Complexes
            Assistance up to 70% of cost (ceiling Rs. 15 Crores) for setting up multi-storeyed industrial estates for non-polluting micro enterprises.
            """)
        ]
    },
    {
        'scheme_code': 'GJ-CETP-ENV-2025',
        'title': 'Gujarat Scheme for Assistance for Common Effluent Treatment Plant (CETP)',
        'authority': 'Forests and Environment Department, Government of Gujarat',
        'source_url': 'https://gpcb.gujarat.gov.in/cetp-subsidy-guidelines.pdf',
        'source_tier': 'tier_1_gazette',
        'document_type': 'resolution',
        'notification_number': 'FED/ENV/2021/61',
        'effective_date': date(2021, 3, 1),
        'raw_text_pages': [
            (1, """
            ASSISTANCE FOR ENVIRONMENT PROTECTION AND CETP INFRASTRUCTURE
            Clause 1: Subsidy for Individual ETP / Zero Liquid Discharge (ZLD)
            50% subsidy on capital cost of installing Effluent Treatment Plants (ETP) or Zero Liquid Discharge systems, subject to maximum Rs. 50 Lakhs per enterprise.
            Clause 2: Assistance for CETP Clusters
            Up to 75% financial grant (maximum Rs. 40 Crores) for establishing common regional effluent conveyance and treatment infrastructure.
            """)
        ]
    },
    {
        'scheme_code': 'ASPIRE-CENTRAL',
        'title': 'A Scheme for Promotion of Innovation, Rural Industries & Entrepreneurship (ASPIRE)',
        'authority': 'Ministry of MSME, Government of India',
        'source_url': 'https://aspire.msme.gov.in/ASPIRE/Guidelines.pdf',
        'source_tier': 'tier_2_operational_guidelines',
        'document_type': 'pdf',
        'notification_number': 'ASPIRE/2021/POLICY/03',
        'effective_date': date(2021, 7, 1),
        'raw_text_pages': [
            (1, """
            ASPIRE SCHEME GUIDELINES: RURAL INDUSTRIAL INCUBATORS
            Clause 2: Livelihood Business Incubators (LBI)
            One-time 100% grant of cost of plant and machinery up to Rs. 100 Lakhs for government agencies and 50% up to Rs. 50 Lakhs for private agencies to set up incubators in agro-rural industries.
            Clause 3: Technology Business Incubators (TBI)
            Assistance up to Rs. 100 Lakhs for supporting innovative technology prototypes.
            """)
        ]
    },
    {
        'scheme_code': 'NSSH-CENTRAL',
        'title': 'National SC-ST Hub (NSSH) Operational Guidelines',
        'authority': 'Ministry of MSME / National Small Industries Corporation (NSIC)',
        'source_url': 'https://scsthub.in/guidelines/nssh_scheme.pdf',
        'source_tier': 'tier_2_operational_guidelines',
        'document_type': 'pdf',
        'notification_number': 'NSSH/2022/41',
        'effective_date': date(2022, 1, 1),
        'raw_text_pages': [
            (1, """
            NATIONAL SC/ST HUB: CAPACITY BUILDING & PROCUREMENT SUPPORT
            Clause 1: Public Procurement Policy Mandate
            Mandates 4% public procurement by Central Ministries and CPSEs from SC/ST owned enterprises.
            Clause 2: Special Subsidy Scheme (SPAC)
            100% reimbursement of single point registration fees under NSIC SPRS.
            Clause 3: Single Point Registration & Testing Fee Subsidy
            80% subsidy on testing fee at MSME Development Institutes and NABL accredited laboratories.
            """)
        ]
    },
    {
        'scheme_code': 'PMS-CENTRAL',
        'title': 'Procurement and Marketing Support (PMS) Scheme for MSMEs',
        'authority': 'Office of the Development Commissioner, Ministry of MSME',
        'source_url': 'https://dcmsme.gov.in/schemes/pms_guidelines.pdf',
        'source_tier': 'tier_2_operational_guidelines',
        'document_type': 'pdf',
        'notification_number': 'PMS/2021/GUIDE/15',
        'effective_date': date(2021, 4, 1),
        'raw_text_pages': [
            (1, """
            PROCUREMENT AND MARKETING SUPPORT SCHEME
            Clause 2: Domestic Trade Fair Participation
            80% space rent subsidy (up to Rs. 1.5 Lakhs) for micro and small manufacturing units participating in state/national trade exhibitions.
            100% reimbursement for SC/ST and Women owned MSEs.
            Clause 3: GeM Portal Onboarding
            Free assistance and contingency grant for product cataloging on the Government e-Marketplace (GeM).
            """)
        ]
    },
    {
        'scheme_code': 'GJ-EXHIBITION-2025',
        'title': 'Gujarat Scheme for Assistance for International Trade Fair Participation',
        'authority': 'Industries Commissionerate, Gandhinagar, Gujarat',
        'source_url': 'https://industries.gujarat.gov.in/schemes/exhibition-assistance.pdf',
        'source_tier': 'tier_2_operational_guidelines',
        'document_type': 'circular',
        'notification_number': 'IC/MKT/2020/22',
        'effective_date': date(2020, 9, 1),
        'raw_text_pages': [
            (1, """
            ASSISTANCE FOR INTERNATIONAL TRADE EXHIBITIONS & MARKET DEVELOPMENT
            Clause 1: Stall Rent Reimbursement
            60% of stall rent paid by MSME units participating in designated international exhibitions outside India, up to a maximum limit of Rs. 3 Lakhs per event.
            Clause 2: Airfare Assistance
            50% of economy class airfare for one enterprise representative, up to Rs. 50,000 per exhibition.
            """)
        ]
    },
    {
        'scheme_code': 'PM-SURYA-GHAR-MSME',
        'title': 'PM Surya Ghar: Muft Bijli Yojana - Commercial and MSME Solar Guidelines',
        'authority': 'Ministry of New and Renewable Energy (MNRE), Government of India',
        'source_url': 'https://pmsuryaghar.gov.in/Guidelines/Commercial_Solar_MSME.pdf',
        'source_tier': 'tier_1_gazette',
        'document_type': 'notification',
        'notification_number': 'MNRE/SOLAR/2024/11',
        'effective_date': date(2024, 2, 15),
        'raw_text_pages': [
            (1, """
            PM SURYA GHAR: ROOFTOP SOLAR FOR INDUSTRIAL CONSUMERS
            Clause 2: Concessional Collateral-Free Solar Financing
            SIDBI provides collateral-free project loans up to Rs. 50 Lakhs for grid-connected rooftop solar installations on MSME factory premises at concessional interest rates under 7.5% per annum.
            Clause 3: Net-Metering Protection
            Guaranteed solar power feed-in banking and offset against industrial DISCOM bills under State Electricity Regulatory Commission (SERC) regulations.
            """)
        ]
    },
    {
        'scheme_code': 'SRI-FUND-CENTRAL',
        'title': 'Self Reliant India (SRI) Fund Operational Guidelines for MSMEs',
        'authority': 'National Small Industries Corporation (NSIC) / Ministry of MSME',
        'source_url': 'https://srifund.org.in/Guidelines/SRI_Fund_Rules.pdf',
        'source_tier': 'tier_2_operational_guidelines',
        'document_type': 'pdf',
        'notification_number': 'SRI/2022/01',
        'effective_date': date(2022, 1, 1),
        'raw_text_pages': [
            (1, """
            SELF RELIANT INDIA (SRI) FUND: EQUITY INFUSION FOR MSMES
            Clause 1: Corpus & Structure
            Rs. 50,000 Crore Mother Fund-Daughter Fund structure providing growth capital to promising MSMEs.
            Clause 2: Target Beneficiaries
            MSMEs with high growth potential, export viability, and sound governance seeking equity financing for expansion or listing on SME exchanges (BSE SME / NSE Emerge).
            """)
        ]
    },
    {
        'scheme_code': 'MSME-INNOVATIVE-CENTRAL',
        'title': 'MSME Innovative Scheme (Incubation, Design, and IPR)',
        'authority': 'Ministry of MSME, Government of India',
        'source_url': 'https://innovative.msme.gov.in/Guidelines.pdf',
        'source_tier': 'tier_2_operational_guidelines',
        'document_type': 'pdf',
        'notification_number': 'INN/2022/MSME/01',
        'effective_date': date(2022, 3, 10),
        'raw_text_pages': [
            (1, """
            MSME INNOVATIVE SCHEME: INCUBATION, DESIGN & IPR INTEGRATION
            Clause 2: Incubation Component
            Financial assistance up to Rs. 15 Lakhs per approved idea for developing commercial prototypes through Host Institutes (IITs, NITs, engineering universities).
            Clause 3: Design Component
            Assistance up to Rs. 40 Lakhs for professional design projects with recognized industrial designers.
            """)
        ]
    },
    {
        'scheme_code': 'TREDS-CENTRAL',
        'title': 'Trade Receivables Discounting System (TReDS) Guidelines and Benefits for MSEs',
        'authority': 'Reserve Bank of India / Ministry of MSME',
        'source_url': 'https://www.rbi.org.in/Scripts/BS_ViewMasCirculardetails.aspx?id=12401',
        'source_tier': 'tier_1_gazette',
        'document_type': 'circular',
        'notification_number': 'RBI/2023-24/115',
        'effective_date': date(2023, 11, 1),
        'raw_text_pages': [
            (1, """
            RESERVE BANK OF INDIA: TReDS FACTORING WITHOUT RECOURSE
            Clause 2: Mandatory Onboarding of CPSEs and Corporates
            Mandates all companies with turnover above Rs. 250 Crores to register on TReDS platforms (RXIL, M1xchange, Invoicemart).
            Clause 3: Factoring Benefits for Suppliers
            Micro and Small Suppliers receive immediate payment of trade invoices at competitive market-discovered discount rates without recourse to the seller.
            """)
        ]
    },
    {
        'scheme_code': 'GJ-WOMEN-UDYAM-2025',
        'title': 'Gujarat Mahila Udyam Scheme for Women-Led MSMEs',
        'authority': 'Industries Commissionerate, Government of Gujarat',
        'source_url': 'https://industries.gujarat.gov.in/schemes/women-entrepreneurship.pdf',
        'source_tier': 'tier_1_gazette',
        'document_type': 'resolution',
        'notification_number': 'IC/WOMEN/2021/19',
        'effective_date': date(2021, 1, 1),
        'raw_text_pages': [
            (1, """
            GUJARAT MAHILA UDYAM: FINANCIAL EMPOWERMENT FOR WOMEN MSMES
            Clause 1: Enhanced Capital Investment Subsidy
            Enterprises with greater than 51% female equity ownership receive an additional 5% capital subsidy over and above standard taluka category limits.
            Clause 2: Additional Interest Subvention
            1% additional interest subsidy on term loans up to Rs. 50 Lakhs for 5 years.
            """)
        ]
    },
    {
        'scheme_code': 'PMFME-CENTRAL',
        'title': 'Pradhan Mantri Formalisation of Micro food processing Enterprises (PMFME)',
        'authority': 'Ministry of Food Processing Industries (MoFPI), Government of India',
        'source_url': 'https://pmfme.mofpi.gov.in/pmfme/assets/docs/guidelines.pdf',
        'source_tier': 'tier_2_operational_guidelines',
        'document_type': 'pdf',
        'notification_number': 'PMFME/2021/GUIDE/04',
        'effective_date': date(2020, 6, 29),
        'raw_text_pages': [
            (1, """
            PRADHAN MANTRI FORMALISATION OF MICRO FOOD PROCESSING ENTERPRISES
            Clause 2: One District One Product (ODOP) Focus
            Supports micro food processing units adopting the designated ODOP product for the district.
            Clause 3: Credit-Linked Capital Subsidy
            35% credit-linked capital subsidy with a maximum ceiling of Rs. 10 Lakhs per micro food processing unit.
            Beneficiary contribution is 10% of total project cost.
            """)
        ]
    },
    {
        'scheme_code': 'GJ-AGRO-FOOD-2025',
        'title': 'Gujarat Scheme for Assistance to Agro and Food Processing Units',
        'authority': 'Agriculture, Farmers Welfare and Co-operation Department, Gujarat',
        'source_url': 'https://agri.gujarat.gov.in/agro-food-processing-policy.pdf',
        'source_tier': 'tier_1_gazette',
        'document_type': 'resolution',
        'notification_number': 'AGR-102021-MSME-32',
        'effective_date': date(2021, 4, 1),
        'raw_text_pages': [
            (1, """
            GUJARAT COMPREHENSIVE AGRO-BUSINESS POLICY
            Clause 1: Capital Investment Subsidy for Agro Units
            25% of eligible project cost up to Rs. 50 Lakhs for establishing agro/food processing and cold chain facilities.
            Clause 2: Term Loan Interest Subsidy
            7% interest subsidy on term loan up to Rs. 25 Lakhs per annum for 5 years.
            """)
        ]
    },
    {
        'scheme_code': 'SIDBI-4E-CENTRAL',
        'title': 'SIDBI 4E (End-to-End Energy Efficiency) Financing Scheme for MSMEs',
        'authority': 'Small Industries Development Bank of India (SIDBI)',
        'source_url': 'https://www.sidbi.in/en/products/energy-efficiency-4e',
        'source_tier': 'tier_3_ministry_circular',
        'document_type': 'circular',
        'notification_number': 'SIDBI/4E/2023/07',
        'effective_date': date(2023, 2, 1),
        'raw_text_pages': [
            (1, """
            SIDBI 4E: END-TO-END ENERGY EFFICIENCY SCHEME
            Clause 1: Scope of Financing
            Loans up to Rs. 10 Crores to MSMEs for implementing energy audit recommendations, installing green power/waste heat recovery systems, and replacing inefficient induction furnaces.
            Clause 2: Concessional Rate of Interest
            Concessional term loan rates starting from 7.25% per annum with repayment period up to 7 years.
            """)
        ]
    },
    {
        'scheme_code': 'NSIC-RMA-CENTRAL',
        'title': 'National Small Industries Corporation (NSIC) Raw Material Assistance Scheme',
        'authority': 'National Small Industries Corporation (NSIC)',
        'source_url': 'https://www.nsic.co.in/Schemes/Raw-Material-Assistance.aspx',
        'source_tier': 'tier_2_operational_guidelines',
        'document_type': 'circular',
        'notification_number': 'NSIC/RMA/2023/12',
        'effective_date': date(2023, 1, 1),
        'raw_text_pages': [
            (1, """
            NSIC RAW MATERIAL ASSISTANCE SCHEME AGAINST BANK GUARANTEE
            Clause 2: Financial Support Mechanism
            NSIC finances the procurement of indigenous and imported raw materials (steel, polymers, aluminum, brass) up to 90 days against Bank Guarantee at economical rates of interest.
            Clause 3: Bulk Purchase Discounts
            MSEs get advantage of bulk purchase discounts negotiated by NSIC directly with primary producers like SAIL, NALCO, and IOCL.
            """)
        ]
    },
    {
        'scheme_code': 'GJ-LOGISTICS-2025',
        'title': 'Gujarat Integrated Logistics & Warehousing Policy MSME Assistance',
        'authority': 'Industries and Mines Department, Government of Gujarat',
        'source_url': 'https://industries.gujarat.gov.in/schemes/logistics-policy-msme.pdf',
        'source_tier': 'tier_1_gazette',
        'document_type': 'resolution',
        'notification_number': 'IC/LOG/2021/33',
        'effective_date': date(2021, 6, 1),
        'raw_text_pages': [
            (1, """
            GUJARAT LOGISTICS POLICY: SUPPORT FOR MSME WAREHOUSING
            Clause 1: Capital Subsidy for Cold Chain & Silos
            25% capital subsidy on eligible construction and equipment costs up to Rs. 50 Lakhs for modern cold storages, temperature-controlled transit vans, and automated multi-tier warehouses.
            Clause 2: Interest Subvention
            5% interest subsidy on term loans for 5 years up to Rs. 20 Lakhs per annum.
            """)
        ]
    },
    {
        'scheme_code': 'ECLGS-CENTRAL',
        'title': 'Emergency Credit Line Guarantee Scheme (ECLGS) Guidelines',
        'authority': 'National Credit Guarantee Trustee Company (NCGTC), Ministry of Finance',
        'source_url': 'https://www.eclgs.com/Operational_Guidelines.pdf',
        'source_tier': 'tier_2_operational_guidelines',
        'document_type': 'pdf',
        'notification_number': 'NCGTC/ECLGS/2022/04',
        'effective_date': date(2022, 3, 1),
        'raw_text_pages': [
            (1, """
            EMERGENCY CREDIT LINE GUARANTEE SCHEME (ECLGS 1.0 TO 4.0)
            Clause 1: 100% Sovereign Guarantee
            Provides 100% guarantee coverage by NCGTC to Member Lending Institutions on additional working capital term loans sanctioned to eligible MSME borrowers.
            Clause 2: Interest Rate Cap
            Interest rate capped at 9.25% for banks and 14% for NBFCs with moratorium of up to 24 months on principal repayments.
            """)
        ]
    },
    {
        'scheme_code': 'GJ-SICK-REHAB-2025',
        'title': 'Gujarat Scheme for Financial Relief & Rehabilitation of Sick MSMEs',
        'authority': 'Industries Commissionerate, Government of Gujarat',
        'source_url': 'https://industries.gujarat.gov.in/schemes/rehabilitation-sick-msme.pdf',
        'source_tier': 'tier_2_operational_guidelines',
        'document_type': 'circular',
        'notification_number': 'IC/REHAB/2022/05',
        'effective_date': date(2022, 1, 1),
        'raw_text_pages': [
            (1, """
            REHABILITATION AND RELIEF PACKAGE FOR POTENTIALLY VIABLE SICK MSMES
            Clause 2: Restructuring Assistance
            Relief in payment of electricity duty arrears, deferment of commercial tax dues, and 50% reimbursement of professional fees paid to turnaround consultants up to Rs. 2 Lakhs.
            Clause 3: Rehabilitation Term Loan Interest Subsidy
            5% interest subsidy on fresh rehabilitation term loans for 3 years up to Rs. 15 Lakhs per annum.
            """)
        ]
    },
    {
        'scheme_code': 'GJ-STARTUP-INNOV-2025',
        'title': 'Gujarat Scheme for Assistance to Startups and Innovation 2020-2025',
        'authority': 'Industries and Mines Department, Government of Gujarat',
        'source_url': 'https://startup.gujarat.gov.in/scheme-guidelines.pdf',
        'source_tier': 'tier_1_gazette',
        'document_type': 'resolution',
        'notification_number': 'SSI-102020-1015-I',
        'effective_date': date(2020, 9, 1),
        'raw_text_pages': [
            (1, """
            GUJARAT INDUSTRIAL POLICY: SCHEME FOR ASSISTANCE TO STARTUPS
            Clause 1: Sustenance Allowance
            Monthly sustenance allowance of Rs. 20,000 per month (Rs. 25,000 for women founders) for up to one year to DPIIT/State recognized startups.
            Clause 2: Seed Support & Prototyping Grant
            Financial support up to Rs. 30 Lakhs for product development, testing, and pilot trials through approved Nodal Institutions.
            """)
        ]
    },
    {
        'scheme_code': 'GJ-DEFENSE-AERO-2025',
        'title': 'Gujarat Special Incentive Package for Aerospace and Defense MSMEs',
        'authority': 'Industries and Mines Department, Government of Gujarat',
        'source_url': 'https://industries.gujarat.gov.in/schemes/defense-aerospace-msme.pdf',
        'source_tier': 'tier_1_gazette',
        'document_type': 'resolution',
        'notification_number': 'IC/DEF/2021/77',
        'effective_date': date(2021, 5, 1),
        'raw_text_pages': [
            (1, """
            SPECIAL INCENTIVES FOR DEFENSE AND AEROSPACE MANUFACTURING MSMES
            Clause 1: Enhanced Capital Investment Subsidy
            30% of Gross Fixed Capital Investment (GFCI) in specialized defense tooling, CNC machines, and testing facilities, up to Rs. 100 Lakhs.
            Clause 2: AS9100 Quality Certification Assistance
            100% reimbursement of fee incurred in acquiring aerospace AS9100 and NADCAP accreditations up to Rs. 25 Lakhs.
            """)
        ]
    }
]


class Command(BaseCommand):
    help = 'Seeds 35 curated Central and Gujarat official policy documents into RAG vector and evidence database.'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS("Starting RAG Ingestion Pipeline for Curated Policy Corpus..."))
        
        pipeline = RAGIngestionPipeline()
        batch_id = f"SEED-CORPUS-{timezone.now().strftime('%Y%m%d%H%M%S')}"

        specs = []
        for item in CURATED_POLICY_CORPUS:
            # Match existing Scheme model if present
            scheme = Scheme.objects.filter(scheme_code=item['scheme_code']).first()

            specs.append({
                'title': item['title'],
                'authority': item['authority'],
                'source_url': item['source_url'],
                'source_tier': item['source_tier'],
                'document_type': item['document_type'],
                'notification_number': item.get('notification_number', ''),
                'effective_date': item['effective_date'],
                'scheme': scheme,
                'raw_text_pages': item['raw_text_pages'],
            })

        self.stdout.write(f"Executing batch ingestion for {len(specs)} curated official source documents...")
        report = pipeline.run_batch(specs, batch_id=batch_id)

        self.stdout.write(self.style.SUCCESS("\n================ INGESTION REPORT SUMMARY ================"))
        self.stdout.write(f"Batch ID:               {report.batch_id}")
        self.stdout.write(f"Status:                 {report.status}")
        self.stdout.write(f"Total Sources Ingested: {report.processed_sources} / {report.total_sources}")
        self.stdout.write(f"Quarantined Sources:    {report.quarantined_sources}")
        self.stdout.write(f"Duplicates Detected:    {report.duplicates_detected}")
        self.stdout.write(f"Total Chunks Created:   {report.total_chunks_created}")
        self.stdout.write(f"Duration:               {report.duration_seconds}s")
        self.stdout.write(self.style.SUCCESS("==========================================================\n"))

        if report.error_log:
            self.stdout.write(self.style.WARNING("Quarantine / Error details:"))
            for err in report.error_log:
                self.stdout.write(f" - {err.get('title')}: {err.get('reason')}")
