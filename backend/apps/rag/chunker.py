"""
Page-aware text extraction, legal section detection, SimHash fingerprinter,
and provenance-preserving chunker for official government policy documents.
"""
import re
import hashlib
from typing import List, Dict, Any, Tuple


def compute_sha256(content: bytes) -> str:
    """Compute standard SHA-256 hexadecimal hash."""
    return hashlib.sha256(content).hexdigest()


def compute_simhash(text: str, hashbits: int = 64) -> str:
    """
    Compute SimHash for near-duplicate document detection across
    statutory circulars, amendments, and notifications.
    """
    tokens = re.findall(r'\b\w{3,}\b', text.lower())
    if not tokens:
        return "0" * (hashbits // 4)

    v = [0] * hashbits
    for token in tokens:
        # 64-bit integer hash
        h = int(hashlib.md5(token.encode('utf-8')).hexdigest()[:16], 16)
        for i in range(hashbits):
            bitmask = 1 << i
            if h & bitmask:
                v[i] += 1
            else:
                v[i] -= 1

    fingerprint = 0
    for i in range(hashbits):
        if v[i] > 0:
            fingerprint |= (1 << i)

    return f"{fingerprint:016x}"


class LegalDocumentParser:
    """
    Extracts text and cleans legal government policy documents (Gazettes,
    Operational Guidelines, Government Resolutions, Circulars).
    Preserves page boundaries and identifies section/clause headers.
    """

    CLAUSE_PATTERNS = [
        # Clause 4.2 / Clause 4.2(a) / Clause 5
        r'^(?:Clause|Cl\.)\s+([0-9]+(?:\.[0-9]+)*(?:\([a-zA-Z0-9]+\))*)[:\s\-]*(.*)$',
        # Section 3 / Section 3(1)(a)
        r'^(?:Section|Sec\.)\s+([0-9]+(?:\([a-zA-Z0-9]+\))*)(?:[\s\:\.\-]+(.*))?$',
        # Rule 5 / Rule 12A
        r'^(?:Rule)\s+([0-9]+[A-Za-z]*)(?:[\s\:\.\-]+(.*))?$',
        # Paragraph 2 / Para 2.1
        r'^(?:Paragraph|Para)\s+([0-9]+(?:\.[0-9]+)*)(?:[\s\:\.\-]+(.*))?$',
        # Standard Legal / Policy Heading keywords
        r'^(?:1|2|3|4|5|6|7|8|9|10|11|12|13|14|15|16|17|18|19|20)\.\s+([A-Z][A-Za-z0-9\s,\-\/\(\)]+)$',
        # Capitalized statutory headings
        r'^(ELIGIBILITY(?:\s+CRITERIA)?|QUANTUM\s+OF\s+ASSISTANCE|FINANCIAL\s+ASSISTANCE|INELIGIBLE\s+ACTIVITIES|APPLICATION\s+PROCEDURE|TERMS\s+AND\s+CONDITIONS|DEFINITIONS|OBJECTIVE|NODAL\s+AGENCY|DISBURSEMENT\s+SCHEDULE)[:\s\-]*(.*)$',
    ]

    def __init__(self):
        self.compiled_patterns = [
            re.compile(p, re.IGNORECASE | re.MULTILINE) for p in self.CLAUSE_PATTERNS
        ]

    def clean_text(self, text: str) -> str:
        """
        Normalize whitespace while preserving legal punctuation, numbering,
        and clause formatting.
        """
        if not text:
            return ""
        # Remove null bytes
        text = text.replace('\x00', '')
        # Remove repetitive header/footer line artifacts like 'Page X of Y' or 'Government of Gujarat'
        text = re.sub(r'Page\s+\d+\s+of\s+\d+', '', text, flags=re.IGNORECASE)
        # Normalize carriage returns and tabs
        text = text.replace('\r\n', '\n').replace('\r', '\n')
        # Replace multiple spaces with single space
        text = re.sub(r'[ \t]+', ' ', text)
        # Replace excessive blank lines
        text = re.sub(r'\n{3,}', '\n\n', text)
        return text.strip()

    def parse_pages(self, raw_pages: List[Tuple[int, str]]) -> List[Dict[str, Any]]:
        """
        Takes list of (page_number, raw_text) and breaks into section-aware chunks.
        Retains page number, clause heading, and token approximations.
        """
        chunks = []
        chunk_idx = 1
        current_section = "General Provisions"

        for page_num, raw_content in raw_pages:
            cleaned = self.clean_text(raw_content)
            if not cleaned:
                continue

            lines = cleaned.split('\n')
            current_buffer = []

            for line in lines:
                stripped = line.strip()
                if not stripped:
                    continue

                # Check if this line introduces a new section or clause
                detected_heading = None
                for pattern in self.compiled_patterns:
                    match = pattern.match(stripped)
                    if match:
                        detected_heading = stripped
                        break

                if detected_heading:
                    # Flush existing buffer as a chunk if it has substantial content
                    if current_buffer:
                        chunk_text = " ".join(current_buffer).strip()
                        if len(chunk_text.split()) >= 15:
                            chunks.append(self._create_chunk_dict(
                                chunk_idx=chunk_idx,
                                page_number=page_num,
                                section_heading=current_section,
                                chunk_text=chunk_text
                            ))
                            chunk_idx += 1
                        current_buffer = []
                    current_section = detected_heading[:250]
                    current_buffer.append(stripped)
                else:
                    current_buffer.append(stripped)
                    # Check buffer size: if > 350 words, split preserving section heading
                    word_count = sum(len(l.split()) for l in current_buffer)
                    if word_count >= 300:
                        chunk_text = " ".join(current_buffer).strip()
                        chunks.append(self._create_chunk_dict(
                            chunk_idx=chunk_idx,
                            page_number=page_num,
                            section_heading=current_section,
                            chunk_text=chunk_text
                        ))
                        chunk_idx += 1
                        # Retain last 30 words as semantic sliding-window overlap
                        overlap_words = chunk_text.split()[-30:]
                        current_buffer = [" ".join(overlap_words)]

            # Flush remaining buffer at end of page
            if current_buffer:
                chunk_text = " ".join(current_buffer).strip()
                if len(chunk_text.split()) >= 15:
                    chunks.append(self._create_chunk_dict(
                        chunk_idx=chunk_idx,
                        page_number=page_num,
                        section_heading=current_section,
                        chunk_text=chunk_text
                    ))
                    chunk_idx += 1

        return chunks

    def _create_chunk_dict(self, chunk_idx: int, page_number: int, section_heading: str, chunk_text: str) -> Dict[str, Any]:
        """Helper to assemble raw chunk dictionary with checksum."""
        tokens = len(chunk_text.split())
        chunk_hash = hashlib.sha256(chunk_text.encode('utf-8')).hexdigest()
        return {
            'chunk_index': chunk_idx,
            'page_number': page_number,
            'section_heading': section_heading,
            'chunk_text': chunk_text,
            'chunk_hash': chunk_hash,
            'token_count': tokens,
        }
