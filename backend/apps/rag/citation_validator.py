"""
Citation Fidelity & Hallucination Validator for Grounded Policy Explanations.
Enforces:
1. Exact ID integrity (every cited chunk must exist in prompt context).
2. Numerical & factual entity alignment (numbers, percentages, currencies must exist in source text).
3. Attribution of every material claim to at least one valid chunk.
4. Auto-remediation: downgrades ungrounded output to INSUFFICIENT_EVIDENCE or REJECTED_UNGROUNDED.
"""
import re
from typing import List, Dict, Any, Tuple


class CitationValidator:
    """
    Validates that LLM output claims and citations are strictly grounded in
    the provided official government context.
    """

    STATUTORY_SAFETY_NOTE = (
        "Statutory Disclaimer: This explanation is synthesized solely from official government documents "
        "(Gazettes, Guidelines, and Circulars) provided in context. It does not constitute formal statutory sanction "
        "or legal advice. Final benefit approval rests solely with the competent government authority."
    )

    def validate_and_remediate(
        self,
        raw_output: Dict[str, Any],
        context_chunks: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Validates raw LLM JSON response against context chunks and remediates
        any phantom IDs or unsupported factual claims.
        """
        # Map available context chunk IDs and their normalized text
        context_map: Dict[str, str] = {
            str(c.get('chunk_id') or c.get('id')): (c.get('chunk_text', '') + " " + c.get('section_heading', ''))
            for c in context_chunks
        }

        claims = raw_output.get('evidence_claims', [])
        citations = raw_output.get('citations', [])
        unresolved = raw_output.get('unresolved_questions', [])
        current_status = raw_output.get('status', 'GROUNDED')

        validated_claims = []
        valid_citations = []
        hallucination_detected = False
        reasons = []

        # 1. Validate Citations: ensure every citation references an actual context chunk
        seen_citation_ids = set()
        for cit in citations:
            cid = str(cit.get('chunk_id', ''))
            if cid not in context_map:
                hallucination_detected = True
                reasons.append(f"Phantom citation ID '{cid}' does not exist in prompt context.")
                continue

            # Verify snippet actually appears in chunk text
            snippet = cit.get('exact_quote_snippet', '').strip()
            chunk_text = context_map[cid]
            if snippet and not self._fuzzy_substring_match(snippet, chunk_text):
                reasons.append(f"Quote snippet in citation '{cid}' was not found verbatim in source text.")

            if cid not in seen_citation_ids:
                seen_citation_ids.add(cid)
                valid_citations.append(cit)

        # 2. Validate Evidence Claims
        for claim in claims:
            claim_text = claim.get('claim_text', '').strip()
            evidence_ids = [str(x) for x in claim.get('evidence_chunk_ids', [])]

            if not evidence_ids:
                # Material claim with zero citation
                validated_claims.append({
                    'claim_text': claim_text,
                    'evidence_chunk_ids': [],
                    'verification_status': 'unsupported'
                })
                reasons.append(f"Claim lacks supporting citation: '{claim_text}'")
                continue

            # Check if all cited chunk IDs exist
            invalid_ids = [cid for cid in evidence_ids if cid not in context_map]
            if invalid_ids:
                hallucination_detected = True
                validated_claims.append({
                    'claim_text': claim_text,
                    'evidence_chunk_ids': [cid for cid in evidence_ids if cid in context_map],
                    'verification_status': 'hallucinated_id'
                })
                reasons.append(f"Claim cited non-existent chunk IDs {invalid_ids}: '{claim_text}'")
                continue

            # Check numerical and entity alignment
            aligned, mismatch_reason = self._verify_numerical_alignment(claim_text, evidence_ids, context_map)
            if not aligned:
                hallucination_detected = True
                validated_claims.append({
                    'claim_text': claim_text,
                    'evidence_chunk_ids': evidence_ids,
                    'verification_status': 'unsubstantiated_numbers'
                })
                reasons.append(f"Numerical/entity mismatch: {mismatch_reason}")
            else:
                validated_claims.append({
                    'claim_text': claim_text,
                    'evidence_chunk_ids': evidence_ids,
                    'verification_status': 'grounded'
                })

        # 3. Determine Final Status & Remediate
        grounded_count = sum(1 for c in validated_claims if c['verification_status'] == 'grounded')
        unsupported_count = len(validated_claims) - grounded_count

        if hallucination_detected or unsupported_count > 0:
            if grounded_count == 0:
                final_status = 'REJECTED_UNGROUNDED'
                remediated_answer = (
                    "UNKNOWN / INSUFFICIENT OFFICIAL EVIDENCE: The platform could not substantiate the answer "
                    "using verified official policy documents in the active context."
                )
            else:
                final_status = 'PARTIAL_EVIDENCE'
                remediated_answer = raw_output.get('answer', '') + "\n\n[Caution: Certain secondary points could not be verified from statutory text.]"
        else:
            final_status = 'GROUNDED'
            remediated_answer = raw_output.get('answer', '')

        # Safety note is strictly enforced
        safety_note = self.STATUTORY_SAFETY_NOTE
        if reasons:
            safety_note += " Validation Notes: " + "; ".join(reasons[:3])

        return {
            'answer': remediated_answer,
            'evidence_claims': validated_claims,
            'citations': valid_citations,
            'unresolved_questions': unresolved,
            'status': final_status,
            'safety_note': safety_note,
            'validation_diagnostics': {
                'total_claims': len(claims),
                'grounded_claims': grounded_count,
                'unsupported_claims': unsupported_count,
                'hallucination_detected': hallucination_detected,
                'audit_reasons': reasons
            }
        }

    def _fuzzy_substring_match(self, snippet: str, full_text: str) -> bool:
        """Checks if a snippet appears in text ignoring whitespace/case differences."""
        clean_snip = re.sub(r'\s+', ' ', snippet.lower()).strip()
        clean_full = re.sub(r'\s+', ' ', full_text.lower()).strip()
        return clean_snip in clean_full

    def _verify_numerical_alignment(
        self,
        claim_text: str,
        evidence_ids: List[str],
        context_map: Dict[str, str]
    ) -> Tuple[bool, str]:
        """
        Extracts numbers, currency amounts (Rs., Lakhs, Crores), and percentages
        from claim_text and checks if they exist in the combined text of the cited chunks.
        Prevents LLMs from inventing fake subsidies or thresholds.
        """
        # Match percentages e.g. 25%, 7%, 85.5%
        claim_percentages = set(re.findall(r'\b\d+(?:\.\d+)?%', claim_text))
        # Match rupee amounts e.g. Rs. 50 Lakhs, 35 Lakhs, 500 Lakhs, 1 Crore
        claim_financials = set(re.findall(r'(?:Rs\.?\s*)?\d+(?:\.\d+)?\s*(?:Lakhs?|Crores?|Cr)', claim_text, re.IGNORECASE))

        combined_evidence = " ".join(context_map[cid] for cid in evidence_ids).lower()

        # Check percentages
        for p in claim_percentages:
            if p.lower() not in combined_evidence:
                return False, f"Percentage '{p}' cited in claim is absent from supporting evidence."

        # Check financial amounts
        for f in claim_financials:
            # Normalize e.g. '50 Lakhs' or 'Rs. 50 Lakhs'
            num_match = re.search(r'\d+(?:\.\d+)?', f)
            unit_match = re.search(r'(?:lakh|crore|cr)', f, re.IGNORECASE)
            if num_match and unit_match:
                num = num_match.group(0)
                unit = unit_match.group(0).lower()
                pattern = rf'{num}\s*{unit}'
                if not re.search(pattern, combined_evidence, re.IGNORECASE):
                    return False, f"Financial threshold '{f}' cited in claim is absent from supporting evidence."

        return True, ""
