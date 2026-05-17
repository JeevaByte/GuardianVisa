# GuardianVisa — Agent Internal Tool-Call Flow

How the Vertex AI Agent Builder routes user intent to the correct tool chain, queries MongoDB via MCP, and produces a structured response.

```mermaid
flowchart TD
    %% ── Entry ───────────────────────────────────────────────────────────────────
    START(["📨 User Input Received\nvia FastAPI"])

    %% ── Intent classification ───────────────────────────────────────────────────
    IC["🤖 Gemini: Intent Classification\nextract_intent + extract_entities"]

    START --> IC

    %% ── Intent branches ─────────────────────────────────────────────────────────
    IC --> WH{"Work-Hours\nCheck?"}
    IC --> SD{"Scam\nDetection?"}
    IC --> EM{"Emergency\nCrisis?"}
    IC --> GQ{"General\nQuestion?"}

    %% ═══════════════════════════════════════════════════════════════════════════
    %% FLOW 1 — Visa work-hour violation
    %% ═══════════════════════════════════════════════════════════════════════════
    WH -->|"yes"| F1A["🔧 Tool: get_student_profile(student_id)\n→ MongoDB MCP → students collection"]
    F1A --> F1B["🔧 Tool: check_visa_hours(current, proposed, limit)\n→ MongoDB MCP → visa_rules collection"]
    F1B --> F1C{"total > limit?"}
    F1C -->|"VIOLATION"| F1D["🤖 Gemini: reason violation\n+ calculate overage hours"]
    F1C -->|"SAFE"| F1E["🤖 Gemini: confirm safe\n+ remaining weekly headroom"]
    F1D --> F1F["🔧 Tool: draft_safe_response(HIGH)\n→ Gemini: polite employer decline"]
    F1E --> F1G["🤖 Gemini: draft acceptance confirmation"]
    F1F --> OUT1(["📤 RISK_ALERT JSON\nstatus | severity | overage\nsafe_reply | action"])
    F1G --> OUT1

    %% ═══════════════════════════════════════════════════════════════════════════
    %% FLOW 2 — Scam detection
    %% ═══════════════════════════════════════════════════════════════════════════
    SD -->|"yes"| F2A["🤖 Gemini: extract_keywords(listing_text)"]
    F2A --> F2B["🔧 Tool: scan_scam_signals(keywords[])\n→ MongoDB MCP → scam_patterns collection\n$in query on keywords array"]
    F2B --> F2C["🤖 Gemini: analyse_scam_severity\n(listing + matched patterns)"]
    F2C --> F2D{"Risk\nLevel?"}
    F2D -->|"DANGER / HIGH"| F2E["Build red_flags[] + safe_actions[]\nconfidence score ≥ 0.75"]
    F2D -->|"MEDIUM"| F2F["Build caution_flags[] + safe_actions[]\nconfidence score 0.40–0.74"]
    F2D -->|"LOW"| F2G["Standard checks note\nconfidence score < 0.40"]
    F2E --> OUT2(["📤 SCAM_SCORE JSON\nrisk_level | confidence\nred_flags[] | safe_actions[]"])
    F2F --> OUT2
    F2G --> OUT2

    %% ═══════════════════════════════════════════════════════════════════════════
    %% FLOW 3 — Emergency plan
    %% ═══════════════════════════════════════════════════════════════════════════
    EM -->|"yes"| F3A["🔧 Tool: get_student_profile(student_id)\n→ MongoDB MCP → students collection\nreturns city, visa_expiry, university"]
    F3A --> F3B["🤖 Gemini: assess_visa_risk\n(days to expiry, trigger type)"]
    F3B --> F3C["🔧 Tool: get_emergency_resources(city)\n→ MongoDB MCP → emergency_resources\n$in query on eligibility"]
    F3C --> F3D["🤖 Gemini: create_emergency_plan\n(profile + resources + trigger)"]
    F3D --> F3E["🔧 Tool: draft_safe_response(email)\n→ Gemini: draft ISS support email"]
    F3E --> OUT3(["📤 EMERGENCY_PLAN JSON\nseven_day_plan[] | resources[]\ndraft_email | immediate_actions[]"])

    %% ═══════════════════════════════════════════════════════════════════════════
    %% FLOW 4 — General question (no tools)
    %% ═══════════════════════════════════════════════════════════════════════════
    GQ -->|"yes"| F4A["🤖 Gemini: direct reasoning\n(no tool call needed)"]
    F4A --> OUT4(["📤 GENERAL_RESPONSE JSON\nanswer | follow_up_suggestions[]"])

    %% ── Response merge ───────────────────────────────────────────────────────────
    OUT1 --> RESP["FastAPI serialises response\n→ React Frontend"]
    OUT2 --> RESP
    OUT3 --> RESP
    OUT4 --> RESP

    %% ── Styling ──────────────────────────────────────────────────────────────────
    classDef startEnd fill:#1565C0,stroke:#0D47A1,color:#fff,rx:20
    classDef gemini   fill:#7C4DFF,stroke:#4527A0,color:#fff
    classDef tool     fill:#FF6F00,stroke:#E65100,color:#fff
    classDef decision fill:#00897B,stroke:#00695C,color:#fff
    classDef output   fill:#2E7D32,stroke:#1B5E20,color:#fff,rx:16
    classDef merge    fill:#37474F,stroke:#263238,color:#fff

    class START,RESP startEnd
    class IC,F1D,F1E,F1G,F2A,F2C,F3B,F3D,F4A gemini
    class F1A,F1B,F1F,F2B,F3A,F3C,F3E tool
    class WH,SD,EM,GQ,F1C,F2D decision
    class OUT1,OUT2,OUT3,OUT4 output
    class RESP merge
```

## Key Insights

| Component | Colour | Role |
|-----------|--------|------|
| **Purple nodes** | Gemini calls | All LLM reasoning is isolated to purple nodes — intent classification, severity analysis, plan generation, drafting |
| **Orange nodes** | Tool calls | All data access goes through MCP tool calls — keeps the agent stateless and database credentials out of the LLM |
| **Green decision diamonds** | Routing gates | Hard logical branches (total > limit?, risk level?) use deterministic rules, not LLM guesses |
| **Dark output nodes** | Typed JSON | Each flow produces a distinct, schema-validated JSON type — prevents frontend from handling ambiguous responses |
| **Flow 4 (no tools)** | Direct Gemini path | Simple visa FAQs skip MongoDB entirely — cost-efficient for common "what is Tier-4?" questions |

> **Design principle:** LLMs reason; tools fetch. The agent never asks Gemini to recall visa rules from training data — it always fetches authoritative values from MongoDB, then asks Gemini to reason about them.
