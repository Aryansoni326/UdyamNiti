"""
Synthetic Demo Relationship Dataset.
Clearly labeled as DEMO DATA for development, evaluation, and hackathon presentation.
Captures canonical Indian MSME (Central + Gujarat) policy stacking, prerequisites, and exclusions.
"""
from typing import List, Dict, Any

SYNTHETIC_DEMO_RELATIONSHIPS: List[Dict[str, Any]] = [
    {
        "scheme_a_code": "GJ-CAPITAL-2025",
        "scheme_b_code": "GJ-INTEREST-2025",
        "relationship_type": "COMPATIBLE",
        "direction": "BIDIRECTIONAL",
        "affected_cost_categories": ["plant_and_machinery", "term_loan_interest"],
        "conditions": {
            "term_loan_required": True,
            "same_financial_institution": True,
            "non_duplication_status": "distinct_cost_heads"
        },
        "evidence_ids": ["chunk-gj-ind-pol-2025-sec4", "chunk-gj-gr-interest-sec2"],
        "policy_versions": {
            "GJ-CAPITAL-2025": "v2025.1",
            "GJ-INTEREST-2025": "v2025.1"
        },
        "description": (
            "[DEMO DATA - SYNTHETIC STATUTORY RELATIONSHIP] Synergistic stacking: Gujarat MSME Capital Investment Subsidy "
            "(25% on plant & machinery) and Gujarat Interest Subvention (7% on term loan) can be availed simultaneously "
            "for the same manufacturing expansion, because they address separate financial heads (asset capital vs debt servicing)."
        ),
        "source_evidence": (
            "Government Resolution No. SSI/102020/MSME-Incentive/W, Clause 4.3: 'An enterprise availing capital assistance "
            "under this resolution shall also be eligible for interest subsidy on the term loan sanctioned by Financial Institutions/Banks.'"
        ),
        "confidence": 1.0,
        "is_demo_data": True
    },
    {
        "scheme_a_code": "PMEGP-CENTRAL",
        "scheme_b_code": "GJ-CAPITAL-2025",
        "relationship_type": "INCOMPATIBLE",
        "direction": "BIDIRECTIONAL",
        "affected_cost_categories": ["plant_and_machinery"],
        "conditions": {
            "same_expenditure_invoice": True,
            "conflict_type": "non_duplication_violation"
        },
        "evidence_ids": ["chunk-pmegp-guidelines-para-11-2", "chunk-gj-resolution-rule-7"],
        "policy_versions": {
            "PMEGP-CENTRAL": "v2024.3",
            "GJ-CAPITAL-2025": "v2025.1"
        },
        "description": (
            "[DEMO DATA - SYNTHETIC STATUTORY RELATIONSHIP] Non-Duplication Exclusion: PMEGP Margin Money Subsidy cannot "
            "be combined with Gujarat State Capital Subsidy on the exact same plant and machinery investment. MSME policy guidelines "
            "strictly prohibit double-dipping from Central and State capital grant windows for the same physical asset."
        ),
        "source_evidence": (
            "PMEGP Operational Guidelines Para 11.2 & Gujarat Scheme Rule 7: 'Any unit which has availed capital subsidy / "
            "margin money from Central Government under any scheme shall not be eligible for capital subsidy under this scheme for the same assets.'"
        ),
        "confidence": 1.0,
        "is_demo_data": True
    },
    {
        "scheme_a_code": "CGTMSE-CENTRAL",
        "scheme_b_code": "GJ-CAPITAL-2025",
        "relationship_type": "SEQUENTIAL",
        "direction": "A_TO_B",
        "affected_cost_categories": ["credit_collateral", "plant_and_machinery"],
        "conditions": {
            "loan_sanction_first": True,
            "disbursement_proof_required": True,
            "window_days": 365
        },
        "evidence_ids": ["chunk-cgtmse-brochure-cl4", "chunk-gj-capital-procedural-manual"],
        "policy_versions": {
            "CGTMSE-CENTRAL": "v2024.1",
            "GJ-CAPITAL-2025": "v2025.1"
        },
        "description": (
            "[DEMO DATA - SYNTHETIC STATUTORY RELATIONSHIP] Procedural Sequencing: An enterprise should first secure bank term loan "
            "sanction under CGTMSE collateral-free guarantee. After machinery purchase and commencement of commercial production, "
            "the Gujarat Capital Subsidy application must be submitted within 1 year from the commercial production date."
        ),
        "source_evidence": (
            "Gujarat MSME Capital Assistance Operational Manual, Section 5: 'Application for capital assistance must be filed "
            "within one year from the Date of Commercial Production (DOCP) supported by term loan sanction letter from the lending institution.'"
        ),
        "confidence": 0.95,
        "is_demo_data": True
    },
    {
        "scheme_a_code": "CLCSS-CENTRAL",
        "scheme_b_code": "GJ-CAPITAL-2025",
        "relationship_type": "OVERLAPPING",
        "direction": "BIDIRECTIONAL",
        "affected_cost_categories": ["plant_and_machinery"],
        "conditions": {
            "both_claim_plant_and_machinery": True,
            "statutory_cap_applies": True
        },
        "evidence_ids": ["chunk-clcss-guidelines-sec9", "chunk-gj-ind-pol-2025-sec4"],
        "policy_versions": {
            "CLCSS-CENTRAL": "v2023.2",
            "GJ-CAPITAL-2025": "v2025.1"
        },
        "description": (
            "[DEMO DATA - SYNTHETIC STATUTORY RELATIONSHIP] Overlapping Cost Head: Both schemes provide upfront capital subsidy on "
            "plant and machinery. While an enterprise upgrading technology can theoretically explore both, total government capital "
            "assistance is capped and dual claims on the same machine invoice will be flagged during DIC/Bank audit."
        ),
        "source_evidence": (
            "CLCSS Guidelines Section 9.1: 'Incentives under CLCSS shall be adjusted against any state capital subsidy claimed for identical machinery.'"
        ),
        "confidence": 0.90,
        "is_demo_data": True
    },
    {
        "scheme_a_code": "MSME-ZED-CENTRAL",
        "scheme_b_code": "GJ-INTEREST-2025",
        "relationship_type": "COMPATIBLE",
        "direction": "BIDIRECTIONAL",
        "affected_cost_categories": ["quality_certification", "term_loan_interest"],
        "conditions": {
            "zed_certificate_active": True,
            "interest_subvention_top_up_unlocked": True
        },
        "evidence_ids": ["chunk-zed-guidelines-para-8", "chunk-gj-gr-interest-sec2"],
        "policy_versions": {
            "MSME-ZED-CENTRAL": "v2024.2",
            "GJ-INTEREST-2025": "v2025.1"
        },
        "description": (
            "[DEMO DATA - SYNTHETIC STATUTORY RELATIONSHIP] Incentive Top-Up Synergy: Obtaining ZED (Zero Defect Zero Effect) Bronze/Silver/Gold "
            "certification under the Central ZED scheme unlocks an additional 1% interest subvention bonus under the Gujarat Industrial Policy, "
            "reducing net borrowing cost from 7% to 8% total subvention."
        ),
        "source_evidence": (
            "Gujarat Industrial Policy 2025, Incentive Booster Clause 6.4: 'Enterprises possessing active ZED certification shall receive "
            "an additional 1% interest subsidy over and above the standard applicable rate.'"
        ),
        "confidence": 0.98,
        "is_demo_data": True
    }
]
