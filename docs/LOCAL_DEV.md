# GuardianVisa — Local Development Guide

## Prerequisites

| Tool | Version | Purpose |
|------|---------|---------|
| Python | 3.11+ | Backend (FastAPI + Vertex AI SDK) |
| Node.js | 20+ | Frontend (React + Vite) |
| Docker Desktop | Latest | Optional docker-compose path |
| MongoDB Atlas | Free tier | Student data, visa rules, scam patterns |
| Google Cloud | Free trial / account | Vertex AI Agents, Gemini 1.5 Pro, Cloud Run |

### Verify your tools
```bash
python3 --version   # should print 3.11.x or higher
node --version      # should print v20.x.x or higher
docker --version    # optional
```

---

## Quick Start (without Docker)

```bash
# 1. Clone and enter the repo
git clone https://github.com/JeevaByte/GuardianVisa.git
cd GuardianVisa

# 2. Create your local .env file
make setup-env
# Opens: backend/.env — fill in your credentials (see below)

# 3. Install all dependencies (Python + Node)
make install

# 4. Seed MongoDB with demo data
make seed

# 5. Validate your setup (MongoDB + GCP connectivity)
make validate

# 6. Start the backend  [Terminal 1]
make dev-backend

# 7. Start the frontend [Terminal 2]
make dev-frontend

# 8. Open in browser
open http://localhost:5173
```

### backend/.env reference

```dotenv
MONGODB_URI=mongodb+srv://<user>:<password>@<cluster>.mongodb.net/guardianvisa
GCP_PROJECT_ID=your-gcp-project-id
GCP_LOCATION=us-central1
AGENT_ID=your-vertex-agent-id
GEMINI_MODEL=gemini-1.5-pro

# Optional — force mock responses without any cloud credentials
MOCK_MODE=false
```

Use `make check-env` at any time to verify no placeholder values remain.

---

## Quick Start (with Docker)

```bash
make setup-env
# Edit backend/.env with your credentials

make docker-up
# Backend:  http://localhost:8000
# Frontend: http://localhost:3000
```

To stop:
```bash
make docker-down
```

---

## API Endpoints

The FastAPI backend runs on `http://localhost:8000`. Interactive docs:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc:       `http://localhost:8000/redoc`

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/api/check` | Visa hours risk check |
| `POST` | `/api/scan-scam` | Scam detection |
| `POST` | `/api/emergency` | 7-day emergency plan |
| `GET`  | `/api/student/{id}` | Student profile lookup |
| `GET`  | `/health` | Liveness probe |

---

## Testing the 3 Demo Flows

### Flow 1 — Visa Hours Guard

1. Select the **"Visa Guard"** tab
2. Paste the following message into the input box:

   > "Hi Priya, can you cover extra weekend shifts this Saturday and Sunday? About 4 hours each day so 8 hours total. We're really short-staffed!"

3. **Expected result:**  
   🔴 **RED RISK ALERT** — Current 18 hrs + proposed 8 hrs = 26 hrs, which violates the Tier 4 student visa 20 hrs/week limit during term time.  
   The agent also generates a safe employer-response draft that Priya can send without risking her visa.

---

### Flow 2 — Scam Scanner

1. Select the **"Scam Scanner"** tab
2. Paste the following listing:

   > "Beautiful 2-bed flat in Manchester city centre, only £400/month! I'm currently overseas so can't show the property. Please send 3 months rent in cash upfront to secure it. Decision needed today!"

3. **Expected result:**  
   🚨 **DANGER** scam score — 3+ red flags detected:
   - Suspiciously below-market rent
   - Landlord unavailable to show property
   - Cash-only upfront payment demanded
   - Artificial urgency ("decision needed today")

---

### Flow 3 — Emergency Action Plan

1. Select the **"Emergency Plan"** tab
2. Type:

   > "I just lost my job at the café. I don't know what to do."

3. **Expected result:**  
   📋 **7-day action plan** with Manchester-specific resources including university international student support, UKCISA helpline, food banks, and a draft email to the university International Office.

---

## Mock Mode (No Credentials Needed)

The backend automatically activates **mock mode** when `GCP_PROJECT_ID` is not set or left as a placeholder. All three flows return realistic pre-canned responses based on the Priya scenario — perfect for demoing without cloud credentials.

To force mock mode regardless of env vars:

```dotenv
# backend/.env
MOCK_MODE=true
```

Mock mode is indicated in the response headers (`X-Mock-Mode: true`) and logged at startup.

---

## Makefile Reference

```
make help            Print all targets with descriptions
make setup-env       Copy backend/.env.example → backend/.env
make check-env       Verify no placeholder values remain in .env
make install         pip install + npm install
make seed            Seed MongoDB with demo data
make validate        Run full pre-flight check (MongoDB + GCP)
make dev-backend     Start FastAPI with hot-reload (port 8000)
make dev-frontend    Start Vite dev server (port 5173)
make build-frontend  Production build → frontend/dist
make docker-up       docker-compose up --build
make docker-down     docker-compose down
make deploy          gcloud builds submit (Cloud Build)
make logs-backend    Stream Cloud Run backend logs
make logs-frontend   Stream Cloud Run frontend logs
make clean           Remove dist/, node_modules, __pycache__
```

---

## Troubleshooting

| Symptom | Fix |
|---------|-----|
| `MongoServerError: bad auth` | Check MONGODB_URI in backend/.env — user/password must be URL-encoded |
| `DefaultCredentialsError` from GCP | Run `gcloud auth application-default login` or set `MOCK_MODE=true` |
| Frontend shows "Failed to fetch" | Confirm backend is running on port 8000 and CORS is unrestricted |
| `uvicorn: command not found` | Run `make install` to install Python dependencies |
| Port 8000 already in use | `lsof -ti:8000 \| xargs kill` then retry |
| MongoDB Atlas IP not whitelisted | Add `0.0.0.0/0` to Atlas Network Access for development |
