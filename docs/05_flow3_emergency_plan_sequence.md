# GuardianVisa — Flow 3: Emergency Survival Plan

Step-by-step sequence when a student reports sudden job loss or financial crisis.

```mermaid
sequenceDiagram
    %% ── Participants ────────────────────────────────────────────────────────────
    actor       User         as 🧑‍🎓 Student
    participant FE           as React Frontend
    participant API          as FastAPI Backend
    participant AB           as Agent Builder<br/>(Vertex AI)
    participant GEM          as Gemini 1.5 Pro
    participant MCP          as MongoDB MCP Server
    participant DB           as MongoDB Atlas

    %% ── Step 1: User reports crisis ─────────────────────────────────────────────
    User  ->>  FE  : Types in ChatInterface:<br/>"I just lost my job. I don't know what to do."

    %% ── Step 2: Frontend → Backend ─────────────────────────────────────────────
    FE    ->>  API : POST /api/emergency<br/>{ message, student_id }
    Note over API  : Sets request timeout to 30s (plan generation is longer)

    %% ── Step 3: Backend → Agent ─────────────────────────────────────────────────
    API   ->>  AB  : invoke_agent("emergency", message, student_id)

    %% ── Step 4: Intent confirmation ─────────────────────────────────────────────
    AB    ->>  GEM : classify_intent(message)
    GEM   -->> AB  : intent = "emergency_financial_crisis",<br/>trigger = "job_loss"

    %% ── Step 5: Fetch student profile ───────────────────────────────────────────
    AB    ->>  MCP : tool: get_student_profile(student_id)
    MCP   ->>  DB  : db.students.findOne({ _id: student_id })
    DB    -->> MCP : { name:"Priya", university:"Uni of Manchester",<br/>visa_type:"Tier-4", visa_expiry:"2025-09-30",<br/>city:"Manchester", course:"MSc Data Science",<br/>work_hours_this_week:0, email:"priya@student.ac.uk" }
    MCP   -->> AB  : student profile

    %% ── Step 6: Calculate visa urgency ──────────────────────────────────────────
    AB    ->>  GEM : assess_visa_risk(visa_expiry="2025-09-30", today="2025-06-07")
    GEM   -->> AB  : { days_remaining: 115, risk: "MODERATE",<br/>note: "Must maintain enrollment; job loss does not<br/>directly invalidate Tier-4 but financial hardship<br/>may affect tuition payments" }

    %% ── Step 7: Fetch local resources ───────────────────────────────────────────
    AB    ->>  MCP : tool: get_emergency_resources(city="Manchester")
    MCP   ->>  DB  : db.emergency_resources.find({<br/>  city: "Manchester",<br/>  eligibility: { $in: ["international_student","all"] }<br/>})
    DB    -->> MCP : [<br/>  { type:"hardship_fund", name:"UoM Emergency Fund",<br/>    contact:"hardship@manchester.ac.uk",<br/>    url:"https://www.manchester.ac.uk/hardship" },<br/>  { type:"food_bank", name:"Manchester Central Foodbank",<br/>    contact:"0161-832-1234", eligibility:"all" },<br/>  { type:"legal_aid", name:"ISAS Immigration Advice",<br/>    contact:"isas@manchester.ac.uk" },<br/>  { type:"counselling", name:"Student Wellbeing",<br/>    contact:"wellbeing@manchester.ac.uk" }<br/>]
    MCP   -->> AB  : 4 local resources

    %% ── Step 8: Generate 7-day plan ─────────────────────────────────────────────
    AB    ->>  GEM : create_emergency_plan(profile, resources, trigger="job_loss")
    GEM   -->> AB  : 7-day action plan:<br/>Day 1 — Notify International Student Support<br/>Day 1 — Apply to UoM Emergency Hardship Fund<br/>Day 2 — Register with Manchester Central Foodbank<br/>Day 3 — Contact ISAS re: visa implications<br/>Day 4 — Update CV & register with JobsBoard<br/>Day 5 — Attend Wellbeing drop-in session<br/>Day 7 — Follow-up on hardship fund application

    %% ── Step 9: Draft support email ─────────────────────────────────────────────
    AB    ->>  GEM : tool: draft_safe_response(situation="job_loss_email",<br/>recipient="International Student Support",<br/>student=profile, resources=resources)
    GEM   -->> AB  : Draft email:<br/>"Dear International Student Support Team,<br/>My name is Priya, MSc Data Science student (ID: ...). I am writing<br/>to inform you that I have recently lost my part-time employment<br/>and am experiencing financial hardship. I would appreciate<br/>guidance on available support options including the Emergency<br/>Hardship Fund. Kind regards, Priya"

    %% ── Step 10: Final response ──────────────────────────────────────────────────
    AB    -->> API : EmergencyPlan JSON {<br/>  trigger: "job_loss",<br/>  visa_risk: { level:"MODERATE", days_remaining:115 },<br/>  seven_day_plan: [ ...7 action items... ],<br/>  resources: [ ...4 local resources... ],<br/>  draft_email: "Dear International Student Support...",<br/>  immediate_actions: ["Do NOT take extra paid work to compensate",<br/>    "Contact university BEFORE missing tuition payment"]<br/>}
    API   -->> FE  : EmergencyPlan JSON
    FE    -->> User : Renders EmergencyCard component:<br/>📋 7-Day Survival Plan<br/>🏦 Local Resources (clickable links)<br/>✉️ Copy-paste email to ISS
```

## Key Insights

| Step | What Happens | Why It Matters |
|------|-------------|----------------|
| **Profile retrieval** | Agent pulls `visa_expiry`, `university`, `city` in one call | Personalises the plan — a London student gets London food banks, not Manchester ones |
| **Visa risk assessment** | Gemini calculates `days_remaining` and flags financial→visa cascade risk | Job loss → missed tuition → visa curtailment is a real, common student crisis chain |
| **`get_emergency_resources`** | MongoDB `$in` query filters by city AND eligibility | Returns only resources the student qualifies for — avoids sending them to domestic-only services |
| **7-day structure** | Gemini generates time-boxed daily tasks | Prevents paralysis — students in crisis need concrete, ordered next steps |
| **`draft_safe_response`** | Pre-written email to International Student Support | Students often don't know what to say; a drafted email removes the activation energy barrier |
| **`immediate_actions` field** | Warns against dangerous workarounds (e.g. illegal extra work) | Critical: financial panic can lead students to unknowingly violate visa conditions |
| **EmergencyCard UI** | All three outputs rendered as distinct cards | Separates "what to do" (plan), "who to call" (resources), and "what to write" (email) |
