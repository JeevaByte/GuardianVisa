# GuardianVisa — Flow 2: Accommodation Scam Detection

Step-by-step sequence when a student pastes a rental listing to check for red flags.

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

    %% ── Step 1: User pastes listing ─────────────────────────────────────────────
    User  ->>  FE  : Pastes rental listing text into ScamScanner input<br/>"2BR flat £400/month. Pay 3 months upfront cash.<br/>No viewings — landlord abroad. WhatsApp only."

    %% ── Step 2: Frontend → Backend ─────────────────────────────────────────────
    FE    ->>  API : POST /api/scan-scam<br/>{ listing_text, student_id }
    Note over API  : Sanitises & truncates text to 4096 chars

    %% ── Step 3: Backend → Agent ─────────────────────────────────────────────────
    API   ->>  AB  : invoke_agent("scam_scan", listing_text, student_id)

    %% ── Step 4: Extract keywords for DB lookup ──────────────────────────────────
    AB    ->>  GEM : extract_keywords(listing_text)
    GEM   -->> AB  : ["cash", "upfront", "no viewing", "abroad",<br/>"whatsapp", "3 months deposit", "urgent"]

    %% ── Step 5: Pattern match against MongoDB ───────────────────────────────────
    AB    ->>  MCP : tool: scan_scam_signals(keywords=[...])
    MCP   ->>  DB  : db.scam_patterns.find({<br/>  keywords: { $in: ["cash","upfront","no viewing",<br/>  "abroad","whatsapp","3 months deposit","urgent"] }<br/>})
    DB    -->> MCP : [<br/>  { pattern:"cash_only_upfront", risk_level:"DANGER",<br/>    advice:"Never pay before viewing." },<br/>  { pattern:"no_viewing_allowed", risk_level:"HIGH",<br/>    advice:"Always insist on in-person or video tour." },<br/>  { pattern:"landlord_abroad", risk_level:"HIGH",<br/>    advice:"Use a licensed UK letting agent." },<br/>  { pattern:"whatsapp_only_contact", risk_level:"MEDIUM",<br/>    advice:"Obtain a physical address & phone number." }<br/>]
    MCP   -->> AB  : matched_patterns (4 patterns, highest=DANGER)

    %% ── Step 6: Gemini analyses severity ────────────────────────────────────────
    AB    ->>  GEM : analyse_scam_severity(listing_text, matched_patterns)
    GEM   -->> AB  : {<br/>  overall_risk: "DANGER",<br/>  confidence: 0.94,<br/>  reasoning: "Cash-upfront + no viewing + landlord abroad<br/>  is the classic Gumtree/Facebook scam trifecta.<br/>  Probability of fraud: very high.",<br/>  red_flags: [<br/>    "3 months cash upfront demanded",<br/>    "No property viewings permitted",<br/>    "Landlord claims to be overseas",<br/>    "WhatsApp-only contact (no traceable record)"<br/>  ],<br/>  safe_actions: [<br/>    "Do NOT send any money",<br/>    "Report listing to Action Fraud (UK)",<br/>    "Check property on Rightmove / Zoopla",<br/>    "Contact university housing office"<br/>  ]<br/>}

    %% ── Alt block: Risk levels ───────────────────────────────────────────────────
    alt overall_risk = DANGER or HIGH
        AB    -->> API : { risk_level:"DANGER", confidence:0.94,<br/>matched_patterns:4, red_flags:[...],<br/>safe_actions:[...], reasoning:"..." }
        API   -->> FE  : DANGER response JSON
        FE    -->> User : ScamScanner renders 🔴 DANGER banner<br/>Red flag chips highlighted<br/>Safe action checklist displayed
    else overall_risk = MEDIUM
        AB    -->> API : { risk_level:"MEDIUM", confidence:0.65,<br/>matched_patterns:2, red_flags:[...],<br/>safe_actions:[...] }
        API   -->> FE  : MEDIUM response JSON
        FE    -->> User : ScamScanner renders 🟠 CAUTION banner<br/>Flags listed with advice
    else overall_risk = LOW
        AB    -->> API : { risk_level:"LOW", confidence:0.12,<br/>matched_patterns:0, red_flags:[],<br/>safe_actions:["Standard checks still recommended"] }
        API   -->> FE  : LOW response JSON
        FE    -->> User : ScamScanner renders 🟢 LIKELY SAFE banner
    end
```

## Key Insights

| Step | What Happens | Why It Matters |
|------|-------------|----------------|
| **Keyword extraction** | Gemini tokenises the listing before hitting MongoDB | Allows fuzzy natural-language input to map to structured pattern keys |
| **`$in` query** | MongoDB MCP uses `$in` operator on the `keywords[]` array field | Fast index scan — no full-text search licence needed; sub-10ms at scale |
| **Pattern database** | `scam_patterns` stores community-curated red flags with severity levels | Non-AI rules can be updated independently of model deployment |
| **Confidence score** | Gemini returns 0–1 confidence alongside the risk label | Frontend can show uncertainty — "94% confident this is fraud" vs "65% caution" |
| **Four risk levels** | LOW / MEDIUM / HIGH / DANGER map to green / amber / red / red-pulsing UI | Graduated response prevents alarm fatigue for minor flag matches |
| **`safe_actions`** | Actionable next steps returned per listing | Transforms detection into student empowerment — not just a warning but a to-do list |
