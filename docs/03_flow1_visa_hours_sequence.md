# GuardianVisa — Flow 1: Visa Work-Hour Violation Check

Step-by-step sequence when a student pastes a manager's message asking them to work extra hours.

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

    %% ── Step 1: User input ──────────────────────────────────────────────────────
    User  ->>  FE  : Pastes manager message into ChatInterface<br/>"Can you work an extra 8 hrs this week?"
    Note over FE   : Extracts session student_id from auth token

    %% ── Step 2: Frontend → Backend ─────────────────────────────────────────────
    FE    ->>  API : POST /api/check<br/>{ message, student_id }

    %% ── Step 3: Backend → Agent ─────────────────────────────────────────────────
    API   ->>  AB  : invoke_agent(message, student_id)

    %% ── Step 4: Fetch student profile ───────────────────────────────────────────
    AB    ->>  MCP : tool: get_student_profile(student_id)
    MCP   ->>  DB  : db.students.findOne({ _id: student_id })
    DB    -->> MCP : { visa_type:"Tier-4", work_hours_this_week:18,<br/>work_limit_term:20, visa_expiry:"2025-09-30" }
    MCP   -->> AB  : student profile object

    %% ── Step 5: Classify intent ─────────────────────────────────────────────────
    AB    ->>  GEM : classify_intent(message)
    GEM   -->> AB  : intent = "work_hours_check",<br/>proposed_hours = 8

    %% ── Step 6: Check hours ─────────────────────────────────────────────────────
    AB    ->>  MCP : tool: check_visa_hours(current=18, proposed=8, limit=20)
    MCP   ->>  DB  : db.visa_rules.findOne({ visa_type:"Tier-4" })
    DB    -->> MCP : { term_work_limit_hours:20,<br/>violation_consequence:"visa curtailment" }
    MCP   -->> AB  : { total_if_accepted:26, limit:20,<br/>overage:6, status:"VIOLATION" }

    %% ── Step 7: Gemini reasons ──────────────────────────────────────────────────
    AB    ->>  GEM : reason({ current:18, proposed:8,<br/>limit:20, total:26, consequence:"curtailment" })
    GEM   -->> AB  : "18 + 8 = 26 hours → exceeds 20-hr Tier-4 limit by 6 hrs.<br/>Risk: VISA CURTAILMENT. Severity: HIGH"

    %% ── Alt block: VIOLATION vs SAFE ────────────────────────────────────────────
    alt total_hours > limit  [VIOLATION]
        AB    ->>  MCP : tool: get_student_profile(student_id)<br/>[already cached — fetch decline template]
        AB    ->>  GEM : tool: draft_safe_response(situation="work_violation",<br/>risk_level="HIGH", consequence="curtailment")
        GEM   -->> AB  : "Hi [Manager], thank you for thinking of me.<br/>Unfortunately I'm unable to take on additional hours<br/>this week due to my visa conditions. I can help in other<br/>ways — happy to discuss."
        AB    -->> API : { status:"VIOLATION", severity:"HIGH",<br/>current_hours:18, proposed_hours:8,<br/>total_if_accepted:26, limit:20, overage:6,<br/>consequence:"visa curtailment",<br/>safe_reply:"Hi [Manager]...",<br/>action:"DECLINE_SHIFT" }
    else total_hours ≤ limit  [SAFE]
        AB    ->>  GEM : tool: draft_safe_response(situation="work_safe",<br/>risk_level="LOW")
        GEM   -->> AB  : Confirmation message — hours are within limits
        AB    -->> API : { status:"SAFE", severity:"LOW",<br/>current_hours:18, proposed_hours:2,<br/>total_if_accepted:20, limit:20,<br/>action:"ACCEPT_SHIFT" }
    end

    %% ── Step 8: Response chain ──────────────────────────────────────────────────
    API   -->> FE  : Structured JSON response
    FE    -->> User : Renders RiskAlert component<br/>🔴 HIGH RISK — Visa Violation Detected<br/>+ copy-paste safe reply for manager
```

## Key Insights

| Step | What Happens | Why It Matters |
|------|-------------|----------------|
| **Profile fetch** | Agent retrieves `work_hours_this_week` and `work_limit_term` in one MCP call | Eliminates need for client to send sensitive visa data in every request |
| **Intent classification** | Gemini extracts `proposed_hours = 8` from natural-language text | Handles informal phrasing like "a couple of extra shifts" |
| **Hour arithmetic** | MCP tool performs `current + proposed vs limit` deterministically | Keeps critical business logic out of the LLM; Gemini only reasons about consequences |
| **`alt` block** | Two branches: VIOLATION (total > limit) and SAFE (total ≤ limit) | The UI renders a red `RiskAlert` for violations, green confirmation for safe scenarios |
| **`draft_safe_response`** | Gemini generates a polite, legally-safe decline message | Student doesn't have to explain visa rules to their employer — the agent does it diplomatically |
| **Structured JSON** | Agent returns typed fields: `status`, `severity`, `overage`, `safe_reply` | Frontend components bind directly to fields without parsing free-form text |
