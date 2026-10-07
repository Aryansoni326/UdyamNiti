"""
Unit & Integration Tests for Hybrid Policy Retrieval & Evaluation Harness.
Validates:
1. Dense vector + keyword lexical scoring with RRF.
2. Statutory Tier-1 Gazette precedence over Tier-4 FAQs.
3. Filtering by active policy versions (no superseded chunks).
4. Statutory terminology and exact scheme name boosting.
5. Fail-closed safety on weak/adversarial evidence.
6. Execution of 20-query golden evaluation harness.
"""
from datetime import date
from django.test import TestCase

from apps.rag.models import PolicySourceDocument, PolicyDocumentChunk
from apps.rag.retrieval import HybridPolicyRetriever, HybridQueryRequest
from apps.rag.evaluation_harness import RetrievalEvaluationHarness
from apps.policies.models import Scheme


class HybridPolicyRetrieverTestCase(TestCase):
    def setUp(self):
        self.retriever = HybridPolicyRetriever()
        self.scheme = Scheme.objects.create(
            name="Gujarat MSME Capital Subsidy",
            code="GJ-CAPITAL-2025",
            category="capital_subsidy"
        )

        # Tier 1 Gazette Document
        self.gazette_doc = PolicySourceDocument.objects.create(
            scheme=self.scheme,
            title="Gujarat Industrial Policy 2020-2025 Gazette Notification",
            authority="Industries and Mines Department",
            source_url="https://gujarat.gov.in/gazette-capital.pdf",
            source_tier="tier_1_gazette",
            effective_date=date(2020, 9, 1),
            version_number=1,
            status="published",
            file_hash="hash_tier1_gazette"
        )
        self.gazette_chunk = PolicyDocumentChunk.objects.create(
            document=self.gazette_doc,
            scheme=self.scheme,
            authority="Industries and Mines Department",
            source_url="https://gujarat.gov.in/gazette-capital.pdf",
            source_tier="tier_1_gazette",
            document_title=self.gazette_doc.title,
            publication_effective_date=date(2020, 9, 1),
            policy_version=1,
            page_number=2,
            section_heading="Clause 4.1: Category of Talukas and Quantum of Subsidy",
            chunk_index=1,
            chunk_text="Category-1 Talukas receive 25% of eligible Gross Fixed Capital Investment (GFCI) in plant & machinery, subject to ceiling of Rs. 35 Lakhs for Micro enterprises.",
            chunk_hash="chunk_hash_001",
            token_count=35,
            embedding=[0.05] * 384,
            is_active=True
        )

        # Tier 4 FAQ Document with similar wording
        self.faq_doc = PolicySourceDocument.objects.create(
            scheme=self.scheme,
            title="Investor Portal FAQ on MSME Capital Scheme",
            authority="IFP Helpdesk",
            source_url="https://ifp.gujarat.gov.in/faq.html",
            source_tier="tier_4_portal_faq",
            effective_date=date(2021, 1, 1),
            version_number=1,
            status="published",
            file_hash="hash_tier4_faq"
        )
        self.faq_chunk = PolicyDocumentChunk.objects.create(
            document=self.faq_doc,
            scheme=self.scheme,
            authority="IFP Helpdesk",
            source_url="https://ifp.gujarat.gov.in/faq.html",
            source_tier="tier_4_portal_faq",
            document_title=self.faq_doc.title,
            publication_effective_date=date(2021, 1, 1),
            policy_version=1,
            page_number=1,
            section_heading="Q4: What is the subsidy in Category 1 taluka?",
            chunk_index=1,
            chunk_text="In Category-1 Talukas, micro units can get 25% subsidy on GFCI up to Rs. 35 Lakhs as per guidelines.",
            chunk_hash="chunk_hash_002",
            token_count=30,
            embedding=[0.05] * 384,
            is_active=True
        )

        # Inactive/Superseded Chunk (Should NEVER be retrieved)
        self.inactive_chunk = PolicyDocumentChunk.objects.create(
            document=self.gazette_doc,
            scheme=self.scheme,
            authority="Industries and Mines Department",
            source_url="https://gujarat.gov.in/gazette-capital.pdf",
            source_tier="tier_1_gazette",
            document_title=self.gazette_doc.title,
            publication_effective_date=date(2015, 1, 1),
            policy_version=1,
            page_number=1,
            section_heading="Old Inactive Clause",
            chunk_index=99,
            chunk_text="Old policy expired: Gross Fixed Capital Investment ceiling is Rs. 10 Lakhs.",
            chunk_hash="chunk_hash_old",
            token_count=15,
            embedding=[0.05] * 384,
            is_active=False
        )

    def test_tier_1_gazette_precedence(self):
        """
        Requirements: Prefer Tier 1 official evidence.
        Given identical lexical match, the Tier 1 Gazette chunk must score higher
        and rank above the Tier 4 FAQ chunk.
        """
        req = HybridQueryRequest(
            user_question="What is the subsidy for micro units on Gross Fixed Capital Investment in Category-1 Talukas?",
            candidate_scheme_ids=["GJ-CAPITAL-2025"],
            top_k=5
        )
        response = self.retriever.retrieve(req)

        self.assertGreaterEqual(len(response.citations), 2)
        top_citation = response.citations[0]
        # Top citation must be the Tier 1 Gazette
        self.assertEqual(top_citation.source_tier, "tier_1_gazette")
        self.assertEqual(top_citation.chunk_id, str(self.gazette_chunk.id))
        self.assertGreater(top_citation.internal_diagnostic_score, response.citations[1].internal_diagnostic_score)

    def test_filter_by_active_policy_version(self):
        """
        Requirements: Filter by current/effective policy version.
        Inactive or superseded chunks must NEVER be retrieved.
        """
        req = HybridQueryRequest(
            user_question="Gross Fixed Capital Investment ceiling",
            top_k=10
        )
        response = self.retriever.retrieve(req)
        retrieved_ids = [c.chunk_id for c in response.citations]
        self.assertNotIn(str(self.inactive_chunk.id), retrieved_ids)

    def test_fail_closed_on_weak_or_adversarial_queries(self):
        """
        Requirements: Fail closed when evidence is weak.
        An off-topic or adversarial query must return 'insufficient_evidence'
        with 0 hallucinated citations.
        """
        req = HybridQueryRequest(
            user_question="Can I get Canadian immigration tax refund for mining Dogecoin in Toronto?",
            min_score_threshold=0.35,
            top_k=5
        )
        response = self.retriever.retrieve(req)

        self.assertEqual(response.retrieval_status, "insufficient_evidence")
        self.assertEqual(len(response.citations), 0)
        self.assertIn("below fail-closed threshold", response.diagnostic_summary['reason'])

    def test_citation_ready_metadata_and_diagnostics(self):
        """
        Requirements: Return citation-ready metadata and internal diagnostic score.
        Diagnostic score must never be presented as statutory eligibility confidence.
        """
        req = HybridQueryRequest(
            user_question="Gujarat Category-1 Talukas GFCI subsidy",
            top_k=1
        )
        response = self.retriever.retrieve(req)
        self.assertEqual(len(response.citations), 1)

        c = response.citations[0]
        self.assertEqual(c.page_number, 2)
        self.assertEqual(c.section_heading, "Clause 4.1: Category of Talukas and Quantum of Subsidy")
        self.assertEqual(c.authority, "Industries and Mines Department")
        self.assertIsNotNone(c.internal_diagnostic_score)
        self.assertEqual(c.retrieval_method, "hybrid_rrf_tier_boosted")
        self.assertIn("gfci", [t.lower() for t in c.matched_terms])

    def test_evaluation_harness_integration(self):
        """
        Validates the 20 golden queries evaluation harness runs end-to-end
        and computes all required IR metrics.
        """
        harness = RetrievalEvaluationHarness()
        eval_result = harness.run_evaluation(top_k=5)

        self.assertEqual(eval_result['total_golden_queries'], 20)
        self.assertEqual(eval_result['out_of_domain_queries'], 2)

        metrics = eval_result['metrics']
        self.assertIn('mrr', metrics)
        self.assertIn('recall_at_1', metrics)
        self.assertIn('recall_at_3', metrics)
        self.assertIn('recall_at_5', metrics)
        self.assertIn('tier1_gazette_ratio_percent', metrics)
        self.assertIn('fail_closed_safety_rate_percent', metrics)
        # Out-of-domain queries should achieve 100% fail-closed safety rate
        self.assertEqual(metrics['fail_closed_safety_rate_percent'], 100.0)
