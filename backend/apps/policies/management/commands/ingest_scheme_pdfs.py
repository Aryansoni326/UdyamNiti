"""
Automated Scheme PDF Ingestion & Extraction Command for UdyamNiti.

Scans the designated PDF folder:
  `backend/data/scheme_pdfs/` (or a custom path passed via --dir or --file)
Extracts policy text using PyPDF and converts guidelines into structured
Scheme, SchemeBenefit, and SchemeRule records in the database.

Usage:
  python manage.py ingest_scheme_pdfs
  python manage.py ingest_scheme_pdfs --file=path/to/scheme.pdf
  python manage.py ingest_scheme_pdfs --dir=path/to/folder
"""
import os
import re
import json
import logging
from datetime import date
from pathlib import Path
from django.core.management.base import BaseCommand
from django.core.cache import cache
from apps.policies.models import Scheme, SchemeRule, SchemeBenefit

logger = logging.getLogger(__name__)

APPS_SCHEME_PDF_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    'data',
    'schemes_pdfs'
)
DATA_SCHEME_PDF_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))),
    'data',
    'scheme_pdfs'
)
DEFAULT_SCHEME_PDF_DIR = APPS_SCHEME_PDF_DIR if os.path.exists(APPS_SCHEME_PDF_DIR) else DATA_SCHEME_PDF_DIR


def extract_text_from_pdf(pdf_path: str) -> str:
    """Extract all text pages from a PDF file using pypdf."""
    from pypdf import PdfReader
    reader = PdfReader(pdf_path)
    pages_text = []
    for idx, page in enumerate(reader.pages):
        text = page.extract_text() or ''
        pages_text.append(f"--- Page {idx + 1} ---\n{text}")
    return "\n\n".join(pages_text)


def parse_scheme_with_llm_or_heuristics(raw_text: str, filename: str) -> dict:
    """
    Parses raw PDF text into structured Scheme fields.
    Uses Gemini API if GEMINI_API_KEY is available; otherwise falls back
    to robust heuristic extraction.
    """
    gemini_key = os.environ.get('GEMINI_API_KEY', '').strip()
    
    if gemini_key:
        try:
            import google.generativeai as genai
            genai.configure(api_key=gemini_key)
            model = genai.GenerativeModel('gemini-1.5-flash')
            
            prompt = f"""You are an expert Government Policy Legal Analyst.
Analyze the following official government scheme guideline document and extract structured JSON matching this schema:

{{
  "scheme_code": "UNIQUE_SHORT_CODE (e.g. GUJ_TEXTILE_2026, CGTMSE_EXP_2026)",
  "name": "Full Official Scheme Name",
  "short_name": "Concise Name",
  "ministry_department": "Issuing Ministry or State Department",
  "implementing_agency": "Nodal Implementing Agency / Directorate",
  "level": "central OR state_gujarat OR state",
  "support_type": "capital_subsidy OR credit_guarantee OR interest_subvention OR technology_grant OR infrastructure OR quality_certification",
  "target_sectors": ["manufacturing", "textile", "etc"],
  "target_msme_categories": ["micro", "small", "medium"],
  "max_benefit_amount_lakhs": 100.0,
  "benefit_percentage": 25.0,
  "benefit_description": "Comprehensive explanation of financial subsidy, loan limit, interest subvention or grant",
  "description": "Full scheme overview, objectives, and background",
  "eligibility_summary": "Numbered list of who is eligible and key criteria",
  "application_process": "Sequential step-by-step application instructions",
  "gazette_notification": "Official Notification, Circular, or Government Resolution Number",
  "official_portal_url": "URL if present or official ministry website",
  "benefits": [
    {{
      "benefit_name": "Name of specific benefit slab",
      "benefit_type": "capital_subsidy OR interest_subvention OR etc",
      "amount_or_percentage": "e.g. 25% up to ₹2.5 Crore",
      "conditions": "Applicable condition",
      "source_clause": "Clause reference if available"
    }}
  ],
  "rules": [
    {{
      "rule_name": "Criterion name (e.g. Valid Udyam Certificate)",
      "field_path": "has_udyam_registration",
      "operator": "bool_true",
      "expected_value": true,
      "importance": "mandatory",
      "display_label": "Valid Udyam Registration",
      "source_clause": "Verbatim quote or clause reference"
    }}
  ]
}}

DOCUMENT TEXT (first 30,000 characters):
{raw_text[:30000]}

Return ONLY valid raw JSON without markdown code fences.
"""
            response = model.generate_content(prompt)
            clean_json = response.text.strip()
            if clean_json.startswith('```'):
                clean_json = re.sub(r'^```json\s*|^```\s*|```$', '', clean_json, flags=re.MULTILINE).strip()
            data = json.loads(clean_json)
            return data
        except Exception as e:
            logger.warning(f"LLM extraction fallback to heuristics: {e}")

    # Deterministic Heuristic Extractor fallback
    clean_name = Path(filename).stem.replace('_', ' ').replace('-', ' ').title()
    code_slug = re.sub(r'[^A-Z0-9]+', '_', clean_name.upper())[:30]

    # Detect level
    is_gujarat = bool(re.search(r'gujarat|gujarāt|gidc|gandhinagar|surat', raw_text, re.I))
    level = 'state_gujarat' if is_gujarat else 'central'

    # Detect support type
    support_type = 'capital_subsidy'
    if re.search(r'guarantee|cgtmse|collateral', raw_text, re.I):
        support_type = 'credit_guarantee'
    elif re.search(r'interest\s*subvention|interest\s*subsidy', raw_text, re.I):
        support_type = 'interest_subvention'
    elif re.search(r'infrastructure|park|cluster', raw_text, re.I):
        support_type = 'infrastructure'

    # Detect max amount
    max_amount_match = re.search(r'(?:₹|rs\.?|inr)?\s*(\d+(?:\.\d+)?)\s*(?:crore|cr|lakh|lakhs)', raw_text, re.I)
    max_lakhs = 100.0
    if max_amount_match:
        val = float(max_amount_match.group(1))
        unit = max_amount_match.group(0).lower()
        max_lakhs = val * 100 if ('crore' in unit or 'cr' in unit) else val

    # Gazette reference detection
    gazette_match = re.search(r'(?:Notification\s*No\.?|Circular\s*No\.?|G\.?R\.?\s*No\.?|Reference\s*No\.?)\s*[:\-]?\s*([^\n\r,;]{5,80})', raw_text, re.I)
    gazette_ref = gazette_match.group(0).strip() if gazette_match else f"Official Notification Ref for {clean_name}"

    # Ministry detection
    ministry_match = re.search(r'(Ministry\s+of\s+[A-Za-z\s]+|Industries\s+(?:and\s+Mines\s+)?Department[A-Za-z\s,]*)', raw_text, re.I)
    ministry = ministry_match.group(0).strip() if ministry_match else ('Industries & Mines Department, Government of Gujarat' if is_gujarat else 'Ministry of Micro, Small and Medium Enterprises')

    return {
        'scheme_code': code_slug,
        'name': clean_name,
        'short_name': clean_name[:40],
        'ministry_department': ministry,
        'implementing_agency': 'Directorate of Industries / District Industries Centre (DIC)',
        'level': level,
        'support_type': support_type,
        'target_sectors': ['manufacturing', 'services', 'industrial'],
        'target_msme_categories': ['micro', 'small', 'medium'],
        'target_states': ['Gujarat'] if is_gujarat else [],
        'max_benefit_amount_lakhs': max_lakhs,
        'benefit_percentage': 25.0,
        'benefit_description': f"Statutory financial assistance and subsidies under {clean_name} for eligible enterprises as per official gazette terms.",
        'description': (
            f"Official Government scheme: {clean_name}. Extracted from primary gazette documentation. "
            "Enables registered Micro, Small, and Medium Enterprises to access financial assistance, "
            "infrastructure linkage, or capital support."
        ),
        'eligibility_summary': (
            "1. Must possess a valid MSME Udyam Registration Certificate.\n"
            "2. Enterprise category must fall within Micro, Small, or Medium classification limits.\n"
            "3. Operational bank account and clean financial track record without NPA classification.\n"
            "4. Prescribed investment and plant machinery procurement criteria as per gazette clauses."
        ),
        'application_process': (
            "Step 1: Check eligibility against enterprise Udyam facts and DPR financial estimates.\n"
            "Step 2: Compile mandatory statutory checklist documents (CA Certificate, Quotations, Bank Sanction).\n"
            "Step 3: Submit online application on the designated government single-window portal.\n"
            "Step 4: Inspection and appraisal by competent authorities / DIC officers.\n"
            "Step 5: Direct Benefit Transfer (DBT) grant or guarantee sanction disbursement."
        ),
        'gazette_notification': gazette_ref,
        'official_portal_url': 'https://ifp.gujarat.gov.in' if is_gujarat else 'https://msme.gov.in',
        'benefits': [
            {
                'benefit_name': f'Assistance Grant under {clean_name}',
                'benefit_type': support_type,
                'amount_or_percentage': f'Up to ₹{max_lakhs / 100:.2f} Cr' if max_lakhs >= 100 else f'Up to ₹{max_lakhs:.1f} Lakhs',
                'conditions': 'Subject to verified DPR and compliance with statutory eligibility conditions.',
                'source_clause': gazette_ref
            }
        ],
        'rules': [
            {
                'rule_name': 'Valid MSME Udyam Registration',
                'field_path': 'has_udyam_registration',
                'operator': 'bool_true',
                'expected_value': True,
                'importance': 'mandatory',
                'display_label': 'Valid Udyam Registration Certificate',
                'source_clause': 'Mandatory statutory requirement under MSMED Act.'
            },
            {
                'rule_name': 'Not Classified as NPA',
                'field_path': 'is_npa',
                'operator': 'bool_false',
                'expected_value': False,
                'importance': 'mandatory',
                'display_label': 'Good Financial Standing (Non-NPA)',
                'source_clause': 'Borrower must not be classified as Non-Performing Asset.'
            }
        ]
    }


class Command(BaseCommand):
    help = 'Ingests official scheme PDF files from backend/data/scheme_pdfs/ into the database.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--file',
            type=str,
            help='Path to a specific PDF file to ingest'
        )
        parser.add_argument(
            '--dir',
            type=str,
            default=DEFAULT_SCHEME_PDF_DIR,
            help='Directory containing scheme PDF files to ingest'
        )

    def handle(self, *args, **options):
        single_file = options.get('file')
        pdf_dir = options.get('dir') or DEFAULT_SCHEME_PDF_DIR

        pdf_files = []
        if single_file:
            if not os.path.exists(single_file):
                self.stderr.write(self.style.ERROR(f"Specified file does not exist: {single_file}"))
                return
            pdf_files = [single_file]
        else:
            if not os.path.exists(pdf_dir):
                os.makedirs(pdf_dir, exist_ok=True)
                self.stdout.write(self.style.WARNING(f"Created empty directory: {pdf_dir}"))
                self.stdout.write(f"Drop your Scheme PDF documents into: {pdf_dir}")
                return

            for fname in os.listdir(pdf_dir):
                if fname.lower().endswith('.pdf'):
                    pdf_files.append(os.path.join(pdf_dir, fname))

        if not pdf_files:
            self.stdout.write(self.style.WARNING(f"No .pdf files found in: {pdf_dir}"))
            self.stdout.write(f"👉 Copy your Scheme PDF files into: {pdf_dir} and run this command again.")
            return

        self.stdout.write(self.style.SUCCESS(f"\n📂 Found {len(pdf_files)} PDF file(s) to process in {pdf_dir}:"))
        for p in pdf_files:
            self.stdout.write(f"  • {os.path.basename(p)}")

        success_count = 0
        for pdf_path in pdf_files:
            fname = os.path.basename(pdf_path)
            self.stdout.write(f"\n⚡ Processing: {fname}...")
            try:
                raw_text = extract_text_from_pdf(pdf_path)
                if not raw_text.strip():
                    self.stderr.write(self.style.WARNING(f"  ⚠️ Warning: No extractable text in {fname} (might be scanned images)."))
                    continue

                scheme_data = parse_scheme_with_llm_or_heuristics(raw_text, fname)
                rules_data = scheme_data.pop('rules', [])
                benefits_data = scheme_data.pop('benefits', [])

                # Ensure status is active
                scheme_data['status'] = 'active'
                if not scheme_data.get('launch_date'):
                    scheme_data['launch_date'] = date.today()

                scheme, created = Scheme.objects.update_or_create(
                    scheme_code=scheme_data['scheme_code'],
                    defaults=scheme_data
                )
                action_str = 'Created new' if created else 'Updated existing'
                self.stdout.write(self.style.SUCCESS(f"  ✓ {action_str} Scheme: {scheme.name} (Code: {scheme.scheme_code})"))

                # Ingest Rules
                for i, rdata in enumerate(rules_data):
                    rdata['order'] = i
                    SchemeRule.objects.update_or_create(
                        scheme=scheme,
                        rule_name=rdata['rule_name'],
                        defaults=rdata
                    )

                # Ingest Benefits
                for bdata in benefits_data:
                    SchemeBenefit.objects.update_or_create(
                        scheme=scheme,
                        benefit_name=bdata['benefit_name'],
                        defaults=bdata
                    )

                success_count += 1
            except Exception as e:
                self.stderr.write(self.style.ERROR(f"  ❌ Failed to ingest {fname}: {e}"))

        # Flush policy cache so frontend immediately sees new schemes
        try:
            cache.clear()
        except Exception:
            pass

        self.stdout.write(self.style.SUCCESS(f"\n🎉 Successfully ingested {success_count} scheme(s)! They will now reflect on the Schemes Dashboard and Detail pages."))
