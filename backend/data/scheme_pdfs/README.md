# Scheme Guidelines & Gazette PDFs Directory

Place your official Government MSME Scheme PDF documents here.

### Supported Document Types:
- Official Gazette Notifications (Central / Gujarat Government)
- Operational Scheme Guidelines & Circulars
- Ministry Benefit & Subsidy Policy Documents (e.g. CGTMSE, Coir Vikas Yojana, Capital Subsidy, PMEGP, etc.)

### How It Works:
1. Copy your `.pdf` files into this directory:
   `backend/data/scheme_pdfs/`
2. Run the ingestion command:
   ```bash
   # If running locally in backend virtualenv:
   python manage.py ingest_scheme_pdfs

   # If running via Docker Compose:
   docker-compose exec backend python manage.py ingest_scheme_pdfs
   ```
3. The platform will automatically:
   - Extract raw text and clauses via `pypdf`
   - Parse Scheme Code, Title, Ministry, Benefits, Eligibility criteria, Documents, and Application Steps
   - Save the scheme into PostgreSQL
   - The scheme will instantly reflect on the Schemes Dashboard (`/dashboard`) and Scheme Detail Page (`/scheme/<id>`).
