# 🛡️ GuardianVisa

### *Not a chatbot. A guardian.*

> **Protecting international students from visa violations, financial scams, and deportation crises — before it's too late.**

[![Google Cloud](https://img.shields.io/badge/Google%20Cloud-4285F4?style=for-the-badge&logo=googlecloud&logoColor=white)](https://cloud.google.com)
[![Gemini](https://img.shields.io/badge/Gemini%20AI-8E75B2?style=for-the-badge&logo=google&logoColor=white)](https://deepmind.google/technologies/gemini/)
[![MongoDB](https://img.shields.io/badge/MongoDB-47A248?style=for-the-badge&logo=mongodb&logoColor=white)](https://mongodb.com)
[![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-61DAFB?style=for-the-badge&logo=react&logoColor=black)](https://react.dev)
[![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)

---

## 💔 Meet Priya

Priya is a Computer Science master's student on an F-1 visa. It's Week 9 of the semester and she just got laid off from her on-campus job. She doesn't know she has exactly **60 days** before she falls out of status. She doesn't know the "immigration consultant" who emailed her last night is running a scam that has already stolen $12,000 from three students in her building. She doesn't know that if she misses one form, her student visa — and her dream of staying in the U.S. — is gone.

**GuardianVisa knows. And it tells her first.**

---

## 🎬 Demo

![Demo](docs/demo_screenshots/demo.gif)

---

## ✨ Features

<table>
<tr>
<td align="center" width="33%">

### 🛂 Visa Guard
Real-time work-hour tracking against your specific visa type. Get a countdown — not a crisis — when you're approaching limits. Automated alerts before violations happen.

</td>
<td align="center" width="33%">

### 🔍 Scam Scanner
Paste any email, text, or "offer" and get an instant risk verdict. Our agent cross-references a live scam pattern database and explains exactly why something is suspicious.

</td>
<td align="center" width="33%">

### 🚨 Emergency Plan
Lost your job? Visa expired? Got an ICE notice? GuardianVisa generates a personalised, step-by-step emergency action plan in seconds — with real DSO contacts and legal resource links.

</td>
</tr>
</table>

---

## 🏗️ Architecture

GuardianVisa is built on a multi-agent orchestration pattern powered by **Google Cloud Vertex AI** and **Gemini**. A root orchestrator agent routes queries to three specialised sub-agents, each with their own tool set and MongoDB-backed knowledge base.

```
User Query
    │
    ▼
┌─────────────────────────────┐
│  Orchestrator Agent (Gemini) │
└──────┬──────────┬───────────┘
       │          │          │
  Visa Guard  Scam Scanner  Emergency
   Agent        Agent       Plan Agent
       │          │          │
       └──────────┴──────────┘
                  │
            MongoDB Atlas
         (Rules · Patterns · Resources)
```

📐 Full architecture diagram → [`docs/01_system_architecture.md`](docs/01_system_architecture.md)

---

## 🚀 Quick Start

```bash
# 1. Clone the repo
git clone https://github.com/your-org/guardianvisa.git
cd guardianvisa

# 2. Copy environment variables
cp .env.example .env
# Fill in GOOGLE_CLOUD_PROJECT, MONGODB_URI, GEMINI_API_KEY

# 3. Seed the database
cd data && python seed_mongodb.py && cd ..

# 4. Launch everything
docker-compose up --build
```

| Service  | URL                   |
|----------|-----------------------|
| Frontend | http://localhost:3000 |
| Backend  | http://localhost:8000 |
| API Docs | http://localhost:8000/docs |

---

## ⚙️ How It Works

### Flow 1 — Visa Hours Check
A student submits their current work hours. The **Visa Guard Agent** queries MongoDB for their visa type's ruleset, calculates remaining allowance, and returns a plain-English status with a risk level and recommended action.

### Flow 2 — Scam Detection
The student pastes a suspicious message. The **Scam Scanner Agent** tokenises key phrases, queries the scam-pattern collection for matches, scores risk using Gemini's reasoning, and returns a verdict card explaining every red flag found.

### Flow 3 — Emergency Plan Generation
The student describes their situation. The **Emergency Plan Agent** identifies the crisis type, retrieves relevant legal resources and DSO contacts from MongoDB, then uses Gemini to generate a personalised, prioritised action checklist.

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| AI Orchestration | Google Cloud Vertex AI · Gemini 1.5 Pro |
| Backend | FastAPI · Python 3.11 · LangChain Agents |
| Database | MongoDB Atlas (multi-collection) |
| Frontend | React 18 · Vite · Tailwind CSS |
| Infra | Docker · Google Cloud Run |
| Auth | JWT (demo mode: pre-seeded student profiles) |

---

## 📁 Project Structure

```
guardianvisa/
├── backend/          # FastAPI app + Gemini agent orchestration
├── frontend/         # React + Tailwind UI
├── data/             # MongoDB seed scripts + JSON fixtures
├── docs/             # Architecture diagrams + sequence flows
├── deploy/           # Cloud Run deployment configs
└── docker-compose.yml
```

---

## 🏆 Hackathon

Built for the **[Google Cloud Rapid Agent Hackathon](https://googlecloudmultiagents.devpost.com/)** — **MongoDB Track**.

> *Multi-agent systems. Real-world impact. Built in a weekend.*

---

## ⚠️ Disclaimer

GuardianVisa is an **educational risk-awareness tool**, not legal advice. All scenarios use simulated student data. Visa rules and scam patterns are illustrative. Always consult a licensed immigration attorney and your Designated School Official (DSO) for decisions affecting your immigration status.

---

## 📄 License

[MIT](LICENSE) © 2026 GuardianVisa Contributors
