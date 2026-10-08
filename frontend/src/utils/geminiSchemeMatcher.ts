import { ALL_OFFICIAL_SCHEMES, OfficialSchemeItem } from '../data/officialSchemes'
import { getUserHeldDocuments, isDocumentHeld, STATUTORY_BUSINESS_DOCUMENTS } from './documentChecklist'

export interface GeminiMatchResultItem {
  scheme: OfficialSchemeItem
  matchScore: number
  whyMatched: string
  keyBenefit: string
  mandatoryDocuments: string[]
  missingDocuments: string[]
  heldDocuments: string[]
  isFullyDocumentReady: boolean
  actionStep: string
}

export interface GeminiMatchResponse {
  userQuery: string
  detectedSector: string
  detectedScale: string
  detectedNeed: string
  executiveSummary: string
  matchedSchemes: GeminiMatchResultItem[]
  strategicRoadmap: string[]
  modelUsed: string
}

const GEMINI_API_KEY =
  (import.meta as any).env?.VITE_GEMINI_API_KEY ||
  (import.meta as any).env?.GEMINI_API_KEY ||
  ''

/**
 * Condensed scheme catalog representation provided to Gemini for optimal context and speed
 */
function buildSchemeCatalogPrompt(): string {
  return ALL_OFFICIAL_SCHEMES.map((s, idx) => {
    return `${idx + 1}. [${s.code}] "${s.name}" (${s.shortName})
- Ministry: ${s.ministry} | Division: ${s.division}
- Category: ${s.category} | Max Benefit: ${s.maxBenefit}
- Highlights: ${s.highlight}
- Gazette: ${s.gazette} | PDF: ${s.pdfFile}
- Target Sectors: ${s.targetSectors.join(', ')}
- Target States: ${s.targetStates.join(', ')}`
  }).join('\n\n')
}

/**
 * Intelligent local semantic matcher fallback if network/quota is unavailable
 */
export function localSemanticMatch(query: string, userHeldDocs: string[] = getUserHeldDocuments()): GeminiMatchResponse {
  const q = query.toLowerCase()
  const scored = ALL_OFFICIAL_SCHEMES.map((scheme) => {
    let score = scheme.baseMatch || 70
    const textToMatch = `${scheme.name} ${scheme.shortName} ${scheme.highlight} ${scheme.category} ${scheme.division} ${scheme.ministry} ${scheme.targetSectors.join(' ')} ${scheme.targetStates.join(' ')}`.toLowerCase()

    const words = q.split(/\s+/).filter((w) => w.length > 2)
    let hitCount = 0
    for (const w of words) {
      if (textToMatch.includes(w)) hitCount++
    }

    if (q.includes('solar') || q.includes('green') || q.includes('rooftop')) {
      if (scheme.category === 'quality_certification' || scheme.code.includes('ZED') || scheme.division.includes('Gujarat')) score += 35
      if (scheme.code.includes('CGTMSE') || scheme.category === 'credit_guarantee') score += 25
    }
    if (q.includes('textile') || q.includes('cotton') || q.includes('fabric')) {
      if (scheme.targetSectors.includes('textiles') || scheme.division.includes('Gujarat')) score += 30
    }
    if (q.includes('export') || q.includes('foreign') || q.includes('niryat')) {
      if (scheme.category === 'export_support' || scheme.code.includes('EXPORT') || scheme.code.includes('EPM') || scheme.code.includes('IC_SCHEME')) score += 40
    }
    if (q.includes('collateral') || q.includes('loan') || q.includes('credit') || q.includes('guarantee')) {
      if (scheme.category === 'credit_guarantee' || scheme.code.includes('CGTMSE') || scheme.code.includes('TREDS')) score += 35
    }
    if (q.includes('machinery') || q.includes('equipment') || q.includes('plant')) {
      if (scheme.category === 'capital_subsidy' || scheme.code.includes('PMEGP') || scheme.code.includes('COIR')) score += 30
    }
    if (q.includes('women') || q.includes('female') || q.includes('mahila')) {
      if (scheme.code.includes('MAHILA') || scheme.code.includes('WOMEN') || scheme.name.toLowerCase().includes('mahila') || scheme.name.toLowerCase().includes('women')) score += 40
    }
    if (q.includes('sc') || q.includes('st') || q.includes('dalit') || q.includes('tribal') || q.includes('backward')) {
      if (scheme.code.includes('NSSH') || scheme.code.includes('DAADC') || scheme.code.includes('GBCDC')) score += 40
    }
    if (q.includes('food') || q.includes('agro') || q.includes('pickle') || q.includes('processing')) {
      if (scheme.code.includes('PMFME') || scheme.targetSectors.includes('food') || scheme.division.includes('Agriculture')) score += 40
    }
    if (q.includes('fish') || q.includes('matsya') || q.includes('aquaculture')) {
      if (scheme.code.includes('PMMSY')) score += 50
    }
    if (q.includes('student') || q.includes('study') || q.includes('scholarship') || q.includes('college')) {
      if (scheme.code.includes('STUDY') || scheme.code.includes('MERIT') || scheme.code.includes('SCHOLARSHIP')) score += 50
    }

    score += hitCount * 12
    return { scheme, score }
  })

  scored.sort((a, b) => b.score - a.score)
  const topMatches = scored.slice(0, 5)

  const matchedItems: GeminiMatchResultItem[] = topMatches.map(({ scheme, score }) => {
    const requiredDocList = [
      'MSME Udyam Registration Certificate',
      'Entity PAN & Active GSTIN Certificate',
      '12-Month Bank Statements',
      'Detailed Project Report (DPR)',
    ]
    if (scheme.category === 'export_support' || scheme.code.includes('EXPORT')) requiredDocList.push('Active Importer-Exporter Code (IEC)')
    if (scheme.category === 'quality_certification') requiredDocList.push('MSME ZED Digital Pledge / Certificate')
    if (scheme.targetSectors.includes('food')) requiredDocList.push('FSSAI Food Safety License')

    const heldList: string[] = []
    const missingList: string[] = []

    requiredDocList.forEach((docName) => {
      const matchDoc = STATUTORY_BUSINESS_DOCUMENTS.find((d) => d.name === docName)
      const docId = matchDoc ? matchDoc.id : docName.toLowerCase()
      if (isDocumentHeld(docId, userHeldDocs)) {
        heldList.push(docName)
      } else {
        missingList.push(docName)
      }
    })

    return {
      scheme,
      matchScore: Math.min(99, Math.max(78, score)),
      whyMatched: `Directly matches your requirement for ${scheme.category.replace('_', ' ')}. Provides ${scheme.maxBenefit} with government-backed assistance under ${scheme.gazette}.`,
      keyBenefit: scheme.maxBenefit,
      mandatoryDocuments: requiredDocList,
      heldDocuments: heldList,
      missingDocuments: missingList,
      isFullyDocumentReady: missingList.length === 0,
      actionStep: `Prepare ${missingList.length > 0 ? missingList[0] : 'application dossier'} and submit online under ${scheme.ministry}.`,
    }
  })

  return {
    userQuery: query,
    detectedSector: 'MSME Manufacturing & Services',
    detectedScale: 'Micro / Small Enterprise',
    detectedNeed: 'Financial & Capital Assistance',
    executiveSummary: `Based on your stated need: "${query}", UdyamNiti AI identified ${matchedItems.length} high-impact government schemes offering up to ${matchedItems[0]?.keyBenefit} in fiscal support and risk coverage.`,
    matchedSchemes: matchedItems,
    strategicRoadmap: [
      '1. Verify active Udyam registration and KYC compliance.',
      '2. Compile mandatory project quotation and bank financial statements.',
      '3. Submit statutory application on the official Ministry portal.',
      '4. Track physical sanction and claim direct benefit transfer (DBT).',
    ],
    modelUsed: 'UdyamNiti Deterministic Semantic Matcher (Corpus Verified)',
  }
}

/**
 * Main Gemini AI Scheme Matcher
 * Calls Gemini API with structured JSON output and falls back gracefully
 */
export async function matchSchemesWithGemini(
  query: string,
  userProfile?: any
): Promise<GeminiMatchResponse> {
  const cleanQuery = query.trim()
  if (!cleanQuery) {
    throw new Error('Please enter your business requirement or query.')
  }

  const heldDocs = getUserHeldDocuments()
  const userHeldDocsText = STATUTORY_BUSINESS_DOCUMENTS.filter((d) => heldDocs.includes(d.id))
    .map((d) => d.name)
    .join(', ') || 'Udyam Certificate, PAN, GST, Bank Statements'

  const profileContext = userProfile
    ? `User Profile:
- Enterprise: ${userProfile.name || 'MSME Enterprise'}
- State: ${userProfile.state || 'Gujarat'}
- Sector: ${userProfile.sector || 'Manufacturing'}
- Category: ${userProfile.category || 'Micro Enterprise'}
- Documents Currently Possessed: ${userHeldDocsText}`
    : `User Profile:
- Documents Currently Possessed: ${userHeldDocsText}`

  const systemPrompt = `You are UdyamNiti's Principal AI Policy Officer and Government Scheme Matching Expert.
Your task is to analyze an Indian MSME entrepreneur's natural language request (in English, Hindi, or Gujarati), understand their exact business intent, and recommend ONLY the most relevant official schemes from the provided scheme corpus.

SCHEME CORPUS (32 VERIFIED CENTRAL & STATE SCHEMES FROM GAZETTE PDFS):
${buildSchemeCatalogPrompt()}

USER CONTEXT:
${profileContext}

USER REQUIREMENT STATEMENT:
"${cleanQuery}"

INSTRUCTIONS:
1. Identify the user's primary requirement (e.g. collateral-free loan, solar rooftop subsidy, machinery purchase, export finance, artisan cluster, female entrepreneur support, agriculture/food processing, etc.).
2. Select between 2 to 5 EXACT matching schemes from the SCHEME CORPUS that address their specific need. DO NOT invent schemes outside the corpus.
3. For each matched scheme, provide:
   - "scheme_code": Exact scheme code from the list above.
   - "match_score": Number between 75 and 99 reflecting relevance.
   - "why_matched": Clear 1-2 sentence explanation tailored specifically to their requirement.
   - "key_benefit": Highlight of the maximum subsidy or financial guarantee.
   - "mandatory_documents": Array of 3-5 key documents required based on the scheme's PDF guidelines.
   - "action_step": Concrete first step for the entrepreneur to apply.
4. Return strict JSON following this schema:
{
  "detected_sector": "e.g. Textile / Solar / Food Processing / Engineering",
  "detected_scale": "e.g. Micro / Small / Medium",
  "detected_need": "e.g. Working Capital / Machinery Subsidy / Export Cover",
  "executive_summary": "1-2 sentence strategic overview of how the matched schemes solve their requirement.",
  "matched_schemes": [
    {
      "scheme_code": "CODE",
      "match_score": 98,
      "why_matched": "explanation",
      "key_benefit": "amount or percentage",
      "mandatory_documents": ["Doc 1", "Doc 2"],
      "action_step": "step"
    }
  ],
  "strategic_roadmap": [
    "Step 1: ...",
    "Step 2: ...",
    "Step 3: ..."
  ]
}`

  const modelsToTry = ['gemini-3-flash-preview', 'gemini-2.5-flash', 'gemini-flash-latest']

  for (const model of modelsToTry) {
    try {
      const url = `https://generativelanguage.googleapis.com/v1beta/models/${model}:generateContent?key=${encodeURIComponent(GEMINI_API_KEY)}`
      const controller = new AbortController()
      const timeoutId = setTimeout(() => controller.abort(), 12000)

      const response = await fetch(url, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        signal: controller.signal,
        body: JSON.stringify({
          contents: [{ parts: [{ text: systemPrompt }] }],
          generationConfig: {
            temperature: 0.1,
            responseMimeType: 'application/json',
          },
        }),
      })
      clearTimeout(timeoutId)

      if (response.ok) {
        const data = await response.json()
        const rawText = data?.candidates?.[0]?.content?.parts?.[0]?.text
        if (rawText) {
          const parsed = JSON.parse(rawText)
          if (Array.isArray(parsed.matched_schemes) && parsed.matched_schemes.length > 0) {
            const matchedItems: GeminiMatchResultItem[] = []

            for (const item of parsed.matched_schemes) {
              const schemeObj = ALL_OFFICIAL_SCHEMES.find(
                (s) => s.code.toLowerCase() === (item.scheme_code || '').toLowerCase()
              ) || ALL_OFFICIAL_SCHEMES.find(
                (s) => s.name.toLowerCase().includes((item.scheme_code || '').toLowerCase()) ||
                       (item.scheme_code || '').toLowerCase().includes(s.code.toLowerCase())
              )

              if (schemeObj) {
                const reqDocs: string[] = Array.isArray(item.mandatory_documents) && item.mandatory_documents.length > 0
                  ? item.mandatory_documents
                  : [
                      'MSME Udyam Registration Certificate',
                      'Entity PAN & Active GSTIN Certificate',
                      '12-Month Audited Bank Statements',
                      'Detailed Project Report (DPR)',
                    ]

                const heldList: string[] = []
                const missingList: string[] = []

                reqDocs.forEach((docName) => {
                  const matchDoc = STATUTORY_BUSINESS_DOCUMENTS.find(
                    (d) => d.name.toLowerCase().includes(docName.toLowerCase()) || docName.toLowerCase().includes(d.name.toLowerCase())
                  )
                  const docId = matchDoc ? matchDoc.id : docName.toLowerCase()
                  if (isDocumentHeld(docId, heldDocs)) {
                    heldList.push(docName)
                  } else {
                    missingList.push(docName)
                  }
                })

                matchedItems.push({
                  scheme: schemeObj,
                  matchScore: item.match_score || 95,
                  whyMatched: item.why_matched || `Matches your requirement for ${schemeObj.category}.`,
                  keyBenefit: item.key_benefit || schemeObj.maxBenefit,
                  mandatoryDocuments: reqDocs,
                  heldDocuments: heldList,
                  missingDocuments: missingList,
                  isFullyDocumentReady: missingList.length === 0,
                  actionStep: item.action_step || `Review official gazette guidelines and submit via ${schemeObj.ministry}.`,
                })
              }
            }

            if (matchedItems.length > 0) {
              return {
                userQuery: cleanQuery,
                detectedSector: parsed.detected_sector || 'General MSME',
                detectedScale: parsed.detected_scale || 'Micro / Small Enterprise',
                detectedNeed: parsed.detected_need || 'Government Scheme Support',
                executiveSummary: parsed.executive_summary || `Gemini AI matched ${matchedItems.length} official schemes matching your requirements.`,
                matchedSchemes: matchedItems,
                strategicRoadmap: Array.isArray(parsed.strategic_roadmap) ? parsed.strategic_roadmap : [
                  '1. Verify active Udyam registration and statutory KYC.',
                  '2. Procure required machinery invoices and project DPR.',
                  '3. Submit application online to the competent authority.',
                ],
                modelUsed: `Google Gemini AI (${model})`,
              }
            }
          }
        }
      }
    } catch (modelErr) {
      console.warn(`Gemini call to ${model} encountered an issue:`, modelErr)
    }
  }

  // Fallback to local semantic matcher if all API calls fail or timeout
  console.info('Switching to local high-precision semantic matcher.')
  return localSemanticMatch(cleanQuery, heldDocs)
}
