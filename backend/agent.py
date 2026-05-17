"""
Vertex AI / Gemini integration for GuardianVisa.

Each public method on GuardianVisaAgent:
  1. Builds a natural-language prompt with student context.
  2. Calls tool_dispatcher.run_agent_turn() which drives the full agentic loop
     (Gemini ↔ tool handlers ↔ Gemini) and returns a final JSON string.
  3. Parses the structured JSON into a typed response dataclass.
  4. Falls back to a realistic mock response when GCP is unavailable (demo mode).
"""

import json
import logging
import os
from dataclasses import dataclass, field
from datetime import date
from typing import Any, Optional

from dotenv import load_dotenv

import mongodb_client as db
from tool_dispatcher import run_agent_turn

load_dotenv()

log = logging.getLogger(__name__)

GCP_PROJECT_ID = os.getenv("GCP_PROJECT_ID", "")
GCP_LOCATION = os.getenv("GCP_LOCATION", "us-central1")
AGENT_ID = os.getenv("AGENT_ID", "")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-1.5-pro")

# ---------------------------------------------------------------------------
# Response dataclasses
# ---------------------------------------------------------------------------

@dataclass
class VisaRiskResponse:
    risk_level: str                  # "LOW" | "MEDIUM" | "HIGH" | "CRITICAL"
    current_hours: float
    proposed_hours: float
    limit: float
    violation: bool
    consequence: str
    safe_response_draft: str
    alternatives: list[str]


@dataclass
class ScamRiskResponse:
    risk_level: str                  # "LOW" | "MEDIUM" | "HIGH"
    risk_score: int                  # 0–100
    red_flags: list[str]
    advice: str
    matched_patterns: list[str]


@dataclass
class EmergencyPlanResponse:
    days_until_visa_expiry: int
    action_plan_7_days: list[dict]   # [{day, action, priority}]
    resources: list[dict]            # [{name, contact, type}]
    draft_email: str


# ---------------------------------------------------------------------------
# JSON parsing helper
# ---------------------------------------------------------------------------

def _parse_json(raw: Optional[str], fallback: dict) -> dict:
    """Safely parse JSON; return *fallback* on any error."""
    if not raw:
        return fallback
    try:
        # Gemini sometimes wraps JSON in markdown fences – strip them.
        cleaned = (
            raw.strip()
            .removeprefix("```json")
            .removeprefix("```")
            .removesuffix("```")
            .strip()
        )
        return json.loads(cleaned)
    except json.JSONDecodeError:
        log.warning("Failed to parse Gemini JSON response")
        return fallback


# ---------------------------------------------------------------------------
# Mock responses (Priya scenario – 18 h current + 8 h proposed = 26 h, Tier 4)
# ---------------------------------------------------------------------------

_MOCK_VISA_RISK = {
    "risk_level": "CRITICAL",
    "current_hours": 18.0,
    "proposed_hours": 8.0,
    "limit": 20.0,
    "violation": True,
    "consequence": (
        "Working 26 hours per week exceeds the Tier 4 (Student) visa limit of 20 hours. "
        "This constitutes a visa condition breach that can result in visa curtailment, "
        "removal from the UK, and a ban on future applications."
    ),
    "safe_response_draft": (
        "Hi [Employer], thank you for the additional shifts offer. "
        "Unfortunately, my student visa only permits me to work a maximum of 20 hours "
        "per week during term time. I am currently at 18 hours so I can only take on "
        "2 more hours this week. I'd love to take on more hours during my university "
        "holiday periods when the restriction is lifted. Could we discuss scheduling "
        "around those dates instead?"
    ),
    "alternatives": [
        "Accept only 2 additional hours this week to stay within the 20-hour limit.",
        "Request shifts during university holiday periods (no hour cap applies).",
        "Ask your international student advisor if your course allows an exemption.",
        "Check whether a part-time postgraduate route offers different work conditions.",
    ],
}

_MOCK_SCAM = {
    "risk_level": "HIGH",
    "risk_score": 85,
    "red_flags": [
        "Requests payment upfront before providing a job offer letter.",
        "Promises unusually high pay (£25/hr) for unskilled cash-in-hand work.",
        "Employer is unregistered and cannot sponsor a Skilled Worker visa.",
        "Communication only via WhatsApp with no official email domain.",
        "Urgency pressure: 'Accept by tonight or lose the slot.'",
    ],
    "advice": (
        "Do NOT pay any fee. Legitimate employers never charge workers for placement. "
        "Verify the company on Companies House (gov.uk) before sharing personal details. "
        "Report the listing to Action Fraud (actionfraud.police.uk) and your university "
        "careers service."
    ),
    "matched_patterns": [
        "upfront-payment-job-scam",
        "cash-in-hand-no-contract",
        "whatsapp-only-contact",
    ],
}

_MOCK_EMERGENCY = {
    "days_until_visa_expiry": 14,
    "action_plan_7_days": [
        {"day": 1, "action": "Contact your university's International Student Advisory team immediately.", "priority": "URGENT"},
        {"day": 1, "action": "Gather all immigration documents: BRP, CAS letter, enrollment proof.", "priority": "URGENT"},
        {"day": 2, "action": "Book an appointment with a registered OISC immigration adviser.", "priority": "HIGH"},
        {"day": 3, "action": "Submit a Tier 4 extension application via UKVI if eligible.", "priority": "HIGH"},
        {"day": 4, "action": "Notify your university's registry of your visa status to pause studies if needed.", "priority": "MEDIUM"},
        {"day": 5, "action": "Apply for emergency hardship fund if financially impacted.", "priority": "MEDIUM"},
        {"day": 7, "action": "Follow up with UKVI and adviser; confirm application reference number.", "priority": "HIGH"},
    ],
    "resources": [
        {"name": "UKCISA – UK Council for International Student Affairs", "contact": "020 7788 9214", "type": "legal_advice"},
        {"name": "Migrants' Rights Network", "contact": "info@migrantsrights.org.uk", "type": "legal_advice"},
        {"name": "Shelter Housing Helpline", "contact": "0808 800 4444", "type": "housing"},
        {"name": "Samaritans (24/7 mental health)", "contact": "116 123", "type": "mental_health"},
        {"name": "University International Office", "contact": "Check your university website", "type": "academic"},
    ],
    "draft_email": (
        "Subject: Urgent – Tier 4 Visa Expiry Concern\n\n"
        "Dear International Student Advisory Team,\n\n"
        "I am writing to urgently request guidance regarding my Tier 4 student visa, "
        "which is due to expire in approximately 14 days. I am currently enrolled on "
        "[Course Name] and wish to continue my studies.\n\n"
        "I would be grateful for an emergency appointment at your earliest convenience "
        "to discuss my extension options and any supporting documentation required.\n\n"
        "My student ID is [STUDENT_ID] and I can be reached at [EMAIL / PHONE].\n\n"
        "Thank you for your support.\n\nKind regards,\n[Your Name]"
    ),
}


# ---------------------------------------------------------------------------
# Agent class
# ---------------------------------------------------------------------------

class GuardianVisaAgent:
    """Orchestrates MongoDB context retrieval + Gemini agentic inference."""

    # --- Visa hours check ---------------------------------------------------

    async def check_visa_risk(
        self, student_id: str, message: str
    ) -> VisaRiskResponse:
        """
        Analyse whether the described work situation violates the student's
        visa work-hour limits.

        Steps:
          1. Build a prompt telling Gemini to use get_student_profile and
             check_visa_hours, then draft a safe employer response.
          2. Run the full agentic loop via run_agent_turn.
          3. Parse the JSON result into a VisaRiskResponse.
          4. Fall back to the Priya mock on any GCP failure.
        """
        # Fetch minimal context to personalise the prompt; the agent will
        # fetch full details via tool calls.
        profile = await db.get_student_profile(student_id) or {}
        visa_type = profile.get("visa_type", "Tier 4")

        prompt = f"""
A student (student_id="{student_id}") needs an urgent visa work-hours check.

Their visa type is {visa_type}. They have sent this message:
"{message}"

Please:
1. Call get_student_profile to get their current work hours and term dates.
2. Extract the proposed additional hours from the message, then call
   check_visa_hours with the current hours, proposed hours, visa type, and
   whether it is currently term time.
3. Call draft_safe_response to produce a professional employer reply if a
   violation is detected.

Return ONLY valid JSON:
{{
  "risk_level": "LOW|MEDIUM|HIGH|CRITICAL",
  "current_hours": <float>,
  "proposed_hours": <float>,
  "limit": <float>,
  "violation": <bool>,
  "consequence": "<string>",
  "safe_response_draft": "<string>",
  "alternatives": ["<string>", ...]
}}
"""

        turn = await run_agent_turn(prompt, student_id=student_id)
        data = _parse_json(turn.final_text, _MOCK_VISA_RISK)

        return VisaRiskResponse(
            risk_level=data.get("risk_level", _MOCK_VISA_RISK["risk_level"]),
            current_hours=float(data.get("current_hours", _MOCK_VISA_RISK["current_hours"])),
            proposed_hours=float(data.get("proposed_hours", _MOCK_VISA_RISK["proposed_hours"])),
            limit=float(data.get("limit", _MOCK_VISA_RISK["limit"])),
            violation=bool(data.get("violation", _MOCK_VISA_RISK["violation"])),
            consequence=data.get("consequence", _MOCK_VISA_RISK["consequence"]),
            safe_response_draft=data.get("safe_response_draft", _MOCK_VISA_RISK["safe_response_draft"]),
            alternatives=data.get("alternatives", _MOCK_VISA_RISK["alternatives"]),
        )

    # --- Scam detection -----------------------------------------------------

    async def scan_scam(self, text: str) -> ScamRiskResponse:
        """
        Evaluate supplied text for scam indicators targeting international
        students.

        Steps:
          1. Build a prompt asking Gemini to call scan_scam_signals.
          2. Run the agentic loop.
          3. Parse the JSON result into a ScamRiskResponse.
          4. Fall back to mock on GCP failure.
        """
        prompt = f"""
A student has asked GuardianVisa to check whether the following text is a scam:

TEXT TO ANALYSE:
\"\"\"{text}\"\"\"

Please call scan_scam_signals with this text. If the student's city is
identifiable from the text, pass it as the city parameter.

Return ONLY valid JSON:
{{
  "risk_level": "LOW|MEDIUM|HIGH|DANGER",
  "risk_score": <int 0-100>,
  "red_flags": ["<string>", ...],
  "advice": "<actionable advice string>",
  "matched_patterns": ["<pattern id>", ...]
}}
"""

        turn = await run_agent_turn(prompt)
        data = _parse_json(turn.final_text, _MOCK_SCAM)

        # Normalise advice: the tool returns a list; the dataclass expects a string.
        advice = data.get("advice", _MOCK_SCAM["advice"])
        if isinstance(advice, list):
            advice = " ".join(advice)

        return ScamRiskResponse(
            risk_level=data.get("risk_level", _MOCK_SCAM["risk_level"]),
            risk_score=int(data.get("risk_score", _MOCK_SCAM["risk_score"])),
            red_flags=data.get("red_flags", _MOCK_SCAM["red_flags"]),
            advice=advice,
            matched_patterns=data.get("matched_patterns", _MOCK_SCAM["matched_patterns"]),
        )

    # --- Emergency plan -----------------------------------------------------

    async def get_emergency_plan(
        self, student_id: str, situation: str
    ) -> EmergencyPlanResponse:
        """
        Generate an urgent 7-day action plan for a student facing an
        immigration or welfare emergency.

        Steps:
          1. Build a prompt asking Gemini to call get_student_profile,
             get_emergency_resources, and draft_safe_response.
          2. Run the agentic loop.
          3. Parse the JSON result into an EmergencyPlanResponse.
          4. Fall back to mock on GCP failure.
        """
        profile = await db.get_student_profile(student_id) or {}
        city = profile.get("city", "London")

        prompt = f"""
A student (student_id="{student_id}") is facing an urgent situation in {city}:
"{situation}"

Please:
1. Call get_student_profile to get full context including visa expiry date.
2. Call get_emergency_resources for their city, filtered to types relevant to
   the situation (e.g. legal_advice, housing, mental_health, hardship_fund).
3. Call draft_safe_response to draft an urgent email to their university's
   International Student Advisory team.

Calculate days_until_visa_expiry from the visa_expiry date in the profile.

Return ONLY valid JSON:
{{
  "days_until_visa_expiry": <int>,
  "action_plan_7_days": [
    {{"day": <int 1-7>, "action": "<string>", "priority": "URGENT|HIGH|MEDIUM"}}
  ],
  "resources": [
    {{"name": "<string>", "contact": "<string>", "type": "<string>"}}
  ],
  "draft_email": "<full draft email string>"
}}
"""

        turn = await run_agent_turn(prompt, student_id=student_id)
        data = _parse_json(turn.final_text, _MOCK_EMERGENCY)

        return EmergencyPlanResponse(
            days_until_visa_expiry=int(
                data.get("days_until_visa_expiry", _MOCK_EMERGENCY["days_until_visa_expiry"])
            ),
            action_plan_7_days=data.get(
                "action_plan_7_days", _MOCK_EMERGENCY["action_plan_7_days"]
            ),
            resources=data.get("resources", _MOCK_EMERGENCY["resources"]),
            draft_email=data.get("draft_email", _MOCK_EMERGENCY["draft_email"]),
        )
