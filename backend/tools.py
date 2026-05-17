"""
tools.py – GuardianVisa Vertex AI tool definitions.

Each tool consists of:
  1. A FunctionDeclaration  – registered with the GenerativeModel so Gemini
     knows when and how to call it.
  2. An async handler       – the Python function that actually executes the
     tool and returns a JSON-serialisable dict.
"""

import json
import logging
import os
from typing import Optional

import mongodb_client as db

log = logging.getLogger(__name__)

GCP_PROJECT_ID = os.getenv("GCP_PROJECT_ID", "")
GCP_LOCATION = os.getenv("GCP_LOCATION", "us-central1")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-1.5-pro")

# ---------------------------------------------------------------------------
# Lazy Vertex AI import helper
# ---------------------------------------------------------------------------

def _get_function_declaration_class():
    """Import FunctionDeclaration only when Vertex AI is available."""
    from vertexai.generative_models import FunctionDeclaration  # noqa: PLC0415
    return FunctionDeclaration


# ---------------------------------------------------------------------------
# Tool 1 – get_student_profile
# ---------------------------------------------------------------------------

def make_get_student_profile_declaration():
    """Return the FunctionDeclaration for get_student_profile."""
    FunctionDeclaration = _get_function_declaration_class()
    return FunctionDeclaration(
        name="get_student_profile",
        description=(
            "Retrieves a student's profile including visa type, work hours this "
            "week, and term dates. Call this first whenever a student_id is available."
        ),
        parameters={
            "type": "object",
            "properties": {
                "student_id": {
                    "type": "string",
                    "description": "The unique student identifier.",
                },
            },
            "required": ["student_id"],
        },
    )


async def handle_get_student_profile(student_id: str) -> dict:
    """
    Fetch the student profile from MongoDB and return a flat dict.

    Returns keys: name, university, visa_type, visa_expiry,
                  work_hours_this_week, work_limit_term, term_dates, city.
    """
    profile = await db.get_student_profile(student_id)
    if not profile:
        return {
            "error": f"Student '{student_id}' not found",
            "name": student_id,
            "university": "Unknown",
            "visa_type": "Tier 4",
            "visa_expiry": "unknown",
            "work_hours_this_week": 0,
            "work_limit_term": 20,
            "term_dates": {},
            "city": "London",
        }

    # Fetch the current week's logged hours to populate work_hours_this_week.
    try:
        from datetime import date  # noqa: PLC0415
        week_start = date.today().strftime("%Y-%m-%d")
        work_logs = await db.get_work_logs(student_id, week_start=week_start)
        hours_this_week = sum(log.get("hours", 0) for log in work_logs)
    except Exception as exc:
        log.warning("Could not fetch work logs for %s: %s", student_id, exc)
        hours_this_week = profile.get("work_hours_this_week", 0)

    # Fetch visa rules to obtain the term-time limit.
    visa_type = profile.get("visa_type", "Tier 4")
    try:
        rules = await db.get_visa_rules(visa_type) or {}
        limit = rules.get("weekly_hour_limit", 20)
    except Exception:
        limit = 20

    return {
        "name": profile.get("name", student_id),
        "university": profile.get("university", "Unknown"),
        "visa_type": visa_type,
        "visa_expiry": profile.get("visa_expiry", "unknown"),
        "work_hours_this_week": hours_this_week,
        "work_limit_term": limit,
        "term_dates": profile.get("term_dates", {}),
        "city": profile.get("city", "London"),
    }


# ---------------------------------------------------------------------------
# Tool 2 – check_visa_hours
# ---------------------------------------------------------------------------

def make_check_visa_hours_declaration():
    """Return the FunctionDeclaration for check_visa_hours."""
    FunctionDeclaration = _get_function_declaration_class()
    return FunctionDeclaration(
        name="check_visa_hours",
        description=(
            "Checks if accepting proposed work hours would violate the student's "
            "visa conditions. Returns risk level, violation flag, and the specific "
            "rule being breached."
        ),
        parameters={
            "type": "object",
            "properties": {
                "current_hours": {
                    "type": "number",
                    "description": "Hours the student has already worked this week.",
                },
                "proposed_additional_hours": {
                    "type": "number",
                    "description": "Additional hours the student is considering.",
                },
                "visa_type": {
                    "type": "string",
                    "description": "Student visa category, e.g. 'Tier 4', 'Graduate'.",
                },
                "is_term_time": {
                    "type": "boolean",
                    "description": "True if university is currently in term time.",
                },
            },
            "required": [
                "current_hours",
                "proposed_additional_hours",
                "visa_type",
                "is_term_time",
            ],
        },
    )


async def handle_check_visa_hours(
    current_hours: float,
    proposed_additional_hours: float,
    visa_type: str,
    is_term_time: bool,
) -> dict:
    """
    Compute whether current + proposed hours exceeds the visa limit.

    Fetches the authoritative limit from MongoDB; falls back to 20 h (Tier 4
    term-time default) if the rule cannot be found.
    """
    # Attempt to load the limit from the database.
    try:
        rules = await db.get_visa_rules(visa_type) or {}
        if is_term_time:
            limit = rules.get("weekly_hour_limit", 20)
        else:
            # Most UK student visas have no cap in vacation periods.
            limit = rules.get("vacation_hour_limit", 9999)
    except Exception as exc:
        log.warning("Could not fetch visa rules for %s: %s", visa_type, exc)
        limit = 20

    current_total = current_hours + proposed_additional_hours
    excess = max(0.0, current_total - limit)
    would_violate = current_total > limit

    # Map excess to a risk level.
    if not would_violate:
        risk_level = "SAFE"
    elif excess <= 2:
        risk_level = "WARNING"
    elif excess <= 5:
        risk_level = "HIGH"
    else:
        risk_level = "CRITICAL"

    # Choose the appropriate consequence text.
    consequences = {
        "SAFE": "No violation – hours are within the permitted limit.",
        "WARNING": (
            f"Marginally over the {limit}-hour limit. A small excess may still "
            "constitute a technical breach and should be avoided."
        ),
        "HIGH": (
            f"Working {current_total:.0f} hours exceeds the {visa_type} limit of "
            f"{limit} hours by {excess:.0f} hours. This is a reportable breach."
        ),
        "CRITICAL": (
            f"Working {current_total:.0f} hours significantly exceeds the {visa_type} "
            f"limit of {limit} hours ({excess:.0f} h over). This risks visa curtailment, "
            "removal from the UK, and a ban on future visa applications."
        ),
    }

    return {
        "would_violate": would_violate,
        "current_total": int(current_total),
        "limit": int(limit),
        "excess_hours": int(excess),
        "risk_level": risk_level,
        "consequence": consequences[risk_level],
    }


# ---------------------------------------------------------------------------
# Tool 3 – scan_scam_signals
# ---------------------------------------------------------------------------

def make_scan_scam_signals_declaration():
    """Return the FunctionDeclaration for scan_scam_signals."""
    FunctionDeclaration = _get_function_declaration_class()
    return FunctionDeclaration(
        name="scan_scam_signals",
        description=(
            "Analyses text for accommodation or job scam indicators by matching "
            "against known scam patterns stored in MongoDB. Returns a risk score, "
            "matched patterns, red flags, and actionable advice."
        ),
        parameters={
            "type": "object",
            "properties": {
                "text": {
                    "type": "string",
                    "description": "The message, listing, or offer text to analyse.",
                },
                "city": {
                    "type": "string",
                    "description": "City context (optional) to weight local scam patterns.",
                },
            },
            "required": ["text"],
        },
    )


async def handle_scan_scam_signals(text: str, city: Optional[str] = None) -> dict:
    """
    Extract keywords from *text*, query MongoDB scam_patterns, and aggregate
    risk levels into a summary response.
    """
    # Extract meaningful keywords (>4 chars to skip stop-words).
    keywords = [w.strip(".,!?\"'()") for w in text.lower().split() if len(w) > 4][:15]
    if city:
        keywords.append(city.lower())

    matched_docs: list = []
    try:
        matched_docs = await db.search_scam_patterns(keywords)
    except Exception as exc:
        log.warning("Scam pattern search failed: %s", exc)

    # Aggregate risk from matched documents.
    risk_weights = {"LOW": 10, "MEDIUM": 30, "HIGH": 60, "DANGER": 90}
    cumulative_score = 0
    red_flags: list[str] = []
    advice_fragments: list[str] = []
    pattern_ids: list[str] = []

    for doc in matched_docs:
        pattern_ids.append(doc.get("pattern_id", doc.get("name", "unknown")))
        doc_risk = doc.get("risk_level", "LOW").upper()
        cumulative_score += risk_weights.get(doc_risk, 10)
        if "red_flag" in doc:
            red_flags.append(doc["red_flag"])
        if "advice" in doc:
            advice_fragments.append(doc["advice"])

    # Heuristic bump: check for known high-risk phrases directly in the text.
    HIGH_RISK_PHRASES = [
        ("upfront fee", 40, "Requests payment before job/tenancy confirmed."),
        ("cash in hand", 35, "Cash-in-hand work may be unregistered and unprotected."),
        ("whatsapp only", 30, "Contact only via WhatsApp – no official email trail."),
        ("no contract", 35, "Offer without a written contract is a red flag."),
        ("limited time", 20, "Artificial urgency is a common pressure tactic."),
        ("guaranteed visa", 50, "No private entity can guarantee a visa outcome."),
        ("pay to apply", 50, "Legitimate employers never charge workers for placement."),
        ("western union", 45, "Wire-transfer payment methods are unrecoverable if scammed."),
    ]
    text_lower = text.lower()
    for phrase, bump, flag in HIGH_RISK_PHRASES:
        if phrase in text_lower:
            cumulative_score += bump
            red_flags.append(flag)

    risk_score = min(100, cumulative_score)

    if risk_score < 20:
        risk_level = "LOW"
    elif risk_score < 50:
        risk_level = "MEDIUM"
    elif risk_score < 75:
        risk_level = "HIGH"
    else:
        risk_level = "DANGER"

    default_advice = [
        "Verify any employer or landlord on official registers before sharing personal details.",
        "Never pay money upfront for a job or tenancy deposit via untraceable methods.",
        "Report suspected scams to Action Fraud (actionfraud.police.uk).",
    ]
    final_advice = advice_fragments if advice_fragments else default_advice

    return {
        "risk_score": risk_score,
        "risk_level": risk_level,
        "matched_patterns": pattern_ids,
        "red_flags": list(dict.fromkeys(red_flags)),  # deduplicate, preserve order
        "advice": final_advice,
    }


# ---------------------------------------------------------------------------
# Tool 4 – get_emergency_resources
# ---------------------------------------------------------------------------

def make_get_emergency_resources_declaration():
    """Return the FunctionDeclaration for get_emergency_resources."""
    FunctionDeclaration = _get_function_declaration_class()
    return FunctionDeclaration(
        name="get_emergency_resources",
        description=(
            "Retrieves emergency support resources for a student's city including "
            "food banks, hardship funds, legal advice, housing, and university support."
        ),
        parameters={
            "type": "object",
            "properties": {
                "city": {
                    "type": "string",
                    "description": "The city to search for resources in.",
                },
                "resource_types": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": (
                        "Optional filter list, e.g. ['food_bank', 'hardship_fund', "
                        "'legal_advice', 'housing', 'mental_health']."
                    ),
                },
            },
            "required": ["city"],
        },
    )


async def handle_get_emergency_resources(
    city: str,
    resource_types: Optional[list] = None,
) -> dict:
    """
    Query MongoDB emergency_resources for the given city, optionally filtered
    by one or more resource_types.
    """
    try:
        resources = await db.get_emergency_resources(city)
    except Exception as exc:
        log.warning("Emergency resource lookup failed for %s: %s", city, exc)
        resources = []

    # Apply optional type filter.
    if resource_types:
        normalised_types = [t.lower() for t in resource_types]
        resources = [
            r for r in resources
            if r.get("type", "").lower() in normalised_types
        ]

    # Normalise each document to the expected schema.
    normalised = [
        {
            "name": r.get("name", "Unknown Resource"),
            "type": r.get("type", "general"),
            "contact_phone": r.get("contact_phone", r.get("contact", "")),
            "contact_email": r.get("contact_email", ""),
            "url": r.get("url", ""),
            "eligibility": r.get("eligibility", "Open to all students"),
        }
        for r in resources
    ]

    return {
        "resources": normalised,
        "total_found": len(normalised),
    }


# ---------------------------------------------------------------------------
# Tool 5 – draft_safe_response
# ---------------------------------------------------------------------------

def make_draft_safe_response_declaration():
    """Return the FunctionDeclaration for draft_safe_response."""
    FunctionDeclaration = _get_function_declaration_class()
    return FunctionDeclaration(
        name="draft_safe_response",
        description=(
            "Drafts a polite, professional response message for the student to send "
            "to their employer, landlord, university, or a government body. Use this "
            "when the student needs help composing a safe and legally sound reply."
        ),
        parameters={
            "type": "object",
            "properties": {
                "situation": {
                    "type": "string",
                    "description": "Brief description of what the student needs to communicate.",
                },
                "recipient_type": {
                    "type": "string",
                    "enum": ["manager", "landlord", "university", "government"],
                    "description": "Who the message is addressed to.",
                },
                "tone": {
                    "type": "string",
                    "enum": ["firm", "polite", "urgent"],
                    "description": "Desired tone of the message.",
                },
                "context": {
                    "type": "object",
                    "description": (
                        "Additional key-value context, e.g. "
                        "{'visa_type': 'Tier 4', 'hours_limit': 20, 'hours_worked': 18}."
                    ),
                },
            },
            "required": ["situation", "recipient_type", "tone"],
        },
    )


async def handle_draft_safe_response(
    situation: str,
    recipient_type: str,
    tone: str,
    context: Optional[dict] = None,
) -> dict:
    """
    Build a structured prompt and call Gemini directly to generate a draft
    message the student can send.  Falls back to a template if Gemini is
    unavailable.
    """
    context = context or {}

    recipient_guidance = {
        "manager": "Maintain a professional and cooperative tone. Reference UK employment law briefly.",
        "landlord": "Reference the Landlord and Tenant Act; be clear about rights.",
        "university": "Be formal; address the International Student Advisory team.",
        "government": "Be precise and factual; reference UKVI guidelines where relevant.",
    }

    tone_guidance = {
        "firm": "Assert the student's legal rights clearly without being aggressive.",
        "polite": "Prioritise rapport while still communicating the boundary clearly.",
        "urgent": "Convey time-sensitivity respectfully; request a same-day response.",
    }

    prompt = f"""You are GuardianVisa, an AI assistant protecting international students.

TASK: Draft a {tone} message from a student to their {recipient_type}.

SITUATION:
{situation}

ADDITIONAL CONTEXT:
{json.dumps(context, indent=2)}

RECIPIENT GUIDANCE: {recipient_guidance.get(recipient_type, '')}
TONE GUIDANCE: {tone_guidance.get(tone, '')}

Return ONLY valid JSON with this exact schema:
{{
  "draft_message": "<full message text ready to send>",
  "subject_line": "<email subject line>",
  "key_points": ["<point 1>", "<point 2>", ...]
}}
"""

    # Attempt a direct Gemini call for this tool.
    draft_text = None
    if GCP_PROJECT_ID:
        try:
            import vertexai  # noqa: PLC0415
            from vertexai.generative_models import GenerationConfig, GenerativeModel  # noqa: PLC0415

            vertexai.init(project=GCP_PROJECT_ID, location=GCP_LOCATION)
            model = GenerativeModel(GEMINI_MODEL)
            resp = model.generate_content(
                prompt,
                generation_config=GenerationConfig(
                    temperature=0.3,
                    max_output_tokens=800,
                    response_mime_type="application/json",
                ),
            )
            draft_text = resp.text
        except Exception as exc:
            log.warning("Gemini call in draft_safe_response failed: %s", exc)

    if draft_text:
        try:
            cleaned = (
                draft_text.strip()
                .removeprefix("```json")
                .removeprefix("```")
                .removesuffix("```")
                .strip()
            )
            return json.loads(cleaned)
        except json.JSONDecodeError:
            log.warning("Failed to parse draft_safe_response JSON from Gemini")

    # Fallback template when Gemini is unreachable.
    return {
        "draft_message": (
            f"Dear {recipient_type.capitalize()},\n\n"
            f"I am writing regarding: {situation}\n\n"
            "I would appreciate your prompt attention to this matter.\n\n"
            "Kind regards,\n[Your Name]"
        ),
        "subject_line": f"Re: {situation[:60]}",
        "key_points": [
            "State the situation clearly.",
            "Reference applicable rules or legal rights.",
            "Request a specific action or response.",
        ],
    }


# ---------------------------------------------------------------------------
# Exported collection of all declarations (used by agent_config.py)
# ---------------------------------------------------------------------------

def get_all_declarations() -> list:
    """Return all five FunctionDeclaration objects for registration with Gemini."""
    return [
        make_get_student_profile_declaration(),
        make_check_visa_hours_declaration(),
        make_scan_scam_signals_declaration(),
        make_get_emergency_resources_declaration(),
        make_draft_safe_response_declaration(),
    ]
