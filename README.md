# 🛡️ GuardianVisa

### *Not a chatbot. A guardian.*

> **Protecting international students from visa violations, financial scams, and deportation crises — before it's too late.**

[![Google Cloud](https://img.shields.io/badge/Google%20Cloud-4285F4?style=for-the-badge&logo=googlecloud&logoColor=white)](https://cloud.google.com)
[![Gemini](https://img.shields.io/badge/Gemini%20AI-8E75B2?style=for-the-badge&logo=google&logoColor=white)](https://deepmind.google/technologies/gemini/)
[![MongoDB](https://img.shields.io/badge/MongoDB-47A248?style=for-the-badge&logo=mongodb&logoColor=white)](https://mongodb.com)
[![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-61DAFB?style=for-the-badge&logo=react&logoColor=black)](https://react.dev)
[![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)](https://opensource.org/licenses/MIT)
[![OSI Approved](https://img.shields.io/badge/OSI-Approved%20License-blue?style=for-the-badge&logo=opensourceinitiative&logoColor=white)](https://opensource.org/licenses/MIT)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg?style=for-the-badge)](CONTRIBUTING.md)
[![Contributor Covenant](https://img.shields.io/badge/Contributor%20Covenant-2.1-4baaaa.svg?style=for-the-badge)](CODE_OF_CONDUCT.md)

---

## 💔 Real Students. Real Risk. Real Protection.

These are the students GuardianVisa was built for.

| # | Name | Country | Visa | Situation |
|---|------|---------|------|-----------|
| 1 | **Ananya Krishnan** | 🇮🇳 India | F-1 | Data Science master's student who unknowingly exceeded work hours during an unpaid internship |
| 2 | **Lucas Ferreira** | 🇧🇷 Brazil | J-1 | Exchange student targeted by a fraudulent "urgent visa renewal" text message |
| 3 | **Hana Yoshida** | 🇯🇵 Japan | F-1 | Biology PhD candidate whose advisor is pushing her to defer, risking her status timeline |
| 4 | **Omar Khalil** | 🇯🇴 Jordan | F-1 | Electrical engineering student who received a suspicious recruiter email offering cash jobs |
| 5 | **Ngozi Okonkwo** | 🇳🇬 Nigeria | M-1 | Culinary arts student unsure whether switching schools will violate her M-1 conditions |
| 6 | **Zhang Wei** | 🇨🇳 China | F-1 | Finance MBA student whose SEVIS record was incorrectly terminated by an admin error |
| 7 | **Isabella Romero** | 🇨🇴 Colombia | J-2 | Spouse on J-2 who wants to start a side business but doesn't know if it's allowed |
| 8 | **Vikram Reddy** | 🇮🇳 India | OPT | Software engineer on OPT who received a job offer from a company not registered with E-Verify |
| 9 | **Amira Benali** | 🇩🇿 Algeria | F-1 | Pre-med student who lost her housing scholarship and faces potential enrolment gap |
| 10 | **Alexei Petrov** | 🇷🇺 Russia | F-1 | Aerospace PhD student whose funding was cut mid-semester with no guidance on next steps |

**GuardianVisa knows the risks they face. And it tells them first.**

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

## 🚀 Quick Start (Local)

**Prerequisites:** Python 3.11+, Node.js 18+, MongoDB running locally

```bash
# 1. Clone the repo
git clone https://github.com/JeevaByte/GuardianVisa.git
cd GuardianVisa

# 2. Set up environment variables
cp .env.example .env
# Edit .env and fill in: MONGODB_URI=mongodb://localhost:27017/guardianvisa, GEMINI_API_KEY
```

**Backend**
```bash
cd backend
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Seed the database
cd ../data && python seed_mongodb.py && cd ../backend

# Start the API server
uvicorn main:app --reload --port 8000
```

**Frontend** *(open a new terminal)*
```bash
cd frontend
npm install
npm run dev
```

| Service  | URL                        |
|----------|----------------------------|
| Frontend | http://localhost:3000      |
| Backend  | http://localhost:8000      |
| API Docs | http://localhost:8000/docs |

> **Tip:** You can also run everything with Docker: `docker-compose up --build`

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
| AI Orchestration | Gemini 1.5 Pro (via API) · LangChain Agents |
| Backend | FastAPI · Python 3.11 |
| Database | MongoDB (local) |
| Frontend | React 18 · Vite · Tailwind CSS |
| Infra | Docker · docker-compose |
| Auth | JWT (demo mode: pre-seeded student profiles) |

---

## 📁 Project Structure

```
guardianvisa/
├── backend/          # FastAPI app + Gemini agent orchestration
├── frontend/         # React + Tailwind UI
├── data/             # MongoDB seed scripts + JSON fixtures
├── docs/             # Architecture diagrams + sequence flows
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

## 🤝 Contributing

We welcome contributions of all kinds — new visa rules, scam patterns, bug fixes, translations, and docs!

- 📖 Read the [Contributing Guide](CONTRIBUTING.md)
- 🐛 [Report a bug](../../issues/new?template=bug_report.md)
- 💡 [Request a feature](../../issues/new?template=feature_request.md)
- 🔒 [Report a security issue](SECURITY.md)
- 📜 [Code of Conduct](CODE_OF_CONDUCT.md)

---

## 📄 License

GuardianVisa is released under the **[MIT License](LICENSE)** — an [OSI-approved](https://opensource.org/licenses/MIT) open source license.

```
MIT License © 2026 GuardianVisa Contributors
```

You are free to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of this software. See [LICENSE](LICENSE) for the full text.
