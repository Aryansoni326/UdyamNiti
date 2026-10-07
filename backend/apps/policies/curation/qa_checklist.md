# Quality Assurance (QA) Checklist & Peer Review Protocol

**Target Application**: Knowledge Base Ingestion for Central & Gujarat MSME Programs  
**Protocol Requirement**: Four-Eyes Principle (No record may be ingested without Curator and Reviewer signatures)

---

## 24-Point Scheme Curation QA Rubric

### 🏛️ Section A: Source Authenticity & Legal Authority (Items 1–4)
- [ ] **A.1 Official Domain Verification**: The primary document URL is hosted strictly on an approved `.gov.in` or `.nic.in` domain (or official nodal bank portal like `cgtmse.in`, `sidbi.in`). Third-party sites (`indiamart`, `cleartax`, `startupindia.gov.in` aggregation blogs) are not used.
- [ ] **A.2 Source Tiering Designated**: The authority tier is correctly classified (`tier_1_gazette`, `tier_2_operational_guidelines`, `tier_3_ministry_circular`, or `tier_4_portal_faq`).
- [ ] **A.3 Document Identifier Present**: An official notification number, circular number, or Government Resolution (GR) reference ID is recorded (e.g., `F.No. 1(2)/CLCSS/2024` or `GR No. SSI-102020-Gujarat`).
- [ ] **A.4 PDF Integrity Archival**: The source PDF has been downloaded, archived in the repository storage, and verified accessible.

### 🔍 Section B: Verbatim Evidence & Provenance Pinpointing (Items 5–8)
- [ ] **B.1 Verbatim Excerpt Accuracy**: The quote in `exact_quote` matches the official document word-for-word without summarization, omission, or paraphrasing.
- [ ] **B.2 Clause & Section Pinpointing**: The specific clause, sub-clause, or section number is explicitly referenced (e.g., `Clause 4.1(b)`).
- [ ] **B.3 Physical PDF Page Number**: The physical page number where the text appears in the PDF reader is documented.
- [ ] **B.4 Zero Hallucination**: No conditions, criteria, or limits are added from oral advice, hearsay, or consultant interpretation.

### ⚙️ Section C: Deterministic Rule Codification (Items 9–13)
- [ ] **C.1 Valid Profile Field Paths**: All `field_path` entries map to verified `BusinessProfile` attributes (e.g. `business_profile.msme_category`, `business_profile.investment_in_plant_machinery_lakhs`).
- [ ] **C.2 Operator Correctness**: The operator (`eq`, `in`, `lte`, `bool_false`, etc.) correctly mirrors the statutory boundary (e.g. "does not exceed ₹100 Lakh" must be `lte 100.0`, not `lt 100.0`).
- [ ] **C.3 Clean Disqualification (Mandatory vs Preferred)**: Mandatory conditions that disqualify an enterprise are marked `importance: "mandatory"`. Scored criteria are marked `preferred`.
- [ ] **C.4 Plain-English Failure Messages**: Each rule includes an informative `failure_message` explaining why an enterprise was rejected and how to rectify if possible.
- [ ] **C.5 Ambiguity Logging**: Discretionary provisions (e.g. "acceptable bank viability appraisal") are flagged in `ambiguity_notes` rather than coded as binary filters.

### 🔗 Section D: Stacking, Sequencing & Non-Duplication (Items 14–17)
- [ ] **D.1 GFR 230(1) Anti-Duplication Check**: Checked whether the central scheme bars claiming another central subsidy for the exact same capital expenditure.
- [ ] **D.2 State Top-up Allowance Verified**: If mapped as `stacks_with` a state scheme (e.g. Gujarat Capital Subsidy), the state guideline authorizing top-up assistance is cited.
- [ ] **D.3 Prerequisites Explicitly Sequenced**: If a scheme requires prior milestone completion (e.g. Udyam Registration, ZED pledge, bank term loan sanction), it is mapped as `prerequisite_for`.
- [ ] **D.4 Exclusions & Negative List Captured**: Statutory negative lists (tobacco, liquor, power generation) are explicitly documented under `exclusions`.

### 💰 Section E: Benefit Formula & Financial Precision (Items 18–20)
- [ ] **E.1 Formula Type Alignment**: The `formula_type` (`percentage_of_capex`, `interest_rebate`, `credit_guarantee`) matches the statutory delivery mechanism.
- [ ] **E.2 Percentage & Cap Exactness**: The subsidy percentage and statutory monetary ceiling in INR Lakhs match the gazette table exactly.
- [ ] **E.3 Priority Multipliers Verified**: Affirmative action bonuses (women-owned, SC/ST, aspirational district/taluka categories) have explicit documentary basis.

### 🌐 Section F: Application Route & Deadlines (Items 21–22)
- [ ] **F.1 Direct Statutory Portal Link**: `official_application_url` leads directly to the official filing system, not an informational landing page or marketing splash.
- [ ] **F.2 Effective Dates Verified**: `effective_date` corresponds to scheme notification; `effective_until` captures sunset date (or is null if open-ended).

### ✍️ Section G: Two-Person Review Gate (Items 23–24)
- [ ] **G.1 Curator Self-Audit Completed**: The researcher has run the automated validation script without errors.
- [ ] **G.2 Second-Eye Independent Review**: A secondary reviewer has independently inspected the source PDF, verified the quotes, and signed below.

---

## Sign-Off Block

| Role | Name | Organization / Department | Signature / Date | Status |
|---|---|---|---|---|
| **Curator** | ____________________ | Policy Research Team | _________________ | `[ ] DRAFT [ ] SUBMITTED` |
| **Reviewer** | ____________________ | Legal & Compliance Review | _________________ | `[ ] APPROVED [ ] REVISION NEEDED` |
| **KB Lead** | ____________________ | Knowledge Platform Lead | _________________ | `[ ] PUBLISHED [ ] ARCHIVED` |
