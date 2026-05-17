# GuardianVisa — System Architecture

High-level view of how the React frontend, FastAPI backend, Vertex AI Agent Builder, Gemini 1.5 Pro, MongoDB MCP Server, and MongoDB Atlas connect to protect international students.

```mermaid
graph TD
    %% External actors
    USER["🧑‍🎓 Student (Browser)"]

    %% Frontend tier
    subgraph FE["☁️ Cloud Run — Frontend"]
        REACT["React + Tailwind\nChatInterface / RiskAlert\nScamScanner / EmergencyCard"]
    end

    %% Backend tier
    subgraph BE["☁️ Cloud Run — Backend"]
        FASTAPI["FastAPI\n/api/check\n/api/scan-scam\n/api/emergency"]
    end

    %% AI tier
    subgraph AI["🤖 Vertex AI"]
        AGENT["Google Cloud\nAgent Builder"]
        GEMINI["Gemini 1.5 Pro\nReasoning Engine"]
    end

    %% Data tier
    subgraph DATA["🗄️ Data Layer"]
        MCP["MongoDB\nMCP Server"]
        subgraph ATLAS["MongoDB Atlas"]
            C1[("students")]
            C2[("work_logs")]
            C3[("visa_rules")]
            C4[("scam_patterns")]
            C5[("emergency_resources")]
        end
    end

    %% Connections
    USER -->|"HTTPS"| REACT
    REACT -->|"REST POST"| FASTAPI
    FASTAPI -->|"Agent invocation\n+ student_id"| AGENT
    AGENT <-->|"Tool calls\ncheck_visa_hours\nget_student_profile\nscan_scam_signals\nget_emergency_resources\ndraft_safe_response"| GEMINI
    AGENT -->|"MCP protocol"| MCP
    MCP -->|"MongoDB driver"| C1
    MCP -->|"MongoDB driver"| C2
    MCP -->|"MongoDB driver"| C3
    MCP -->|"MongoDB driver"| C4
    MCP -->|"MongoDB driver"| C5
    AGENT -->|"Structured JSON\nRISK_ALERT / SCAM_SCORE\nEMERGENCY_PLAN"| FASTAPI
    FASTAPI -->|"JSON response"| REACT

    %% Styling
    classDef userStyle fill:#4A90D9,stroke:#2C5F8A,color:#fff,rx:8
    classDef frontendStyle fill:#61DAFB,stroke:#21A1C4,color:#000
    classDef backendStyle fill:#009688,stroke:#00695C,color:#fff
    classDef aiStyle fill:#7C4DFF,stroke:#512DA8,color:#fff
    classDef mcpStyle fill:#FF6F00,stroke:#E65100,color:#fff
    classDef atlasStyle fill:#00ED64,stroke:#00A845,color:#000
    classDef collStyle fill:#E8F5E9,stroke:#00A845,color:#000

    class USER userStyle
    class REACT frontendStyle
    class FASTAPI backendStyle
    class AGENT,GEMINI aiStyle
    class MCP mcpStyle
    class C1,C2,C3,C4,C5 collStyle
```

## Key Insights

| Layer | Technology | Role |
|-------|-----------|------|
| **Frontend** | React + Tailwind on Cloud Run | Renders 3 specialised UI components (RiskAlert, ScamScanner, EmergencyCard) and posts to FastAPI |
| **Backend** | FastAPI on Cloud Run | Thin orchestration layer — validates input, calls Agent Builder, returns structured JSON |
| **Agent Brain** | Vertex AI Agent Builder | Manages tool-call loop; decides which tools to invoke and in what order |
| **Reasoning** | Gemini 1.5 Pro | Performs all LLM reasoning: intent detection, violation maths, scam scoring, plan drafting |
| **Data Gateway** | MongoDB MCP Server | Translates agent tool calls into MongoDB Atlas queries; acts as the secure data bridge |
| **Persistence** | MongoDB Atlas | Five collections store students, logs, rules, scam patterns, and emergency resources |

> The MCP Server is the **only** component with direct database credentials, keeping Gemini and Agent Builder stateless and credentials-free.
