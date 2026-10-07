"""
Evaluation Harness for Hybrid Government Policy Retrieval.
Contains 20 curated statutory golden queries spanning Central and Gujarat MSME schemes.
Measures Recall@K, Precision@K, MRR, Tier-1 Preference Ratio, and Fail-Closed Safety.
"""
from dataclasses import dataclass
from typing import List, Dict, Any
from apps.rag.retrieval import HybridPolicyRetriever, HybridQueryRequest


@dataclass
class GoldenQuery:
    query_id: str
    user_question: str
    business_goal: str
    expected_scheme_codes: List[str]
    expected_clause_keywords: List[str]
    expected_tier: str
    is_out_of_domain: bool = False


GOLDEN_QUERIES: List[GoldenQuery] = [
    GoldenQuery(
        query_id="GQ-01",
        user_question="What is the maximum admissible project cost for a new manufacturing unit under PMEGP?",
        business_goal="Set up a new precision machining micro unit",
        expected_scheme_codes=["PMEGP-CENTRAL"],
        expected_clause_keywords=["Clause 2.1", "50 Lakhs", "manufacturing"],
        expected_tier="tier_2_operational_guidelines"
    ),
    GoldenQuery(
        query_id="GQ-02",
        user_question="Can I get Gujarat capital investment subsidy on refurbished or second-hand imported CNC machinery?",
        business_goal="Import used machinery from Germany to save capex",
        expected_scheme_codes=["GJ-CAPITAL-2025"],
        expected_clause_keywords=["Clause 5.2", "second-hand", "ineligible", "refurbished"],
        expected_tier="tier_1_gazette"
    ),
    GoldenQuery(
        query_id="GQ-03",
        user_question="What is the collateral-free guarantee coverage percentage under CGTMSE for women-owned enterprises?",
        business_goal="Obtain collateral-free bank loan for working capital",
        expected_scheme_codes=["CGTMSE-CENTRAL"],
        expected_clause_keywords=["85%", "Clause 3.2", "women entrepreneurs", "500 Lakhs"],
        expected_tier="tier_2_operational_guidelines"
    ),
    GoldenQuery(
        query_id="GQ-04",
        user_question="What is the rate and duration of interest subsidy in Category 1 talukas under Gujarat MSME Policy?",
        business_goal="Reduce interest burden on factory term loan",
        expected_scheme_codes=["GJ-INTEREST-2025"],
        expected_clause_keywords=["Clause 2.1", "7%", "Category 1", "7 years", "35 Lakhs"],
        expected_tier="tier_1_gazette"
    ),
    GoldenQuery(
        query_id="GQ-05",
        user_question="What is the financial subsidy on ZED certification fees for a micro manufacturing enterprise?",
        business_goal="Obtain environmental and quality benchmark for global exports",
        expected_scheme_codes=["MSME-ZED-CENTRAL"],
        expected_clause_keywords=["80%", "Clause 3.1", "Micro Enterprises", "Bronze"],
        expected_tier="tier_2_operational_guidelines"
    ),
    GoldenQuery(
        query_id="GQ-06",
        user_question="What is the enhanced loan limit under PM Mudra Tarun Plus announced in the latest Union Budget?",
        business_goal="Expand retail inventory and commercial vehicles",
        expected_scheme_codes=["PM-MUDRA-CENTRAL"],
        expected_clause_keywords=["Tarun Plus", "20,00,000", "20 Lakhs", "Clause 2"],
        expected_tier="tier_2_operational_guidelines"
    ),
    GoldenQuery(
        query_id="GQ-07",
        user_question="For how many years is electricity duty exempted for new MSME manufacturing units in Gujarat?",
        business_goal="Lower industrial operating power costs",
        expected_scheme_codes=["GJ-POWER-TARIFF-2025"],
        expected_clause_keywords=["100% exemption", "5 years", "Clause 1", "Electricity Duty"],
        expected_tier="tier_1_gazette"
    ),
    GoldenQuery(
        query_id="GQ-08",
        user_question="Which business activities are strictly prohibited under the negative list of PMEGP?",
        business_goal="Open a meat processing and retail shop",
        expected_scheme_codes=["PMEGP-CENTRAL"],
        expected_clause_keywords=["Clause 5.1", "Negative List", "intoxicant", "polythene"],
        expected_tier="tier_2_operational_guidelines"
    ),
    GoldenQuery(
        query_id="GQ-09",
        user_question="What is the financial ceiling for international patent filing assistance in Gujarat?",
        business_goal="Protect innovative engineering design in US and Europe",
        expected_scheme_codes=["GJ-PATENT-2025"],
        expected_clause_keywords=["50 Lakhs", "75%", "Clause 2.1", "international patent"],
        expected_tier="tier_2_operational_guidelines"
    ),
    GoldenQuery(
        query_id="GQ-10",
        user_question="What interest subvention and concessional interest rate is provided under PM Vishwakarma collateral-free loans?",
        business_goal="Upgrade artisan carpentry workshop with modern power tools",
        expected_scheme_codes=["PM-VISHWAKARMA-CENTRAL"],
        expected_clause_keywords=["5%", "8% interest subvention", "Clause 3", "1,00,000"],
        expected_tier="tier_1_gazette"
    ),
    GoldenQuery(
        query_id="GQ-11",
        user_question="What is the financial grant ceiling for Common Facility Centers under the MSE-CDP scheme?",
        business_goal="Build a shared tooling and testing lab for our brass cluster",
        expected_scheme_codes=["MSE-CDP-CENTRAL"],
        expected_clause_keywords=["70%", "30 Crores", "Common Facility", "Clause 2"],
        expected_tier="tier_2_operational_guidelines"
    ),
    GoldenQuery(
        query_id="GQ-12",
        user_question="What percentage of capital subsidy is provided for industrial Effluent Treatment Plants (ETP) in Gujarat?",
        business_goal="Install zero liquid discharge wastewater plant to meet GPCB norms",
        expected_scheme_codes=["GJ-CETP-ENV-2025"],
        expected_clause_keywords=["50%", "50 Lakhs", "Clause 1", "Effluent Treatment"],
        expected_tier="tier_1_gazette"
    ),
    GoldenQuery(
        query_id="GQ-13",
        user_question="What is the margin money subsidy rate for special category beneficiaries under rural PMEGP?",
        business_goal="Start an agro-processing unit in a rural village",
        expected_scheme_codes=["PMEGP-CENTRAL"],
        expected_clause_keywords=["35%", "Rural", "Special Categories", "Clause 4.2", "5%"],
        expected_tier="tier_2_operational_guidelines"
    ),
    GoldenQuery(
        query_id="GQ-14",
        user_question="Does Gujarat offer 100% reimbursement for aerospace AS9100 quality certifications?",
        business_goal="Become a tier-1 supplier for ISRO and defense aviation components",
        expected_scheme_codes=["GJ-DEFENSE-AERO-2025"],
        expected_clause_keywords=["AS9100", "100%", "25 Lakhs", "Clause 2"],
        expected_tier="tier_1_gazette"
    ),
    GoldenQuery(
        query_id="GQ-15",
        user_question="What is the one-time grant amount for government agencies to set up Livelihood Business Incubators under ASPIRE?",
        business_goal="Establish rural incubation center for honey and agro processing",
        expected_scheme_codes=["ASPIRE-CENTRAL"],
        expected_clause_keywords=["100 Lakhs", "100% grant", "LBI", "Clause 2"],
        expected_tier="tier_2_operational_guidelines"
    ),
    GoldenQuery(
        query_id="GQ-16",
        user_question="What is the Annual Guarantee Fee (AGF) floor rate under CGTMSE for micro units in tier-2/3 centres?",
        business_goal="Negotiate bank credit guarantee charges",
        expected_scheme_codes=["CGTMSE-CENTRAL"],
        expected_clause_keywords=["0.37%", "Annual Guarantee Fee", "Clause 4.1", "AGF"],
        expected_tier="tier_2_operational_guidelines"
    ),
    GoldenQuery(
        query_id="GQ-17",
        user_question="How does TReDS protect micro and small suppliers from delayed corporate payments?",
        business_goal="Discount pending invoices from corporate buyers without recourse",
        expected_scheme_codes=["TREDS-CENTRAL"],
        expected_clause_keywords=["without recourse", "Clause 3", "250 Crores", "Factoring"],
        expected_tier="tier_1_gazette"
    ),
    GoldenQuery(
        query_id="GQ-18",
        user_question="What is the subsidy percentage on energy and water audit fees for Gujarat MSMEs?",
        business_goal="Conduct comprehensive electrical energy audit for boiler plant",
        expected_scheme_codes=["GJ-ENERGY-CONSERV-2025"],
        expected_clause_keywords=["75%", "50,000", "Clause 1", "Energy & Water Audit"],
        expected_tier="tier_2_operational_guidelines"
    ),
    # Adversarial / Out-of-Domain queries to validate Fail-Closed safety
    GoldenQuery(
        query_id="GQ-19-OOD",
        user_question="What is the subsidy for purchasing cryptocurrency mining rigs in Gujarat?",
        business_goal="Mine Bitcoin in factory basement",
        expected_scheme_codes=[],
        expected_clause_keywords=[],
        expected_tier="",
        is_out_of_domain=True
    ),
    GoldenQuery(
        query_id="GQ-20-OOD",
        user_question="How to claim Canadian government agricultural immigration grant from Ahmedabad?",
        business_goal="Relocate to Ontario under Canadian farm subsidy",
        expected_scheme_codes=[],
        expected_clause_keywords=[],
        expected_tier="",
        is_out_of_domain=True
    ),
]


class RetrievalEvaluationHarness:
    """
    Executes standard information retrieval metrics against the golden dataset:
    - Mean Reciprocal Rank (MRR)
    - Recall@1, Recall@3, Recall@5
    - Precision@1, Precision@5
    - Tier-1 Gazette Preference Ratio
    - Fail-Closed Safety Accuracy
    """

    def __init__(self):
        self.retriever = HybridPolicyRetriever()

    def run_evaluation(self, top_k: int = 5) -> Dict[str, Any]:
        results = []
        reciprocal_ranks = []
        recall_at_1 = []
        recall_at_3 = []
        recall_at_5 = []
        precision_at_1 = []
        precision_at_5 = []
        tier1_counts = 0
        total_retrieved = 0
        fail_closed_successes = 0
        total_ood = 0

        for gq in GOLDEN_QUERIES:
            req = HybridQueryRequest(
                user_question=gq.user_question,
                business_goal=gq.business_goal,
                top_k=top_k
            )
            response = self.retriever.retrieve(req)

            if gq.is_out_of_domain:
                total_ood += 1
                # Must fail closed: either 'insufficient_evidence' or 0 citations
                if response.retrieval_status == 'insufficient_evidence' or len(response.citations) == 0:
                    fail_closed_successes += 1
                results.append({
                    'query_id': gq.query_id,
                    'type': 'out_of_domain',
                    'status': response.retrieval_status,
                    'passed_fail_closed': response.retrieval_status == 'insufficient_evidence'
                })
                continue

            # Standard query evaluation
            retrieved_chunks = response.citations
            hit_rank = 0
            has_relevant = False

            # Check if any retrieved chunk satisfies expected keywords
            for idx, c in enumerate(retrieved_chunks, start=1):
                chunk_haystack = (c.chunk_text + " " + c.section_heading + " " + c.document_title).lower()
                # Check keyword matches
                matches = [kw for kw in gq.expected_clause_keywords if kw.lower() in chunk_haystack]
                if matches and hit_rank == 0:
                    hit_rank = idx
                    has_relevant = True

                if c.source_tier == 'tier_1_gazette':
                    tier1_counts += 1
                total_retrieved += 1

            # Compute ranks
            rr = (1.0 / hit_rank) if hit_rank > 0 else 0.0
            reciprocal_ranks.append(rr)

            r1 = 1.0 if (hit_rank == 1) else 0.0
            r3 = 1.0 if (1 <= hit_rank <= 3) else 0.0
            r5 = 1.0 if (1 <= hit_rank <= 5) else 0.0

            recall_at_1.append(r1)
            recall_at_3.append(r3)
            recall_at_5.append(r5)

            p1 = 1.0 if (hit_rank == 1) else 0.0
            p5 = (1.0 / 5.0) if has_relevant else 0.0
            precision_at_1.append(p1)
            precision_at_5.append(p5)

            results.append({
                'query_id': gq.query_id,
                'hit_rank': hit_rank,
                'reciprocal_rank': round(rr, 3),
                'top_source_tier': retrieved_chunks[0].source_tier if retrieved_chunks else 'none',
                'retrieval_status': response.retrieval_status,
                'citations_count': len(retrieved_chunks)
            })

        mrr = round(sum(reciprocal_ranks) / max(1, len(reciprocal_ranks)), 4)
        r_at_1 = round(sum(recall_at_1) / max(1, len(recall_at_1)), 4)
        r_at_3 = round(sum(recall_at_3) / max(1, len(recall_at_3)), 4)
        r_at_5 = round(sum(recall_at_5) / max(1, len(recall_at_5)), 4)
        p_at_1 = round(sum(precision_at_1) / max(1, len(precision_at_1)), 4)
        tier1_ratio = round((tier1_counts / max(1, total_retrieved)) * 100, 2)
        fail_closed_rate = round((fail_closed_successes / max(1, total_ood)) * 100, 2)

        summary = {
            'total_golden_queries': len(GOLDEN_QUERIES),
            'in_domain_queries': len(GOLDEN_QUERIES) - total_ood,
            'out_of_domain_queries': total_ood,
            'metrics': {
                'mrr': mrr,
                'recall_at_1': r_at_1,
                'recall_at_3': r_at_3,
                'recall_at_5': r_at_5,
                'precision_at_1': p_at_1,
                'tier1_gazette_ratio_percent': tier1_ratio,
                'fail_closed_safety_rate_percent': fail_closed_rate
            },
            'query_results': results
        }
        return summary
