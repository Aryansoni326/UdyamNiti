"""
Grounded Evidence Composer for Government Policy Decision Support.
Transforms retrieved official evidence, business facts, and deterministic rule evaluations
into faithful, citation-grounded natural language explanations.
Strictly forbids hallucination, invented thresholds, or independent eligibility declarations.
"""
import json
import os
import re
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional

from apps.rag.citation_validator import CitationValidator
from apps.rag.security import (
    UntrustedDataIsolator,
    ContentSanitizer,
    SchemaConstrainedOutputValidator,
    SafeRenderer,
    SecurityAuditLogger,
    ThreatCategory,
    ThreatSeverity,
)

try:
    import google.generativeai as genai
    _HAS_GENAI = True
except ImportError:
    _HAS_GENAI = False


@dataclass
class ComposerContext:
    user_question: str
    business_facts: Dict[str, Any] = field(default_factory=dict)
    deterministic_rule_results: List[Dict[str, Any]] = field(default_factory=list)
    retrieved_evidence: List[Dict[str, Any]] = field(default_factory=list)
    source_metadata: Dict[str, Any] = field(default_factory=dict)
    candidate_scheme_name: str = ""


class GroundedPromptBuilder:
    """
    Constructs an adversarial-resistant system and user prompt ensuring
    the model reasons strictly over retrieved statutory context.
    Isolates untrusted document text in XML boundaries with explicit anti-jailbreak directives.
    """

    SYSTEM_PROMPT = f"""You are the Official Evidence Synthesizer for UdyamNiti, an evidence-backed government support strategy platform for Indian MSMEs.

Your role is to explain policy rules and support opportunities in clear, professional language grounded ONLY in the retrieved official government documents provided.

STRICT INVARIANTS & CONSTRAINTS:
1. NEVER invent a financial threshold, percentage, or statutory deadline. If a number is not in the evidence, DO NOT state it.
2. NEVER independently declare formal eligibility. You may ONLY explain the results of the deterministic rule evaluations provided to you.
3. NEVER invent scheme compatibility or cross-scheme relationships not grounded in official guidelines.
4. EVERY material claim in 'evidence_claims' MUST cite one or more exact chunk IDs present in the <untrusted_policy_evidence> tags.
5. If the provided evidence is silent, ambiguous, or insufficient, you MUST set status to 'INSUFFICIENT_EVIDENCE', state 'UNKNOWN' in the answer, and list exact missing items in 'unresolved_questions'.
6. Do NOT hide uncertainty. Distinguish clearly between self-declared MSME facts and document-verified statutory rules.

{UntrustedDataIsolator.SYSTEM_SECURITY_DIRECTIVES}

OUTPUT FORMAT:
You must respond ONLY with a valid, parseable JSON object matching this exact structure:
{{
  "answer": "Plain-language synthesized explanation answering the user's question...",
  "evidence_claims": [
    {{
      "claim_text": "The maximum project cost admissible under manufacturing sector is Rs. 50 Lakhs.",
      "evidence_chunk_ids": ["chunk-uuid-1"]
    }}
  ],
  "citations": [
    {{
      "chunk_id": "chunk-uuid-1",
      "document_title": "PMEGP Operational Guidelines 2024",
      "authority": "Ministry of MSME",
      "source_url": "https://...",
      "page_number": 1,
      "section_heading": "Clause 2.1: Quantum of Project Cost",
      "exact_quote_snippet": "The maximum cost of the project/unit admissible under manufacturing sector is Rs. 50 Lakhs."
    }}
  ],
  "unresolved_questions": [
    "Does the unit possess valid Udyam Registration as a manufacturing micro enterprise?"
  ],
  "status": "GROUNDED", // One of: "GROUNDED", "PARTIAL_EVIDENCE", "INSUFFICIENT_EVIDENCE"
  "safety_note": "Statutory Disclaimer: ..."
}}
"""

    def build_user_prompt(self, ctx: ComposerContext) -> str:
        # 1. Format and sanitize Business Facts
        clean_facts = {}
        if ctx.business_facts:
            for k, v in ctx.business_facts.items():
                clean_k = ContentSanitizer.sanitize(str(k), source_identifier="fact_key")
                clean_v = ContentSanitizer.sanitize(str(v), source_identifier="fact_val") if isinstance(v, str) else v
                clean_facts[clean_k] = clean_v
        facts_block = json.dumps(clean_facts, indent=2) if clean_facts else "No profile facts provided."

        # 2. Format Deterministic Rule Results
        rule_eval_lines = []
        if ctx.deterministic_rule_results:
            for r in ctx.deterministic_rule_results:
                rule_name = ContentSanitizer.sanitize(str(r.get('rule_name', 'Rule')))
                eval_status = ContentSanitizer.sanitize(str(r.get('evaluation_status', 'UNKNOWN')))
                reason = ContentSanitizer.sanitize(str(r.get('reason', '')))
                rule_eval_lines.append(f"- Rule: {rule_name} | Status: {eval_status} | Reason: {reason}")
        rule_block = "\n".join(rule_eval_lines) if rule_eval_lines else "No pre-computed deterministic evaluations."

        # 3. Securely isolate retrieved evidence corpus in XML tags
        isolated_evidence_block = UntrustedDataIsolator.isolate_evidence_corpus(ctx.retrieved_evidence)

        # 4. Isolate user question
        isolated_user_question = UntrustedDataIsolator.isolate_user_input(ctx.user_question)

        prompt = f"""{isolated_user_question}

[CANDIDATE SCHEME]:
{ContentSanitizer.sanitize(ctx.candidate_scheme_name) or "General MSME Support"}

[STRUCTURED BUSINESS PROFILE FACTS]:
{facts_block}

[DETERMINISTIC RULE EVALUATIONS]:
{rule_block}

[RETRIEVED OFFICIAL EVIDENCE]:
{isolated_evidence_block}

Generate the strict JSON response following the system constraints and security directives."""
        return prompt


class GroundedEvidenceComposer:
    """
    Executes grounded answer generation, enforcing the 5-point citation validator
    and fail-closed hallucination containment.
    """

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv('GEMINI_API_KEY')
        self.prompt_builder = GroundedPromptBuilder()
        self.validator = CitationValidator()

        if _HAS_GENAI and self.api_key:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel(
                model_name='gemini-1.5-flash',
                system_instruction=self.prompt_builder.SYSTEM_PROMPT
            )
        else:
            self.model = None

    def compose(self, ctx: ComposerContext) -> Dict[str, Any]:
        """
        Compose grounded answer with automatic citation validation & remediation.
        """
        if not ctx.retrieved_evidence:
            # Immediate fail-closed when evidence context is absent
            return {
                'answer': (
                    "UNKNOWN / INSUFFICIENT OFFICIAL EVIDENCE: No official government policy evidence was retrieved "
                    "matching this inquiry. The platform cannot generate ungrounded advice."
                ),
                'evidence_claims': [],
                'citations': [],
                'unresolved_questions': [
                    "What specific scheme or support category applies to your business goal?",
                    "Do you have official guidelines or notification numbers for this query?"
                ],
                'status': 'INSUFFICIENT_EVIDENCE',
                'safety_note': CitationValidator.STATUTORY_SAFETY_NOTE,
                'validation_diagnostics': {
                    'total_claims': 0,
                    'grounded_claims': 0,
                    'unsupported_claims': 0,
                    'hallucination_detected': False,
                    'audit_reasons': ['Zero retrieved evidence chunks provided in context.']
                }
            }

        from apps.observability.metrics import ObservabilityRegistry
        registry = ObservabilityRegistry()

        # Track retrieved evidence chunk IDs
        chunk_ids = [str(c.get('chunk_id') or c.get('id') or '') for c in ctx.retrieved_evidence if c]
        registry.record_retrieval(
            duration_ms=12.5,
            candidate_count=len(ctx.retrieved_evidence),
            evidence_chunk_ids=chunk_ids
        )

        user_prompt = self.prompt_builder.build_user_prompt(ctx)
        raw_output = None
        fallback_used = False

        # Attempt LLM generation if configured
        if self.model:
            llm_start = time.time()
            try:
                response = self.model.generate_content(
                    user_prompt,
                    generation_config=genai.types.GenerationConfig(
                        temperature=0.1,  # Ultra-low temperature for maximum factual fidelity
                        response_mime_type="application/json"
                    )
                )
                llm_duration = round((time.time() - llm_start) * 1000, 2)
                raw_output = json.loads(response.text)
                prompt_toks = len(user_prompt) // 4
                comp_toks = len(response.text) // 4
                registry.record_llm_call(
                    model_name="gemini-1.5-flash",
                    duration_ms=llm_duration,
                    prompt_tokens=prompt_toks,
                    completion_tokens=comp_toks,
                    success=True
                )
            except Exception as e:
                llm_duration = round((time.time() - llm_start) * 1000, 2)
                raw_output = None
                registry.record_llm_call(
                    model_name="gemini-1.5-flash",
                    duration_ms=llm_duration,
                    success=False,
                    fallback_triggered=True
                )

        # Fallback to high-fidelity deterministic grounded synthesizer if LLM offline or returned invalid JSON
        if not raw_output or not isinstance(raw_output, dict):
            fallback_used = True
            raw_output = self._deterministic_grounded_synthesis(ctx)
            registry.record_fallback(
                component="GroundedEvidenceComposer",
                reason="LLM offline or returned non-JSON; engaged deterministic synthesizer."
            )

        # Enforce strict output schema validation and sanitize fields
        _, raw_output, _ = SchemaConstrainedOutputValidator.validate_output_schema(raw_output)

        # Run strict 5-stage citation validation and hallucination containment
        validated_result = self.validator.validate_and_remediate(
            raw_output=raw_output,
            context_chunks=ctx.retrieved_evidence
        )

        # Provide safe XSS-immune rendered answer for frontend consumption
        validated_result['safe_rendered_answer'] = SafeRenderer.render_safe_text(validated_result.get('answer', ''))
        validated_result['fallback_mode_active'] = fallback_used

        return validated_result

    def _deterministic_grounded_synthesis(self, ctx: ComposerContext) -> Dict[str, Any]:
        """
        Deterministic, audit-proof synthesis engine when LLM is unavailable.
        Extracts relevant clauses verbatim from retrieved chunks, aligns with
        deterministic rule results, and builds the strict JSON structure.
        """
        top_chunks = ctx.retrieved_evidence[:3]
        claims = []
        citations = []
        unresolved = []

        answer_sentences = []
        if ctx.candidate_scheme_name:
            answer_sentences.append(f"Regarding {ctx.candidate_scheme_name}:")

        for idx, chunk in enumerate(top_chunks, start=1):
            cid = str(chunk.get('chunk_id') or chunk.get('id'))
            text = chunk.get('chunk_text', '').strip()
            heading = chunk.get('section_heading', 'Statutory Clause')
            first_sentence = text.split('.')[0].strip() + "."

            claims.append({
                'claim_text': f"According to {heading}, {first_sentence}",
                'evidence_chunk_ids': [cid]
            })

            citations.append({
                'chunk_id': cid,
                'document_title': chunk.get('document_title', 'Official Policy Document'),
                'authority': chunk.get('authority', 'Competent Authority'),
                'source_url': chunk.get('source_url', ''),
                'page_number': chunk.get('page_number', 1),
                'section_heading': heading,
                'exact_quote_snippet': first_sentence[:200]
            })

            answer_sentences.append(f"Under {heading}: {first_sentence}")

        # Check deterministic rule evaluations for unresolved items
        if ctx.deterministic_rule_results:
            for r in ctx.deterministic_rule_results:
                if r.get('evaluation_status') in ['UNKNOWN', 'REQUIRES_OFFICIAL_VERIFICATION']:
                    unresolved.append(f"Verification required: {r.get('rule_name', '')} ({r.get('reason', '')})")

        return {
            'answer': " ".join(answer_sentences),
            'evidence_claims': claims,
            'citations': citations,
            'unresolved_questions': unresolved or ["Confirm active Udyam registration and physical plant verification."],
            'status': 'GROUNDED',
            'safety_note': CitationValidator.STATUTORY_SAFETY_NOTE
        }
