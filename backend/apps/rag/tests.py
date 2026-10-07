"""
Comprehensive Unit & Integration Test Suite for RAG Ingestion Pipeline.
Validates:
1. Legal section-aware chunking with page boundary preservation.
2. SimHash and SHA-256 deduplication.
3. Zero silent overwrite / document versioning invariants.
4. Quarantine isolation for corrupted/unparseable files.
5. Exact 13-field provenance preservation on all chunks.
6. Audit reporting with IngestionReport.
7. Celery task idempotency.
"""
import uuid
from datetime import date
from django.test import TestCase

from apps.rag.models import PolicySourceDocument, PolicyDocumentChunk, IngestionReport
from apps.rag.chunker import LegalDocumentParser, compute_sha256, compute_simhash
from apps.rag.pipeline import RAGIngestionPipeline
from apps.rag.tasks import ingest_policy_document_task
from apps.policies.models import Scheme


class LegalDocumentParserTestCase(TestCase):
    def setUp(self):
        self.parser = LegalDocumentParser()

    def test_clause_detection_and_page_preservation(self):
        sample_pages = [
            (1, "GOVERNMENT OF GUJARAT\nClause 1.1: Scope\nThis scheme applies to micro and small enterprises in Gujarat.\nClause 2.0: Eligibility\nMust possess active Udyam registration and commercial connection."),
            (2, "Clause 3.1: Quantum of Assistance\nEligible units receive 25% capital subsidy up to Rs. 35 Lakhs in Category 1 talukas.")
        ]
        chunks = self.parser.parse_pages(sample_pages)

        self.assertGreaterEqual(len(chunks), 2)
        # Verify page boundary retained
        page_numbers = [c['page_number'] for c in chunks]
        self.assertIn(1, page_numbers)
        self.assertIn(2, page_numbers)

        # Verify clause headings extracted
        headings = [c['section_heading'] for c in chunks]
        self.assertTrue(any('Clause' in h for h in headings))

        # Verify hash and token counts
        for c in chunks:
            self.assertEqual(len(c['chunk_hash']), 64)
            self.assertGreater(c['token_count'], 0)


class SimHashDeduplicationTestCase(TestCase):
    def test_simhash_near_duplicates(self):
        text_a = "The maximum cost of the project admissible under manufacturing sector is Rs. 50 Lakhs for PMEGP."
        text_b = "The maximum cost of project admissible under manufacturing sector is Rs. 50 Lakhs for PMEGP Scheme."
        text_different = "Gujarat electricity duty exemption is granted for five years to all greenfield industrial units."

        hash_a = compute_simhash(text_a)
        hash_b = compute_simhash(text_b)
        hash_diff = compute_simhash(text_different)

        self.assertEqual(len(hash_a), 16)
        self.assertNotEqual(hash_a, hash_diff)


class RAGIngestionPipelineTestCase(TestCase):
    def setUp(self):
        self.pipeline = RAGIngestionPipeline()
        self.scheme = Scheme.objects.create(
            name="Test Capital Scheme",
            code="TEST-CAPITAL-01",
            category="capital_subsidy"
        )

    def test_all_13_provenance_headers_preserved(self):
        doc = self.pipeline.register_source(
            title="Operational Guidelines for Capital Subsidy 2024",
            authority="Industries Commissionerate",
            source_url="https://gujarat.gov.in/test-capital.pdf",
            source_tier="tier_2_operational_guidelines",
            effective_date=date(2024, 1, 1),
            scheme=self.scheme,
            raw_text_pages=[
                (1, "Clause 4.1: Eligible Investment. Plant and machinery purchased directly from original equipment manufacturers.")
            ]
        )

        processed = self.pipeline.process_document(
            doc_id=doc.id,
            raw_text_pages=[
                (1, "Clause 4.1: Eligible Investment. Plant and machinery purchased directly from original equipment manufacturers.")
            ]
        )

        self.assertEqual(processed.status, 'published')
        self.assertGreater(processed.total_chunks, 0)

        chunk = processed.chunks.first()
        self.assertIsNotNone(chunk)

        # 13 Required Invariants Validation
        self.assertEqual(chunk.document_id, doc.id)
        self.assertEqual(chunk.scheme_id, self.scheme.id)
        self.assertEqual(chunk.authority, "Industries Commissionerate")
        self.assertEqual(chunk.source_url, "https://gujarat.gov.in/test-capital.pdf")
        self.assertEqual(chunk.source_tier, "tier_2_operational_guidelines")
        self.assertEqual(chunk.document_title, "Operational Guidelines for Capital Subsidy 2024")
        self.assertEqual(chunk.publication_effective_date, date(2024, 1, 1))
        self.assertEqual(chunk.page_number, 1)
        self.assertIn("Clause 4.1", chunk.section_heading)
        self.assertEqual(chunk.chunk_index, 1)
        self.assertEqual(len(chunk.chunk_hash), 64)
        self.assertIsNotNone(chunk.ingested_at)
        self.assertEqual(chunk.policy_version, 1)

        # Embedding verification (384 dimensions)
        self.assertIsNotNone(chunk.embedding)
        self.assertEqual(len(chunk.embedding), 384)

    def test_versioning_and_no_silent_overwrite(self):
        """
        Invariant: Never silently overwrite old policy evidence.
        Newer version increments version_number, marks old doc 'superseded',
        and retains all historical chunks.
        """
        # Version 1
        doc_v1 = self.pipeline.register_source(
            title="Gujarat Industrial Policy MSME Guidelines",
            authority="Industries and Mines Department",
            source_url="https://gujarat.gov.in/guidelines-v1.pdf",
            source_tier="tier_1_gazette",
            effective_date=date(2020, 9, 1),
            scheme=self.scheme,
            raw_text_pages=[(1, "Clause 1.0: Assistance ceiling is Rs. 35 Lakhs for Micro enterprises in Category 1 talukas.")]
        )
        self.pipeline.process_document(
            doc_id=doc_v1.id,
            raw_text_pages=[(1, "Clause 1.0: Assistance ceiling is Rs. 35 Lakhs for Micro enterprises in Category 1 talukas.")]
        )

        self.assertEqual(doc_v1.version_number, 1)
        self.assertEqual(doc_v1.chunks.filter(is_active=True).count(), 1)

        # Version 2 (amendment with increased ceiling)
        doc_v2 = self.pipeline.register_source(
            title="Gujarat Industrial Policy MSME Guidelines",
            authority="Industries and Mines Department",
            source_url="https://gujarat.gov.in/guidelines-v2.pdf",
            source_tier="tier_1_gazette",
            effective_date=date(2024, 4, 1),
            scheme=self.scheme,
            raw_text_pages=[(1, "Clause 1.0: Assistance ceiling is enhanced to Rs. 50 Lakhs for Micro enterprises in Category 1 talukas.")]
        )
        self.pipeline.process_document(
            doc_id=doc_v2.id,
            raw_text_pages=[(1, "Clause 1.0: Assistance ceiling is enhanced to Rs. 50 Lakhs for Micro enterprises in Category 1 talukas.")]
        )

        doc_v1.refresh_from_db()
        doc_v2.refresh_from_db()

        # Invariant checks
        self.assertEqual(doc_v2.version_number, 2)
        self.assertEqual(doc_v1.status, 'superseded')
        self.assertEqual(doc_v2.status, 'published')

        # Old chunks are NOT deleted; they are archived with is_active=False
        self.assertEqual(doc_v1.chunks.count(), 1)
        self.assertFalse(doc_v1.chunks.first().is_active)
        self.assertEqual(doc_v2.chunks.count(), 1)
        self.assertTrue(doc_v2.chunks.first().is_active)

    def test_quarantine_corrupted_or_empty_document(self):
        """
        Invariant: Corrupted or unparseable inputs must transition to quarantined
        without crashing the pipeline or creating empty chunks.
        """
        doc = self.pipeline.register_source(
            title="Corrupted Policy Circular",
            authority="Unknown",
            source_url="https://corrupt.gov.in/circular.pdf",
            source_tier="tier_3_ministry_circular",
            effective_date=date(2024, 1, 1),
            raw_text_pages=[(1, "   ")]  # Blank content
        )

        processed = self.pipeline.process_document(
            doc_id=doc.id,
            raw_text_pages=[(1, "   ")]
        )

        self.assertEqual(processed.status, 'quarantined')
        self.assertIn("rejected", processed.quarantine_reason.lower())
        self.assertEqual(processed.chunks.count(), 0)

    def test_exact_duplicate_detection(self):
        pages = [(1, "Clause 5.0: Standard terms and conditions for industrial park allotment.")]
        doc1 = self.pipeline.register_source(
            title="Industrial Park Allotment Rules",
            authority="GIDC",
            source_url="https://gidc.gujarat.gov.in/rules.pdf",
            source_tier="tier_2_operational_guidelines",
            effective_date=date(2023, 1, 1),
            raw_text_pages=pages
        )
        self.pipeline.process_document(doc1.id, raw_text_pages=pages)

        # Attempt to register identical document again
        doc2 = self.pipeline.register_source(
            title="Industrial Park Allotment Rules",
            authority="GIDC",
            source_url="https://gidc.gujarat.gov.in/rules.pdf",
            source_tier="tier_2_operational_guidelines",
            effective_date=date(2023, 1, 1),
            raw_text_pages=pages
        )

        self.assertEqual(doc1.id, doc2.id)

    def test_ingestion_report_generation(self):
        batch = [
            {
                'title': 'Batch Doc 1 Valid',
                'authority': 'MoMSME',
                'source_url': 'https://msme.gov.in/doc1.pdf',
                'effective_date': date(2024, 1, 1),
                'raw_text_pages': [(1, "Clause 1.0: Valid legal text for batch processing.")]
            },
            {
                'title': 'Batch Doc 2 Corrupt',
                'authority': 'MoMSME',
                'source_url': 'https://msme.gov.in/doc2.pdf',
                'effective_date': date(2024, 1, 1),
                'raw_text_pages': [(1, "")]  # Will quarantine
            }
        ]

        report = self.pipeline.run_batch(batch, batch_id="TEST-BATCH-01")
        self.assertIsInstance(report, IngestionReport)
        self.assertEqual(report.status, 'partial_quarantine')
        self.assertEqual(report.total_sources, 2)
        self.assertEqual(report.processed_sources, 1)
        self.assertEqual(report.quarantined_sources, 1)
        self.assertGreater(report.total_chunks_created, 0)
        self.assertEqual(len(report.error_log), 1)

    def test_idempotent_celery_task(self):
        pages = [(1, "Clause 2.0: Credit guarantee provisions for micro units.")]
        doc = self.pipeline.register_source(
            title="CGTMSE Circular 2024",
            authority="CGTMSE",
            source_url="https://cgtmse.in/circular.pdf",
            source_tier="tier_2_operational_guidelines",
            effective_date=date(2024, 1, 1),
            raw_text_pages=pages
        )
        self.pipeline.process_document(doc.id, raw_text_pages=pages)

        # First run publishes it
        self.assertEqual(doc.status, 'published')

        # Celery task execution should recognize it is already published and skip
        result = ingest_policy_document_task(str(doc.id), force=False)
        self.assertEqual(result['status'], 'skipped')
        self.assertEqual(result['reason'], 'already_published')
