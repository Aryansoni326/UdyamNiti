# 🇮🇳 UdyamNiti: AI Government-Support Intelligence Platform for Indian MSMEs

> **"Tell us your business goal. We build your statutory government-support strategy."**
>
> An enterprise-grade, deterministic AI advisory platform that maps MSME growth goals against 30+ Central and Gujarat Government schemes with statutory clause-level evidence, cross-scheme relationship reasoning, and automated application readiness.

---

## ⚡ 60-Second Judge Quickstart (One-Command Startup)

Every dependency—PostgreSQL with pgvector, Redis, MinIO S3, Django API, Celery worker, and Vite React frontend—is orchestrated via Docker Compose. Database migrations, seed schemes, and the golden ABC Engineering profile execute automatically upon startup.

```bash
# 1. Clone repository & enter workspace
git clone https://github.com/your-org/UdyamNiti.git
cd UdyamNiti

# 2. Copy the safe development environment (Zero secrets required to run!)
cp .env.example .env

# 3. Launch the complete application stack
docker-compose up --build
```

**That's it!** The system automatically:
1. Provisions PostgreSQL 16 and initializes the `pgvector` extension.
2. Boots Redis 7 and verifies health.
3. Boots MinIO and automatically provisions the `udyamniti-documents` bucket.
4. Executes `python manage.py wait_for_db` ensuring database readiness.
5. Runs Django database migrations.
6. Loads all 30+ Central & Gujarat schemes, statutory rules, cross-scheme relationships, and the golden test profile.
7. Launches the React frontend on `http://localhost:3000`.

---

## 🌐 Service Ports & Access Matrix

| Service | Port | URL | Description & Credentials |
| :--- | :--- | :--- | :--- |
| **Frontend UI** | `3000` | [http://localhost:3000](http://localhost:3000) | React 18 + Vite interactive dashboard |
| **Backend REST API** | `8000` | [http://localhost:8000/api/v1/](http://localhost:8000/api/v1/) | Django REST Framework API root |
| **API Documentation** | `8000` | [http://localhost:8000/api/docs/](http://localhost:8000/api/docs/) | Interactive Swagger / OpenAPI Specification |
| **System Health Check** | `8000` | [http://localhost:8000/api/v1/health/](http://localhost:8000/api/v1/health/) | JSON health status (DB, Redis, Vector index) |
| **MinIO Web Console** | `9001` | [http://localhost:9001](http://localhost:9001) | S3 UI (`User: minioadmin` / `Pass: minioadmin`) |
| **MinIO S3 API** | `9000` | [http://localhost:9000](http://localhost:9000) | S3-compatible document storage endpoint |
| **PostgreSQL (pgvector)** | `5432` | `localhost:5432` | DB: `udyamniti`, User: `udyamniti`, Pass: `udyamniti_secret` |
| **Redis Cache / Queue** | `6379` | `localhost:6379` | In-memory cache & Celery broker |

---

## 🏭 Golden Demo Walkthrough (ABC Engineering Works)

1. Open **[http://localhost:3000](http://localhost:3000)** in your browser.
2. Click **"ABC Engineering Demo →"** on the home screen:
   - **Profile Loaded**: Small Precision Engineering Unit, Surat, Gujarat (Udyam Verified, Investment: ₹45 Lakhs, Turnover: ₹1.8 Crores).
   - **Goal Pre-filled**: *"We want to expand precision machining capacity by purchasing a modern ₹50 Lakh CNC milling center."*
3. Click **"Generate Strategy"**:
   - Watch the real-time orchestrator execute candidate discovery, vector similarity matching, deterministic rule evaluation, and cross-scheme relationship reasoning.
4. **Inspect the Strategy Dashboard**:
   - **Matched Schemes**: Discover Gujarat Assistance for Capital Investment (15% subsidy) and Central CLCSS / Credit Guarantee (CGTMSE).
   - **Status Chips**: Clear statutory status tags (`MATCH`, `POTENTIAL MATCH`, `UNKNOWN`).
   - **"Why This Scheme?" Evidence Drawer**: View exact statutory citations, operational guidelines, and clause references.
   - **Cross-Scheme Optimization**: Notice how CGTMSE collateral guarantees sequence prior to bank term loan approval.
   - **Action Plan**: Review the milestone timeline and required documentation checklist.
5. Visit the **Policy Monitor** (`/policy-monitor`):
   - Review recent gazette notifications and real-time alerts demonstrating how statutory amendments re-evaluate business eligibility.

---

## 🏗️ System Architecture & Data Flow

```
                      ┌───────────────────────────────────────┐
                      │          React 18 + Vite UI           │
                      │        (Port 3000, TypeScript)        │
                      └──────────────────┬────────────────────┘
                                         │ REST API / SSE
                                         ▼
                      ┌───────────────────────────────────────┐
                      │          Django REST API              │
                      │            (Port 8000)                │
                      └──┬───────────────┬──────────────────┬─┘
                         │               │                  │
         ┌───────────────┴──┐    ┌───────┴────────┐   ┌─────┴───────────────┐
         ▼                  ▼    ▼                ▼   ▼                     ▼
┌──────────────────┐  ┌───────────────┐  ┌──────────────────┐  ┌────────────────┐
│  PostgreSQL 16   │  │    Redis 7    │  │  Celery Worker   │  │ MinIO (S3 API) │
│   + pgvector     │  │ (Cache/Broker)│  │ (Async Tasks/RAG)│  │  (Port 9000)   │
│   (Port 5432)    │  │  (Port 6379)  │  └──────────────────┘  └────────────────┘
└──────────────────┘  └───────────────┘
```

### Deterministic Multi-Agent Orchestrator
- **Goal Agent**: Normalizes natural language requests into typed machine goals.
- **Hybrid Retrieval**: Vector semantic search (`pgvector`) combined with full-text keyword indexing (`tsvector`).
- **Deterministic Rule Engine**: Zero hallucinations in statutory evaluation; boolean and arithmetic operations execute against canonical rules.
- **Cross-Scheme Engine**: Analyzes prerequisites, stacking conflicts, mutual exclusions, and sequence dependencies.
- **Strategy Agent**: Synthesizes the legal analysis into an actionable executive roadmap.

---

## 🧰 Developer CLI (`Makefile` Shortcuts)

```bash
# General Management
make up            # Start stack in foreground
make up-d          # Start stack in background (detached)
make down          # Stop all containers
make restart       # Restart running containers
make logs          # Follow logs from all services

# Service Specific Logs
make logs-backend  # Django REST API logs
make logs-frontend # Vite dev server logs
make logs-celery   # Celery worker logs
make logs-minio    # MinIO storage logs

# Database Operations
make seed          # Re-apply statutory schemes & demo profile
make migrate       # Run pending Django migrations
make shell-backend # Launch Django interactive shell
make shell-db      # Connect to PostgreSQL via psql

# Automated Testing
make test          # Run all automated tests (backend + frontend)
make test-backend  # Run backend pytest suite
make test-frontend # Run frontend vitest suite

# Clean Reset
make reset         # Stop, purge volumes, and rebuild completely
```

---

## 🔒 Security Baseline & No Secrets Guarantee

- **Zero Hardcoded Secrets**: Production secrets are never stored in version control. All services configure through environment variables with safe development defaults.
- **Offline / Mock Mode Available**: If no `GEMINI_API_KEY` is provided in `.env`, UdyamNiti gracefully defaults to built-in deterministic mocks for the ABC Engineering demo flow.
- **CORS & CSRF Controls**: Django `corsheaders` allows requests exclusively from `http://localhost:3000`, `http://127.0.0.1:3000`, and `http://localhost:5173`.
- **Tenant Isolation**: Object-level permissions enforce strict boundaries so MSMEs can only access their authorized profile records.
- **S3 Document Security**: Uploaded verification documents pass through MIME-type validation, file size limits (10MB), and private bucket storage.

---

## 🩺 Health Check & Diagnostics Verification

Verify that all subsystems are healthy and operational:

```bash
# Test API Health Endpoint
curl -s http://localhost:8000/api/v1/health/ | jq .
```

Expected JSON Output:
```json
{
  "status": "healthy",
  "database": "connected",
  "redis": "connected",
  "pgvector": "installed",
  "version": "1.0.0",
  "schemes_loaded": 32
}
```

---

## ❓ Troubleshooting & FAQs

- **Port 5432 or 8000 already in use?**
  If local Postgres or another service is running on your host machine, modify the host port mappings in `docker-compose.yml` (e.g., `"5433:5432"` or `"8080:8000"`).
- **Docker database connection timeout?**
  The backend container uses `python manage.py wait_for_db` with exponential backoff and health-check dependencies (`service_healthy`) to ensure Postgres is fully ready before running migrations.
- **Can I run backend tests in Docker?**
  Yes! Simply run:
  ```bash
  docker-compose exec backend pytest -v
  ```
- **Where are files persisted?**
  ---

## 🚨 Emergency War-Room Recovery Commands (Demo Day Playbook)

If an unexpected freeze, database state corruption, or network outage occurs during judging, use these battle-tested recovery commands:

### 1. Instant 15-Second Data & Demo Account Reset
If data was modified or dirty state was left from a previous test run:
```bash
# Re-apply canonical seed schemes, relationships, policy changes, and ABC Engineering profile:
docker-compose exec backend python manage.py seed_data

# Or trigger zero-friction auto-provisioning via cURL:
curl -s http://localhost:8000/api/v1/auth/demo/
```

### 2. Complete Zero-Downtime Clean Stack Rebuild (< 45 seconds)
If containers are completely stuck or ports conflicted:
```bash
# 1. Stop and remove volumes
docker-compose down -v

# 2. Launch fresh stack in background
docker-compose up --build -d

# 3. Wait for database and verify seed
docker-compose exec backend python manage.py wait_for_db
docker-compose exec backend python manage.py migrate
docker-compose exec backend python manage.py seed_data
```

### 3. Offline / Airplane Mode Guarantee (Zero Internet Required)
If venue Wi-Fi fails or Gemini LLM rate limits trigger:
```bash
# UdyamNiti automatically falls back to deterministic AST boolean rule evaluation,
# pre-ingested RAG policy chunks, and linguistic Gujlish lexicons.
# To force offline mode explicitly, leave GEMINI_API_KEY empty:
export GEMINI_API_KEY=""
```

### 4. Cache Purge (Clear Stale Strategy & Evidence Caches)
```bash
docker-compose exec redis redis-cli flushall
```

### 5. Instant Point-in-Time Database Backup / Export
```bash
docker-compose exec db pg_dump -U udyamniti udyamniti > pristine_demo_snapshot.sql
```

---

*Built with ❤️ for Indian MSMEs · UdyamNiti Platform*
