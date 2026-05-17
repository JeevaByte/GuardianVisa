# GuardianVisa — MongoDB Entity-Relationship Diagram

All five MongoDB Atlas collections and their fields, plus the relationships between them.

```mermaid
erDiagram
    %% ── Core entities ──────────────────────────────────────────────────────────

    students {
        ObjectId  id                   PK
        string    name
        string    university
        string    course
        string    nationality
        string    visa_type            "e.g. Tier-4 / F-1 / 500"
        date      visa_expiry
        date      term_start
        date      term_end
        int       work_hours_this_week
        int       work_limit_term      "hours/week during term"
        int       work_limit_holiday   "hours/week during break"
        string    city
        string    email
    }

    work_logs {
        ObjectId  id           PK
        ObjectId  student_id   FK
        date      date
        float     hours_worked
        string    employer
        string    shift_type   "regular | overtime | weekend"
    }

    visa_rules {
        ObjectId  id                        PK
        string    visa_type                 "Tier-4 | F-1 | Student 500"
        string    country                   "UK | USA | AUS"
        int       term_work_limit_hours     "hours per week during term"
        int       holiday_work_limit_hours  "hours per week during break"
        string    violation_consequence     "curtailment | deportation | ban"
        string    source                    "UKVI | USCIS | HomeAffairs"
        date      last_updated
    }

    scam_patterns {
        ObjectId  id           PK
        string    pattern      "pattern name e.g. cash_only_upfront"
        string    risk_level   "LOW | MEDIUM | HIGH | DANGER"
        string    description
        string    advice
        array     keywords     "list of trigger words"
    }

    emergency_resources {
        ObjectId  id          PK
        string    city
        string    type        "food_bank | hardship_fund | legal_aid | counselling"
        string    name
        string    contact
        string    eligibility "international_student | all | low_income"
        string    url
    }

    %% ── Relationships ───────────────────────────────────────────────────────────

    %% One student has many work log entries
    students ||--o{ work_logs : "logs hours via"

    %% Many students share one visa rule set (same visa type)
    students }o--|| visa_rules : "governed by"
```

## Key Insights

- **`students`** is the central entity — it embeds denormalised work-limit fields (`work_limit_term`, `work_limit_holiday`) so the visa-hours check tool can run a single document read without a join.
- **`work_logs`** uses `student_id` as a foreign key. The MCP tool `check_visa_hours()` aggregates this week's hours with `$sum` and compares against the limit.
- **`visa_rules`** is a lookup table keyed on `visa_type + country`, keeping rule updates independent of student records — critical when UK UKVI or US USCIS changes regulations.
- **`scam_patterns`** stores the `keywords[]` array so the MCP query can use MongoDB `$in` against tokenised listing text, enabling fast pattern matching without full-text search overhead.
- **`emergency_resources`** is geographically scoped by `city`, so `get_emergency_resources(city)` returns only locally relevant services for the student's location.
- No explicit relationship exists between `scam_patterns`/`emergency_resources` and `students` — these are read-only reference collections queried by agent tools, not linked by FK.
