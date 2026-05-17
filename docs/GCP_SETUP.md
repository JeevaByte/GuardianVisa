# GCP Setup Guide — GuardianVisa

Complete step-by-step guide to provision GCP infrastructure for the GuardianVisa hackathon project.

---

## Section 1: Create GCP Project

```bash
# Install gcloud CLI first: https://cloud.google.com/sdk/docs/install
gcloud auth login
gcloud projects create guardianvisa-hackathon --name="GuardianVisa"
gcloud config set project guardianvisa-hackathon
```

> **Enable billing (required for Vertex AI)**
> Go to: https://console.cloud.google.com/billing
> Link a billing account to `guardianvisa-hackathon`

---

## Section 2: Enable Required APIs

```bash
gcloud services enable \
  aiplatform.googleapis.com \
  dialogflow.googleapis.com \
  cloudbuild.googleapis.com \
  run.googleapis.com \
  containerregistry.googleapis.com \
  secretmanager.googleapis.com
```

---

## Section 3: Create Service Account

```bash
gcloud iam service-accounts create guardianvisa-sa \
  --display-name="GuardianVisa Service Account"

gcloud projects add-iam-policy-binding guardianvisa-hackathon \
  --member="serviceAccount:guardianvisa-sa@guardianvisa-hackathon.iam.gserviceaccount.com" \
  --role="roles/aiplatform.user"

gcloud projects add-iam-policy-binding guardianvisa-hackathon \
  --member="serviceAccount:guardianvisa-sa@guardianvisa-hackathon.iam.gserviceaccount.com" \
  --role="roles/run.invoker"

# Download key for local development
gcloud iam service-accounts keys create backend/service-account.json \
  --iam-account=guardianvisa-sa@guardianvisa-hackathon.iam.gserviceaccount.com
```

> ⚠️ **Never commit `backend/service-account.json` to version control.**
> Ensure it is listed in `.gitignore`.

---

## Section 4: Set Up Vertex AI Agent Builder (Web UI Steps)

1. Go to https://console.cloud.google.com/gen-app-builder
2. Click **"New App"** → **"Agent"** → **"Create"**
3. **App name:** `guardianvisa-agent`
4. **Region:** `us-central1`
5. Click **"Create"**
6. In the agent console, note the **Agent ID** (format: `xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx`)

---

## Section 5: Configure Agent Tools in UI

For each tool, click **"Tools"** → **"Add Tool"**:

### Tool 1: `get_student_profile`
- **Name:** `get_student_profile`
- **Description:** "Retrieves a student's visa profile and work hours"
- **Type:** OpenAPI
- **Schema:** Paste the schema from the `get_student_profile` docstring in `backend/tools.py`

### Tool 2: `check_visa_hours`
- **Name:** `check_visa_hours`
- **Description:** "Checks whether a student has exceeded allowed work hours"
- **Type:** OpenAPI
- **Schema:** Paste the schema from `backend/tools.py`

### Tools 3–5
Repeat the same process for the remaining tools defined in `backend/tools.py`.

---

## Section 6: Configure Environment

Add the following variables to `backend/.env`:

```bash
GCP_PROJECT_ID=guardianvisa-hackathon
GCP_LOCATION=us-central1
AGENT_ID=your-agent-id-here
GOOGLE_APPLICATION_CREDENTIALS=service-account.json
GEMINI_MODEL=gemini-1.5-pro
```

---

## Section 7: Test Vertex AI Connection

```bash
python scripts/validate_gcp.py
```

A passing run will print:
```
✅ GCP ready!
```

---

## Section 8: Deploy to Cloud Run

```bash
# Authenticate Docker with GCR
gcloud auth configure-docker

# Submit build
gcloud builds submit . \
  --config=deploy/cloudbuild.yaml \
  --substitutions=_MONGODB_URI="$(grep MONGODB_URI backend/.env | cut -d= -f2-)",_GCP_PROJECT_ID=guardianvisa-hackathon

# List deployed services and their URLs
gcloud run services list --region=us-central1
```

---

## Section 9: Set Cloud Run Secrets

```bash
# Store MongoDB URI as a Secret Manager secret
echo -n "your-mongodb-uri" | gcloud secrets create MONGODB_URI --data-file=-

# Grant the service account access to read the secret
gcloud secrets add-iam-policy-binding MONGODB_URI \
  --member="serviceAccount:guardianvisa-sa@guardianvisa-hackathon.iam.gserviceaccount.com" \
  --role="roles/secretmanager.secretAccessor"
```

---

## Troubleshooting

| Error | Fix |
|---|---|
| `PERMISSION_DENIED` | Re-run the IAM binding commands in Section 3 |
| `Model not found` | Ensure `aiplatform.googleapis.com` is enabled in the correct project (`gcloud config get project`) |
| `Container failed to start` | Check Cloud Run logs: `gcloud run logs read --service guardianvisa-backend` |
| `Credentials file not found` | Verify `GOOGLE_APPLICATION_CREDENTIALS` path is relative to the working directory where you launch the app |
| `Billing not enabled` | Visit https://console.cloud.google.com/billing and link an account to `guardianvisa-hackathon` |
