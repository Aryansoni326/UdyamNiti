/**
 * Statutory Business Document Taxonomy & Scheme Gap Analyzer
 * Handles enterprise document inventory, cross-scheme statutory matching,
 * and automated AI readiness & gap synthesis based directly on the 33 Scheme PDFs in the data folder.
 */

export interface StatutoryDocument {
  id: string
  name: string
  shortDesc: string
  category: 'Statutory' | 'Taxation' | 'Financial' | 'Technical' | 'Regulatory' | 'Infrastructure' | 'Commercial' | 'Special Category'
  issuingAuthority: string
  guidance: string
  schemePdfSources: string[]
  commonAliases: string[]
}

export const STATUTORY_BUSINESS_DOCUMENTS: StatutoryDocument[] = [
  {
    id: 'udyam',
    name: 'MSME Udyam Registration Certificate',
    shortDesc: 'Permanent 19-digit statutory MSME registration certificate issued with active NIC activity codes.',
    category: 'Statutory',
    issuingAuthority: 'Ministry of MSME / udyamregistration.gov.in',
    guidance: 'Instant digital registration using Aadhaar and GSTIN on the national Udyam portal.',
    schemePdfSources: ['pmegp scheme.pdf', 'Circular 257 - CGS for Export credit merged.pdf', 'msme-cdp.pdf', 'ZED_Guidance_Document_NIC_Division_24.pdf', 'SFURTI_NEW_GUIDELINES.pdf', 'TReDS Cicular 262.pdf'],
    commonAliases: ['udyam', 'udyam_cert', 'udyam_list', 'udyam_gj', 'udyam_fme', 'udyam_scst', 'coir_reg', 'urn'],
  },
  {
    id: 'pan_gst',
    name: 'Entity PAN & Active GSTIN Registration Certificate',
    shortDesc: 'Permanent Account Number & Active GST Registration Certificate with monthly filing records.',
    category: 'Taxation',
    issuingAuthority: 'Income Tax Dept & Goods and Services Tax Network (GSTN)',
    guidance: 'Verify active filing status on gst.gov.in. Required for all financial subsidies and tax credit verification.',
    schemePdfSources: ['1.msme.pdf', 'pmegp scheme.pdf', 'Circular 257 - CGS for Export credit merged.pdf', 'TReDS Cicular 262.pdf'],
    commonAliases: ['pan_gst', 'gst_reg', 'aadhaar_pan', 'declaration', 'gst_invoices', 'pan', 'gst'],
  },
  {
    id: 'bank_statements',
    name: '12-Month Audited Bank Account Statements',
    shortDesc: 'Certified Current Account bank statements verifying commercial transaction volume.',
    category: 'Financial',
    issuingAuthority: 'Scheduled Commercial Bank / Cooperative Bank',
    guidance: 'Obtain digitally signed e-statements with bank stamp or Member Lending Institution appraisal letter.',
    schemePdfSources: ['Circular 257 - CGS for Export credit merged.pdf', 'pmegp scheme.pdf', 'TReDS Cicular 262.pdf', 'cvy.schemes.pdf'],
    commonAliases: ['bank_statements', 'bank_iec', 'bank_appraisal', 'bank_sanction', 'bank_passbook'],
  },
  {
    id: 'audited_balance_sheet',
    name: 'CA Audited Balance Sheet & P&L (Past 3 Years)',
    shortDesc: 'Statutory financial audit statements certified by a practicing Chartered Accountant with UDIN.',
    category: 'Financial',
    issuingAuthority: 'Practicing Chartered Accountant (ICAI / UDIN Certified)',
    guidance: 'Must contain trading account, profit & loss, balance sheet, and depreciation schedule.',
    schemePdfSources: ['GR09082023.pdf', 'Guideline09082023.pdf', 'Final and approved IC Scheme Guidelines-2021.pdf', 'msme-cdp.pdf'],
    commonAliases: ['audited_balance_sheet', 'balance_sheet', 'ca_turnover', 'ca_fixed_assets', 'association_reg', 'pnl'],
  },
  {
    id: 'ca_networth',
    name: 'CA Gross Fixed Capital Investment (GFCI) & Net Worth Certificate',
    shortDesc: 'CA Certificate certifying eligible plant, machinery, testing equipment, and net worth.',
    category: 'Financial',
    issuingAuthority: 'Chartered Accountant (ICAI UDIN)',
    guidance: 'Required for Gujarat Industrial Policy capital subsidy & interest subvention reimbursement claims.',
    schemePdfSources: ['GR09082023.pdf', 'Guideline09082023.pdf', 'Final and approved IC Scheme Guidelines-2021.pdf'],
    commonAliases: ['ca_plant_machinery', 'ca_turnover', 'ca_fixed_assets', 'ca_networth', 'gfci'],
  },
  {
    id: 'dpr',
    name: 'Detailed Project Report (DPR) & Techno-Economic Viability',
    shortDesc: 'Comprehensive project DPR covering machinery layout, civil estimates, and 5-year cash projections.',
    category: 'Technical',
    issuingAuthority: 'Accredited Technical Agency / Empaneled Project Consultant',
    guidance: 'Required for industrial parks, cluster infrastructure, PMEGP, SFURTI, PMFME, and PMMSY grant appraisals.',
    schemePdfSources: ['pmegp scheme.pdf', 'SFURTI_NEW_GUIDELINES.pdf', 'msme-cdp.pdf', 'Pradhan Mantri Formalisation Of Micro Food Processing Enterprises guideline.pdf', 'ICDP_388 for coffee development.pdf', 'PMMSY Guidelines 24 June, 2020.pdf'],
    commonAliases: ['dpr', 'project_report', 'pmegp_app', 'state_dpr', 'dpr_ta', 'pmfme_dpr', 'pmmsy_proposal', 'research_proposal'],
  },
  {
    id: 'machinery_quotations',
    name: 'Machinery Invoices & Proforma Quotations with HSN/GST',
    shortDesc: 'Detailed vendor quotations or purchase invoices confirming BIS standards & HSN codes.',
    category: 'Commercial',
    issuingAuthority: 'Original Equipment Manufacturer (OEM) / Certified Machinery Vendor',
    guidance: 'Required for validating capital cost eligibility under CITUS, CLCSS, and capital subsidy schemes.',
    schemePdfSources: ['pmegp scheme.pdf', 'cvy.schemes.pdf', 'GR09082023.pdf', 'ZED_Guidance_Document_NIC_Division_24.pdf'],
    commonAliases: ['machinery_invoices', 'export_po', 'digital_invoice', 'project_quotation', 'stall_bill', 'perf_guarantee', 'quotations'],
  },
  {
    id: 'term_loan_sanction',
    name: 'Bank Term Loan Sanction & Disbursement Advice',
    shortDesc: 'Formal sanction letter from a Member Lending Institution (MLI) detailing interest & margin rate.',
    category: 'Financial',
    issuingAuthority: 'Commercial Bank / SIDBI / NABARD',
    guidance: 'Needed for claiming interest subvention (up to 7%) or capital investment subsidies.',
    schemePdfSources: ['pmegp scheme.pdf', 'Circular 257 - CGS for Export credit merged.pdf', 'GR09082023.pdf', 'cvy.schemes.pdf'],
    commonAliases: ['term_loan_sanction', 'bank_sanction', 'bank_loan_sanction', 'bank_appraisal', 'loan_sanction'],
  },
  {
    id: 'gidc_land',
    name: 'Land Title Deed / GIDC Allotment / Registered Lease (10+ Yrs)',
    shortDesc: 'Encumbrance-free title deed, GIDC industrial plot allotment letter, or registered lease deed.',
    category: 'Infrastructure',
    issuingAuthority: 'Gujarat Industrial Development Corporation (GIDC) / Revenue Dept',
    guidance: 'Mandatory proof of possession for setting up manufacturing sheds, parks, or common facility centres.',
    schemePdfSources: ['msme-cdp.pdf', 'SFURTI_NEW_GUIDELINES.pdf', 'GR09082023.pdf'],
    commonAliases: ['gidc_land', 'land_lease', 'land_clearance', 'land_lease_pond', 'land_title'],
  },
  {
    id: 'gpcb_clearance',
    name: 'Pollution Control Board Consent (GPCB / SPCB CTE/CTO)',
    shortDesc: 'Consent to Establish (CTE) / Consent to Operate (CTO) or White Category Exemption NOC.',
    category: 'Regulatory',
    issuingAuthority: 'Gujarat Pollution Control Board (GPCB) / State PCB',
    guidance: 'Apply online via GPCB OCMMS portal. Mandatory for industrial park, chemical, and textile operations.',
    schemePdfSources: ['msme-cdp.pdf', 'GR09082023.pdf', 'ZED_Guidance_Document_NIC_Division_24.pdf'],
    commonAliases: ['gpcb_clearance', 'pollution_noc', 'cte_cto', 'gpcb'],
  },
  {
    id: 'iec',
    name: 'Active Importer-Exporter Code (DGFT IEC)',
    shortDesc: 'Valid 10-digit DGFT IEC code linked to PAN and verified bank account.',
    category: 'Statutory',
    issuingAuthority: 'Directorate General of Foreign Trade (DGFT)',
    guidance: 'Mandatory for CGTMSE EPM Export Credit Guarantee and international trade fair assistance.',
    schemePdfSources: ['Circular 257 - CGS for Export credit merged.pdf', 'Final and approved IC Scheme Guidelines-2021.pdf'],
    commonAliases: ['iec', 'dgft_iec', 'cbfte_bills', 'export_po'],
  },
  {
    id: 'zed_cert',
    name: 'MSME ZED Certificate / Digital Pledge Undertaking',
    shortDesc: 'ZED Bronze, Silver, or Gold certification or online pledge confirmation from Quality Council.',
    category: 'Statutory',
    issuingAuthority: 'Quality Council of India (QCI) / zed.msme.gov.in',
    guidance: 'Unlocks priority bank lending, concessional processing fees, and financial assistance.',
    schemePdfSources: ['ZED_Guidance_Document_NIC_Division_24.pdf', 'ZED_Guidance_Document_NIC_Division_27.pdf'],
    commonAliases: ['zed_pledge', 'fee_receipt', 'zed_cert', 'zed'],
  },
  {
    id: 'fssai',
    name: 'FSSAI Food Safety License / Registration',
    shortDesc: 'Statutory food business operator license issued under the Food Safety and Standards Act.',
    category: 'Regulatory',
    issuingAuthority: 'Food Safety and Standards Authority of India (FSSAI)',
    guidance: 'Mandatory prerequisite for PMFME and agro-processing enterprise subsidies.',
    schemePdfSources: ['Pradhan Mantri Formalisation Of Micro Food Processing Enterprises guideline.pdf', 'PMMSY Guidelines 24 June, 2020.pdf'],
    commonAliases: ['fssai_cert', 'fssai_license', 'fssai'],
  },
  {
    id: 'caste_cert',
    name: 'Caste / Community Certificate (SC / ST / OBC / SEBC)',
    shortDesc: 'Official caste certificate issued by competent revenue authority for special credit benefits.',
    category: 'Special Category',
    issuingAuthority: 'Sub-Divisional Magistrate (SDM) / Tehsildar / District Social Welfare Dept',
    guidance: 'Mandatory for National SC-ST Hub (NSSH), Dr. Ambedkar development loan, and GBCDC concessional loans.',
    schemePdfSources: ['NSSH_Guidelines_Sub_scheme_1.pdf', 'Loan for Small Businesses (DAADC).pdf', 'Swayam Saksham Yojana (GBCDC).pdf', 'Pashupalan (GBCDC).pdf', 'mahila_samrudhi_2020.pdf'],
    commonAliases: ['caste_cert', 'sc_st_cert', 'obc_cert', 'sebc_cert', 'aadhaar_pan'],
  },
  {
    id: 'income_cert',
    name: 'Family Income / BPL / Non-Creamy Layer Certificate',
    shortDesc: 'Annual income assessment certificate verifying eligibility for subsidized welfare schemes.',
    category: 'Special Category',
    issuingAuthority: 'Talati-cum-Mantri / Mamlatdar / Revenue Office',
    guidance: 'Required for state concessional loans, foreign study loans, and marginalized worker awards.',
    schemePdfSources: ['Foreign Study Loan.pdf', 'Loan for Small Businesses (DAADC).pdf', 'mahila_samrudhi_2020.pdf', 'Scheme For Grant Of Rewards To The Children Of Salt Labourers.pdf'],
    commonAliases: ['income_cert', 'bpl_cert', 'income_certificate', 'ncl_cert'],
  },
  {
    id: 'power_water',
    name: 'HT/LT Power Line Feeder & Water Allocation NOC',
    shortDesc: 'Power load sanction letter from DISCOM and water connection allotment certificate.',
    category: 'Infrastructure',
    issuingAuthority: 'State Electricity DISCOM (e.g. DGVCL/UGVCL) / Local Authority',
    guidance: 'Prerequisite for physical site inspection and industrial park infrastructure grants.',
    schemePdfSources: ['GR09082023.pdf', 'msme-cdp.pdf', 'SFURTI_NEW_GUIDELINES.pdf'],
    commonAliases: ['power_water', 'electricity_bill', 'power_sanction'],
  },
  {
    id: 'incorporation_docs',
    name: 'Certificate of Incorporation & MoA / Partnership Deed',
    shortDesc: 'Certificate of Incorporation, Articles of Association, or registered Partnership Agreement.',
    category: 'Statutory',
    issuingAuthority: 'Ministry of Corporate Affairs (MCA) / Registrar of Firms',
    guidance: 'Legal constitution proof for SPVs, private limited firms, LLPs, and cluster associations.',
    schemePdfSources: ['msme-cdp.pdf', 'SFURTI_NEW_GUIDELINES.pdf', 'Final and approved IC Scheme Guidelines-2021.pdf'],
    commonAliases: ['spv_reg', 'spv_mou', 'association_reg', 'sbd_compliance', 'gem_procurement', 'non_alienation', 'non_duplication', 'coi', 'moa'],
  },
  {
    id: 'treds_reg',
    name: 'TReDS Platform Onboarding Registration (RXIL / M1xchange)',
    shortDesc: 'Proof of registration on RBI-approved Trade Receivables Discounting System platform.',
    category: 'Commercial',
    issuingAuthority: 'RXIL / M1xchange / Invoicemart / RBI',
    guidance: 'Prerequisite for factoring coverage under CGTMSE Circular 262.',
    schemePdfSources: ['TReDS Cicular 262.pdf'],
    commonAliases: ['treds_reg', 'treds', 'rxil', 'm1xchange'],
  },
  {
    id: 'fisheries_license',
    name: 'Fisheries Dept License / Aquaculture Pond Lease Agreement',
    shortDesc: 'State fisheries department registration and legal pond/water body lease deed.',
    category: 'Regulatory',
    issuingAuthority: 'Department of Fisheries / Marine Products Export Development Authority (MPEDA)',
    guidance: 'Mandatory for fish farming, biofloc units, and cold chain assistance under PMMSY.',
    schemePdfSources: ['PMMSY Guidelines 24 June, 2020.pdf'],
    commonAliases: ['fisheries_license', 'pmmsy_lease', 'pond_lease'],
  },
  {
    id: 'academic_marksheet',
    name: 'Academic Marksheet, Degree & College Admission Letter',
    shortDesc: 'Authenticated marksheet and university admission verification for educational support.',
    category: 'Special Category',
    issuingAuthority: 'Recognized University / State Secondary & Higher Secondary Education Board',
    guidance: 'Required for meritorious student scholarships, foreign education loans, and single girl child grants.',
    schemePdfSources: ['Foreign Study Loan.pdf', 'new_guideline_for_meritorious_student.pdf', 'Post Graduate Indira Gandhi Scholarship For Single Girl Child.pdf', 'Agnipath_Scheme.pdf'],
    commonAliases: ['academic_marksheet', 'marksheet', 'degree_cert', 'admission_letter', 'edu_cert'],
  },
  {
    id: 'fertilizer_mda_license',
    name: 'Organic Fertilizer Manufacturing License & FCO Test Certificate',
    shortDesc: 'Commercial production license and Fertiliser (Inorganic, Organic or Mixed) (Control) Order test report.',
    category: 'Regulatory',
    issuingAuthority: 'Ministry of Chemicals and Fertilizers / Dept of Agriculture',
    guidance: 'Mandatory for claiming ₹1,500/MT Market Development Assistance under PM-PRANAM.',
    schemePdfSources: ['Guidelines on Market Development Assistance (MDA) for Promotion of Organic Fertilizers - Regarding (20-09-2023)_0.pdf'],
    commonAliases: ['fertilizer_mda_license', 'fco_cert', 'organic_license'],
  },
  {
    id: 'labour_welfare_card',
    name: 'Construction / Saltpan Worker Welfare Identity Card',
    shortDesc: 'Registered welfare board identity card for construction or salt manufacturing workers.',
    category: 'Special Category',
    issuingAuthority: 'Gujarat Building & Other Construction Workers Welfare Board (GBOCWWB) / Salt Commissioner',
    guidance: 'Prerequisite for child hostel assistance and cash rewards under state welfare schemes.',
    schemePdfSources: ['Hostel Assistance Scheme for Children of Migrant Construction Workers (GBOCWWB).pdf', 'Scheme For Grant Of Rewards To The Children Of Salt Labourers.pdf'],
    commonAliases: ['labour_welfare_card', 'bocw_card', 'salt_worker_id'],
  },
]

export const DEFAULT_HELD_DOCUMENTS: string[] = [
  'udyam',
  'pan_gst',
  'bank_statements',
  'audited_balance_sheet',
]

/**
 * Retrieve user's held documents from local profile
 */
export function getUserHeldDocuments(): string[] {
  try {
    const raw = localStorage.getItem('udyamniti_user')
    if (raw) {
      const parsed = JSON.parse(raw)
      if (Array.isArray(parsed.held_documents) && parsed.held_documents.length > 0) {
        return parsed.held_documents
      }
    }
  } catch {}
  return [...DEFAULT_HELD_DOCUMENTS]
}

/**
 * Save user's held documents and notify active listeners
 */
export function saveUserHeldDocuments(docIds: string[]): void {
  try {
    const raw = localStorage.getItem('udyamniti_user')
    const user = raw ? JSON.parse(raw) : {}
    user.held_documents = docIds
    localStorage.setItem('udyamniti_user', JSON.stringify(user))
    window.dispatchEvent(new CustomEvent('udyamniti_documents_updated', { detail: docIds }))
  } catch (e) {
    console.error('Failed to save held documents:', e)
  }
}

/**
 * Check if a scheme required document is matched by the firm's held documents
 */
export function isDocumentHeld(requiredDocId: string, heldDocIds: string[]): boolean {
  if (!requiredDocId || !heldDocIds || heldDocIds.length === 0) return false
  const reqLower = requiredDocId.toLowerCase().trim()

  // Exact ID match
  if (heldDocIds.some((h) => h.toLowerCase() === reqLower)) return true

  // Match via official taxonomy definitions & aliases
  for (const docDef of STATUTORY_BUSINESS_DOCUMENTS) {
    const defIdMatch = docDef.id.toLowerCase() === reqLower
    const aliasMatch = docDef.commonAliases.some((alias) => alias.toLowerCase() === reqLower)

    if (defIdMatch || aliasMatch) {
      if (heldDocIds.includes(docDef.id)) return true
      if (docDef.commonAliases.some((alias) => heldDocIds.includes(alias))) return true
    }
  }

  // Semantic keyword fuzzy fallback
  for (const held of heldDocIds) {
    const heldLower = held.toLowerCase()
    if (reqLower.includes(heldLower) || heldLower.includes(reqLower)) return true
    if (reqLower.includes('udyam') && heldLower.includes('udyam')) return true
    if (reqLower.includes('bank') && (heldLower.includes('bank') || heldLower.includes('statement'))) return true
    if (reqLower.includes('land') && (heldLower.includes('land') || heldLower.includes('gidc'))) return true
    if (reqLower.includes('pollution') && (heldLower.includes('pollution') || heldLower.includes('gpcb'))) return true
    if (reqLower.includes('gpcb') && (heldLower.includes('gpcb') || heldLower.includes('clearance'))) return true
    if (reqLower.includes('dpr') && (heldLower.includes('dpr') || heldLower.includes('project'))) return true
    if (reqLower.includes('iec') && heldLower.includes('iec')) return true
    if (reqLower.includes('loan') && (heldLower.includes('loan') || heldLower.includes('sanction'))) return true
    if (reqLower.includes('turnover') && (heldLower.includes('balance') || heldLower.includes('networth') || heldLower.includes('ca'))) return true
    if (reqLower.includes('zed') && heldLower.includes('zed')) return true
    if (reqLower.includes('fssai') && heldLower.includes('fssai')) return true
    if (reqLower.includes('caste') && (heldLower.includes('caste') || heldLower.includes('sc') || heldLower.includes('st'))) return true
    if (reqLower.includes('income') && (heldLower.includes('income') || heldLower.includes('bpl'))) return true
    if (reqLower.includes('treds') && heldLower.includes('treds')) return true
    if (reqLower.includes('marksheet') && (heldLower.includes('academic') || heldLower.includes('marksheet') || heldLower.includes('edu'))) return true
  }

  return false
}

export interface SchemeDocAnalysis {
  matchingDocs: Array<{ id: string; name: string; desc?: string; category?: string; issuingAuthority?: string }>
  missingDocs: Array<{ id: string; name: string; desc?: string; category?: string; mandatory: boolean; guidance?: string; issuingAuthority?: string }>
  totalCount: number
  heldCount: number
  readinessPercentage: number
  status: 'READY' | 'ACTION_REQUIRED' | 'CRITICAL_GAPS'
  aiSummary: string
  blockerHeadline: string
  actionableRoadmap: Array<{ docName: string; action: string; authority: string }>
}

/**
 * Perform comprehensive statutory comparison and synthesize an AI gap report for a scheme
 */
export function analyzeSchemeDocuments(
  requiredDocs: Array<{ id: string; name: string; desc?: string; category?: string; mandatory?: boolean }> | undefined,
  heldDocIds: string[]
): SchemeDocAnalysis {
  const docs = Array.isArray(requiredDocs) && requiredDocs.length > 0 ? requiredDocs : []
  const totalCount = docs.length

  if (totalCount === 0) {
    return {
      matchingDocs: [],
      missingDocs: [],
      totalCount: 0,
      heldCount: 0,
      readinessPercentage: 100,
      status: 'READY',
      aiSummary: 'This scheme does not prescribe preliminary document gatekeepers. Standard statutory KYC is sufficient.',
      blockerHeadline: 'No document blockers identified.',
      actionableRoadmap: [],
    }
  }

  const matchingDocs: SchemeDocAnalysis['matchingDocs'] = []
  const missingDocs: SchemeDocAnalysis['missingDocs'] = []

  docs.forEach((doc) => {
    const isHeld = isDocumentHeld(doc.id, heldDocIds)
    const matchingTaxonomy = STATUTORY_BUSINESS_DOCUMENTS.find(
      (t) => t.id === doc.id || t.commonAliases.includes(doc.id)
    )

    if (isHeld) {
      matchingDocs.push({
        id: doc.id,
        name: doc.name,
        desc: doc.desc,
        category: doc.category || matchingTaxonomy?.category || 'Statutory',
        issuingAuthority: matchingTaxonomy?.issuingAuthority || 'Competent Authority',
      })
    } else {
      missingDocs.push({
        id: doc.id,
        name: doc.name,
        desc: doc.desc,
        category: doc.category || matchingTaxonomy?.category || 'Mandatory Prerequisite',
        mandatory: doc.mandatory !== false,
        guidance: matchingTaxonomy?.guidance || 'Compile certified copies and obtain statutory sign-off before application.',
        issuingAuthority: matchingTaxonomy?.issuingAuthority || 'Issuing Authority / Portal',
      })
    }
  })

  const heldCount = matchingDocs.length
  const readinessPercentage = Math.round((heldCount / totalCount) * 100)

  let status: SchemeDocAnalysis['status'] = 'READY'
  if (readinessPercentage < 50) {
    status = 'CRITICAL_GAPS'
  } else if (readinessPercentage < 100) {
    status = 'ACTION_REQUIRED'
  }

  // Synthesize AI Gap & Readiness Summary
  let aiSummary = ''
  let blockerHeadline = ''

  if (readinessPercentage === 100) {
    aiSummary = `Complete Document Compliance (100% Ready): Your firm possesses all ${totalCount} required documents for this scheme. Your statutory dossier meets all preliminary eligibility and physical scrutiny criteria. You are fully positioned to proceed with immediate application submission.`
    blockerHeadline = 'Zero Document Blockers: Ready for Immediate Submission'
  } else if (readinessPercentage >= 60) {
    const missingNames = missingDocs.map((d) => d.name).join(', ')
    aiSummary = `Strong Document Foundation (${readinessPercentage}% Ready): Your firm holds ${heldCount} out of ${totalCount} required statutory documents (${matchingDocs.map((d) => d.name).join(', ')}). However, ${missingDocs.length} required document(s) are currently missing: ${missingNames}. These must be arranged to avoid rejection during departmental desk review.`
    blockerHeadline = `Missing ${missingDocs.length} Prerequisite Document(s) to Complete Application`
  } else {
    const missingNames = missingDocs.map((d) => d.name).join(', ')
    aiSummary = `Critical Statutory Gaps (${readinessPercentage}% Ready): Your enterprise currently possesses only ${heldCount} of the ${totalCount} mandatory documents. Key missing prerequisites include: ${missingNames}. Under government operational guidelines, applications submitted without these documents face immediate gatekeeper disqualification.`
    blockerHeadline = `Gatekeeper Blockers: Firm Needs ${missingDocs.length} Mandatory Document(s)`
  }

  const actionableRoadmap = missingDocs.map((doc) => ({
    docName: doc.name,
    action: doc.guidance || 'Acquire certified copy from the issuing department.',
    authority: doc.issuingAuthority || 'Governing Authority',
  }))

  return {
    matchingDocs,
    missingDocs,
    totalCount,
    heldCount,
    readinessPercentage,
    status,
    aiSummary,
    blockerHeadline,
    actionableRoadmap,
  }
}
