# GuardianVisa — Cloud Run Deployment Guide

## Prerequisites

- [Google Cloud SDK](https://cloud.google.com/sdk/docs/install) (`gcloud` CLI)
- Docker (for local testing)
- A [MongoDB Atlas](https://www.mongodb.com/atlas) account with a cluster and connection URI
- A GCP project with the following APIs enabled:
  - Cloud Build API
  - Cloud Run API
  - Container Registry API

---

## 1. Set Environment Variables

```bash
export PROJECT_ID=your-gcp-project-id
export MONGODB_URI="mongodb+srv://user:password@cluster.mongodb.net/guardianvisa"

gcloud config set project $PROJECT_ID
```

---

## 2. Enable Required APIs

```bash
gcloud services enable \
  cloudbuild.googleapis.com \
  run.googleapis.com \
  containerregistry.googleapis.com
```

---

## 3. Submit Cloud Build

Run from the **project root**:

```bash
gcloud builds submit . \
  --config=deploy/cloudbuild.yaml \
  --substitutions=_MONGODB_URI="$MONGODB_URI",_GCP_PROJECT_ID="$PROJECT_ID"
```

This will:
1. Build the backend and frontend Docker images
2. Push them to Google Container Registry
3. Deploy both services to Cloud Run in `us-central1`

---

## 4. Set Additional Cloud Run Environment Variables (if needed)

```bash
gcloud run services update guardianvisa-backend \
  --region=us-central1 \
  --set-env-vars="MONGODB_URI=$MONGODB_URI"
```

---

## 5. Get Service URLs

```bash
# Backend URL
gcloud run services describe guardianvisa-backend \
  --region=us-central1 \
  --format="value(status.url)"

# Frontend URL
gcloud run services describe guardianvisa-frontend \
  --region=us-central1 \
  --format="value(status.url)"
```

---

## Local Docker Testing

```bash
# Backend
docker build -t guardianvisa-backend ./backend
docker run -p 8080:8080 -e MONGODB_URI="$MONGODB_URI" guardianvisa-backend

# Frontend
docker build -t guardianvisa-frontend ./frontend
docker run -p 8080:80 guardianvisa-frontend
```
