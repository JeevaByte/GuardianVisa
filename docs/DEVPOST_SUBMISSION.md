# GuardianVisa — Devpost Submission

## Project Name
GuardianVisa

## Tagline
Not a chatbot. A guardian.

---

## The Problem

Priya is a 22-year-old Indian student studying Computer Science at the University of Manchester on a UK Tier 4 student visa. She works part-time at a café to pay her rent — she's allowed to work 20 hours per week during term time. One Thursday evening, her manager sends a WhatsApp message asking her to cover extra weekend shifts. Eight extra hours. "We're really short-staffed," he writes. Priya wants to help. She needs the money. And she has absolutely no idea that accepting would push her to 26 hours for the week — a direct violation of her visa conditions.

Priya doesn't violate her visa out of malice. She does it out of ignorance. And she is not alone.

**Over 600,000 international students** study in the UK. Millions more study across the US, Canada, Australia, and Europe. Every single one carries a visa with conditions attached — work-hour limits, permitted activities, reporting obligations — written in legalese, buried in a welcome pack they received on day one and haven't looked at since. Universities provide information, but they cannot be on call 24/7. Students cannot carry an immigration lawyer in their pocket.

The consequences of a visa violation are catastrophic. Deportation. A 10-year entry ban. A destroyed career before it has started. And these consequences fall disproportionately on students from the Global South — students who have sacrificed everything, whose families have taken on debt, who cannot afford to make a single mistake.

Beyond visa compliance, international students are uniquely vulnerable targets for exploitation:

- **Housing scams** prey on students searching for accommodation from overseas before they arrive. Fake listings, phantom landlords, and upfront cash payment demands cost students thousands of pounds.
- **Job scams** promise flexible work and then steal personal documents or National Insurance numbers.
- **Visa-fee scams** impersonate the Home Office, UKVI, or universities, collecting "processing fees" that disappear into untraceable accounts.

When a real emergency strikes — an unexpected visa expiry, a sudden job loss, a university withdrawal — students are left navigating a labyrinthine system alone, under extreme stress, often in a country where they have no family support network.

There is no intelligent, proactive system watching out for them. Until now.

---

## The Solution

GuardianVisa is a proactive AI agent that protects international students from visa violations, scams, and immigration emergencies — in real time, before harm occurs.

It is not a chatbot. It doesn't wait for students to ask the right questions. It acts.

### Three Protective Flows

**1. Visa Hours Guard**  
The student pastes any work-related message — a WhatsApp from their manager, a rota change, a shift swap request. GuardianVisa's agent calls MongoDB (via MongoDB MCP Server) to retrieve the student's current work hours and visa type, cross-references the applicable UKVI rules, and performs a real-time calculation. If the proposed hours would breach the limit, the student sees a RED RISK ALERT with the exact numbers, the legal consequence, and — critically — a ready-to-send safe response draft they can reply with immediately. No legal knowledge required. No panic. Just protection.

**2. Scam Scanner**  
The student pastes any suspicious message, email, job ad, or housing listing. GuardianVisa queries a curated database of scam patterns targeting international students and uses Gemini 1.5 Pro to score the text for red flags: below-market pricing, urgency tactics, cash-only payment demands, requests for documents, landlord unavailability. The result is a DANGER / WARNING / SAFE rating with specific flags highlighted and actionable advice. Students learn to recognise scams, not just avoid them once.

**3. Emergency Action Plan**  
When a student faces an immigration emergency — sudden job loss, unexpected visa expiry, a letter from the Home Office — they describe their situation in plain language. GuardianVisa generates a prioritised 7-day action plan with city-specific resources (university international office, UKCISA, NHS, food banks, free legal clinics), calculates how many days remain before any visa deadline, and drafts an email to the university International Office on the student's behalf.

### The Architecture

GuardianVisa is built on Google Cloud Agent Builder (Vertex AI Agents) with Gemini 1.5 Pro as the reasoning engine. The agent is equipped with custom tools — defined as FastAPI endpoints and registered as Vertex AI function-calling tools — that connect to MongoDB Atlas via the MongoDB MCP Server. This means the agent doesn't just generate text; it performs real database lookups, calculates real numbers, and makes real decisions.

The frontend is a React + Tailwind CSS single-page application deployed on Cloud Run. The backend is a FastAPI service, also on Cloud Run, behind a Docker container built by Cloud Build.

---

## Demo

🎬 **[YouTube Demo Video — link to be added]**

---

## Live App

🌐 **[Cloud Run URL — link to be added after deployment]**

---

## GitHub

https://github.com/JeevaByte/GuardianVisa

---

## Technologies Used

- **Google Cloud Agent Builder** (Vertex AI Agents) — orchestrates the agentic reasoning loop and function-calling
- **Gemini 1.5 Pro** — natural language understanding, risk assessment, plan generation
- **MongoDB Atlas** — persistent storage for student profiles, visa rules, scam patterns, emergency resources
- **MongoDB MCP Server** — exposes MongoDB collections as semantic tools accessible to the agent
- **Python 3.11 / FastAPI** — backend API server and agent tool implementations
- **React 18 + Tailwind CSS + Vite** — frontend single-page application
- **Google Cloud Run** — serverless container hosting for both frontend and backend
- **Google Cloud Build** — CI/CD pipeline from GitHub to Cloud Run
- **Docker / Docker Compose** — local development and container build

---

## How It Works

### The Agentic Loop

When a student submits a message, the request flows from the React frontend to the FastAPI backend. The backend instantiates a `GuardianVisaAgent` and calls the appropriate method (`check_visa_risk`, `scan_scam`, or `get_emergency_plan`).

The agent sends the query to Vertex AI with a set of registered tools. Gemini 1.5 Pro reasons about the query and decides which tools to call. The `tool_dispatcher.py` module receives tool call requests and routes them to the actual Python implementations in `tools.py`, which perform real MongoDB queries via `mongodb_client.py`.

For the visa check: the agent calls `get_student_profile` (retrieves current hours, visa type, university, term dates from MongoDB), then `get_visa_rules` (fetches the applicable UKVI rules for that visa tier), then `calculate_visa_risk` (performs the hours arithmetic and determines violation status), then `draft_employer_response` (generates the safe reply). All four tool calls happen within a single agentic loop — the agent decides the sequence, not hardcoded logic.

For the scam scanner: the agent calls `query_scam_patterns` (fetches matching patterns from MongoDB using semantic similarity), then applies Gemini's reasoning to score the input text against those patterns.

For the emergency plan: the agent calls `get_student_profile`, `query_emergency_resources` (fetches city-specific resources from MongoDB), and `calculate_visa_deadline` before generating the structured 7-day plan.

### MongoDB as Semantic Tool Access

MongoDB Atlas stores structured collections (`students`, `visa_rules`, `scam_patterns`, `emergency_resources`) seeded by `data/seed_mongodb.py`. The MongoDB MCP Server exposes these as semantic tools — meaning the agent can query them in natural language without needing to construct MongoDB query syntax directly. This is a fundamentally different pattern from traditional RAG: the agent treats the database as a tool, not a retrieval corpus.

---

## Challenges

**1. Making the agentic loop reliable**  
The hardest part of this project was not the individual tools — it was making the agent reliably orchestrate them in the right sequence. Early iterations had the agent skip tool calls and hallucinate results. We solved this through careful system-prompt engineering, explicit tool descriptions, and mandatory structured output schemas (Pydantic models) that force the agent to populate every required field via tool calls rather than inventing values.

**2. MongoDB MCP Server integration**  
Integrating MongoDB via the MCP (Model Context Protocol) Server required understanding a paradigm that is genuinely new — treating a database as an LLM-accessible tool rather than a traditional query target. Getting the tool schema definitions right, ensuring the agent understood the semantics of each tool, and handling partial or malformed tool responses took significant iteration.

**3. Real-time visa calculations under ambiguity**  
Visa rules are not simple lookup tables. Term dates vary by university. Part-time vs full-time status changes the rules. Some students are on placement years with different allowances. The agent had to be taught to ask clarifying questions when context was ambiguous rather than defaulting to a conservative or permissive answer — both of which carry real risk.

**4. Emotional safety in emergency responses**  
The emergency flow deals with students in genuine distress. Early responses were technically accurate but tonally clinical. We invested time in system-prompt design to ensure the agent leads with empathy, validates the student's feelings, and presents the action plan as achievable rather than overwhelming — while still containing all the legally important information.

**5. Zero-credential demo mode**  
For a hackathon, the project needed to be demonstrable by judges who would not have MongoDB Atlas credentials or a Vertex AI project. Building a robust mock mode that mirrors the real agent's behaviour — including realistic response structures, timing, and edge cases — required building the mock layer in parallel with the real implementation.

---

## Accomplishments

**The WOW moment is real.**  
When you type Priya's manager's WhatsApp message into GuardianVisa and a RED ALERT appears telling you *exactly* how many hours you are over, what the legal consequence is, and hands you a safe response to send back — the reaction is visceral. It is not a search result. It is not a FAQ page. It is a guardian that caught something you were about to do wrong and gave you a way out.

We are proud of the following:

- **A genuinely agentic architecture.** The visa check flow involves four sequential tool calls that the agent decides and orchestrates. This is not a prompt-and-response chatbot with a wrapper. Gemini is reasoning about what to retrieve and in what order.

- **MongoDB as a living knowledge base.** The scam patterns database is designed to be updateable — new scam types can be added without redeploying the application. The agent's behaviour improves as the data improves. This is a production-ready design, not a demo hack.

- **Emotional design.** We built for Priya — a specific, real human in a specific, vulnerable situation. Every word in the UI, every alert colour, every response tone was evaluated against that persona. The project has a soul.

- **Full-stack, cloud-native, production-ready.** The codebase is structured with separate frontend/backend containers, environment-based configuration, Docker Compose for local development, Cloud Build for CI/CD, and Cloud Run for production. A judge or investor could actually deploy this.

- **The tagline is true.** "Not a chatbot. A guardian." We mean it.

---

## Learnings

**MongoDB MCP changes how agents interact with data.** We came in expecting to use MongoDB as a traditional database — write queries, get documents, parse results. What we learned is that the MCP Server pattern inverts this: you define the *semantics* of what the database can provide, and the agent decides *when* and *how* to request it. The agent's intelligence is amplified because it can reason about *what* it needs rather than *how* to get it.

**Vertex AI function calling is more powerful than RAG for structured decisions.** Retrieval-Augmented Generation works well for open-ended Q&A. But for a task like "is this work schedule a visa violation?" — which requires precise data retrieval, arithmetic, and rule application — function calling with structured schemas produces dramatically more reliable and auditable results.

**Proactive AI requires a different design philosophy.** Most AI products are reactive: the user asks, the AI answers. GuardianVisa is different — it surfaces risk that the user doesn't know to ask about. Designing for this required thinking carefully about when to interrupt, how to frame urgency without causing panic, and how to give the user agency rather than just telling them what to do.

**The emotional dimension of technical tools is not optional.** When the stakes are a deportation, the difference between a technically correct answer and an emotionally intelligent one is not a nice-to-have. It is the product.

---

## What's Next

- **Real university API integration** — Connect to SITS/e:Vision student records systems to pull live term dates and enrolled hours, eliminating manual data entry
- **WhatsApp / SMS integration** — Students receive protection in the channels they already use, without opening a browser
- **Mobile application** — A native iOS/Android app with push notifications for proactive visa deadline reminders
- **Expanded visa coverage** — US F-1/OPT, Canadian Study Permit, Australian Student Visa, Schengen rules
- **Multi-country scam database** — Region-specific scam patterns for each major student destination country
- **University dashboard** — An institutional interface for international offices to monitor risk signals across their student population (with appropriate privacy controls)
- **Legal partner integrations** — Direct referral to immigration lawyers and student union advisors for complex cases

---

## Track

**MongoDB Track**

GuardianVisa uses MongoDB Atlas as the persistent knowledge base for student profiles, visa rules, scam patterns, and emergency resources. The MongoDB MCP Server is used to expose these collections as semantic tools accessible to the Vertex AI agent, enabling a novel pattern where the LLM treats the database as an intelligent tool rather than a query target. The project demonstrates MongoDB's capability as the backbone of a production-ready, agentic AI system operating in a high-stakes domain.
