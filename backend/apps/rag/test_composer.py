"""
Adversarial & Unit Test Suite for Grounded Evidence Composer & Citation Validator.
Validates:
1. Strict grounding: all material claims mapped to valid chunk IDs.
2. Adversarial phantom ID injection detection and remediation.
3. Adversarial invented financial threshold / percentage detection.
4. Zero-evidence fail-closed containment (INSUFFICIENT_EVIDENCE).
5. Statutory safety note and unresolved questions preservation.
"""
from django.test import TestCase
from apps.rag.composer import GroundedEvidenceComposer, ComposerContext
from apps.rag.citation_validator import CitationValidator


class GroundedEvidenceComposerTestCase(TestCase):
    def setUp(self):
        self.composer = GroundedEvidenceComposer()
        self.validator = CitationValidator()

        self.sample_evidence = [
            {
                'chunk_id': 'chunk-pmegp-001',
                'document_title': 'PMEGP Operational Guidelines 2024',
                'authority': 'Ministry of MSME / KVIC',
                'source_url': 'https://msme.gov.in/pmegp.pdf',
                'source_tier': 'tier_2_operational_guidelines',
                'page_number': 1,
                'section_heading': 'Clause 2.1: Quantum of Project Cost',
                'chunk_text': 'The maximum cost of the project/unit admissible under manufacturing sector is Rs. 50 Lakhs.'
            },
            {
                'chunk_id': 'chunk-pmegp-002',
                'document_title': 'PMEGP Operational Guidelines 2024',
                'authority': 'Ministry of MSME / KVIC',
                'source_url': 'https://msme.gov.in/pmegp.pdf',
                'source_tier': 'tier_2_operational_guidelines',
                'page_number': 2,
                'section_heading': 'Clause 4.2: Rate of Subsidy',
                'chunk_text': 'For General Category: 15% of project cost in Urban areas, 25% in Rural areas. Beneficiary contribution is 10%.'
            }
        ]

    def test_grounded_generation_valid(self):
        ctx = ComposerContext(
            user_question="What is the maximum manufacturing project limit and rural subsidy rate under PMEGP?",
            candidate_scheme_name="PMEGP",
            retrieved_evidence=self.sample_evidence
        )
        result = self.composer.compose(ctx)

        self.assertEqual(result['status'], 'GROUNDED')
        self.assertGreater(len(result['evidence_claims']), 0)
        self.assertGreater(len(result['citations']), 0)

        # Check all claims are grounded
        for claim in result['evidence_claims']:
            self.assertEqual(claim['verification_status'], 'grounded')

        # Check safety disclaimer
        self.assertIn("Statutory Disclaimer", result['safety_note'])

    def test_adversarial_phantom_chunk_id_detected(self):
        """
        Adversarial Test: Model outputs a claim referencing a non-existent chunk ID.
        Validator must catch the hallucinated ID, strip it, and downgrade status.
        """
        raw_output_with_phantom_id = {
            'answer': 'Manufacturing project limit is Rs. 50 Lakhs. Also, special export grant is Rs. 1 Crore.',
            'evidence_claims': [
                {
                    'claim_text': 'The maximum cost of the project admissible under manufacturing sector is Rs. 50 Lakhs.',
                    'evidence_chunk_ids': ['chunk-pmegp-001']
                },
                {
                    'claim_text': 'Special export grant of Rs. 1 Crore is available for overseas marketing.',
                    'evidence_chunk_ids': ['phantom-chunk-uuid-999']  # Fake ID!
                }
            ],
            'citations': [
                {
                    'chunk_id': 'chunk-pmegp-001',
                    'document_title': 'PMEGP Guidelines',
                    'exact_quote_snippet': 'The maximum cost of the project/unit admissible under manufacturing sector is Rs. 50 Lakhs.'
                },
                {
                    'chunk_id': 'phantom-chunk-uuid-999',  # Fake ID!
                    'document_title': 'Hallucinated Policy',
                    'exact_quote_snippet': 'Special export grant of Rs. 1 Crore.'
                }
            ],
            'unresolved_questions': [],
            'status': 'GROUNDED',
            'safety_note': 'Disclaimer'
        }

        validated = self.validator.validate_and_remediate(
            raw_output=raw_output_with_phantom_id,
            context_chunks=self.sample_evidence
        )

        # Invariants check
        self.assertEqual(validated['status'], 'PARTIAL_EVIDENCE')
        self.assertTrue(validated['validation_diagnostics']['hallucination_detected'])
        # Phantom citation stripped from citations list
        valid_ids = [c['chunk_id'] for c in validated['citations']]
        self.assertNotIn('phantom-chunk-uuid-999', valid_ids)
        # Phantom claim flagged as hallucinated_id
        statuses = [c['verification_status'] for c in validated['evidence_claims']]
        self.assertIn('hallucinated_id', statuses)

    def test_adversarial_invented_threshold_detected(self):
        """
        Adversarial Test: Model hallucinates a 95% subsidy percentage not in text.
        Validator must catch the numerical mismatch.
        """
        raw_output_with_fake_percentage = {
            'answer': 'You can get 95% subsidy under PMEGP.',
            'evidence_claims': [
                {
                    'claim_text': 'PMEGP offers a 95% subsidy for general category entrepreneurs.',
                    'evidence_chunk_ids': ['chunk-pmegp-002']
                }
            ],
            'citations': [
                {
                    'chunk_id': 'chunk-pmegp-002',
                    'document_title': 'PMEGP Guidelines',
                    'exact_quote_snippet': 'For General Category: 15% of project cost in Urban areas.'
                }
            ],
            'unresolved_questions': [],
            'status': 'GROUNDED',
            'safety_note': 'Disclaimer'
        }

        validated = self.validator.validate_and_remediate(
            raw_output=raw_output_with_fake_percentage,
            context_chunks=self.sample_evidence
        )

        self.assertEqual(validated['status'], 'REJECTED_UNGROUNDED')
        claim_stat = validated['evidence_claims'][0]['verification_status']
        self.assertEqual(claim_stat, 'unsubstantiated_numbers')
        self.assertIn("UNKNOWN / INSUFFICIENT OFFICIAL EVIDENCE", validated['answer'])

    def test_zero_evidence_fail_closed(self):
        """
        Adversarial Test: Prompt with zero evidence chunks must fail closed immediately.
        """
        ctx = ComposerContext(
            user_question="Is there a grant for buying residential real estate?",
            retrieved_evidence=[]  # Zero evidence
        )
        result = self.composer.compose(ctx)

        self.assertEqual(result['status'], 'INSUFFICIENT_EVIDENCE')
        self.assertEqual(len(result['citations']), 0)
        self.assertEqual(len(result['evidence_claims']), 0)
        self.assertIn("UNKNOWN / INSUFFICIENT OFFICIAL EVIDENCE", result['answer'])
        self.assertGreater(len(result['unresolved_questions']), 0)

    def test_deterministic_rule_unresolved_preservation(self):
        """
        Tests that when deterministic rule evaluation is UNKNOWN,
        the composer does not invent an approval and surfaces the missing fact.
        """
        ctx = ComposerContext(
            user_question="Am I eligible for PMEGP?",
            candidate_scheme_name="PMEGP",
            deterministic_rule_results=[
                {
                    'rule_name': 'Minimum Educational Qualification (Class VIII)',
                    'evaluation_status': 'REQUIRES_OFFICIAL_VERIFICATION',
                    'reason': 'Self-declared qualification requires marksheet verification.'
                }
            ],
            retrieved_evidence=self.sample_evidence
        )
        result = self.composer.compose(ctx)

        # Must not state formal approval; must list unresolved verification
        unresolved_text = " ".join(result['unresolved_questions'])
        self.assertIn("Class VIII", unresolved_text)
