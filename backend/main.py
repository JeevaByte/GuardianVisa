"""
GuardianVisa – FastAPI entry point.

Endpoints:
  POST /api/check          – visa hours risk check
  POST /api/scan-scam      – scam detection
  POST /api/emergency      – emergency 7-day plan
  GET  /api/student/{id}   – student profile
  GET  /health             – liveness probe
"""

import logging
from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

import mongodb_client as db
from agent import (
    EmergencyPlanResponse,
    GuardianVisaAgent,
    ScamRiskResponse,
    VisaRiskResponse,
)

load_dotenv()

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Lifespan – ensure MongoDB connection is alive on startup
# ---------------------------------------------------------------------------

@asynccontextmanager
async def lifespan(app: FastAPI):
    client = db.get_client()
    if client is not None:
        try:
            await client.admin.command("ping")
            log.info("MongoDB connection established.")
        except Exception as exc:
            log.warning("MongoDB not reachable at startup: %s", exc)
    else:
        log.info("Starting without MongoDB (mock/fallback mode).")
    yield
    if client is not None:
        client.close()


# ---------------------------------------------------------------------------
# App
# ---------------------------------------------------------------------------

app = FastAPI(
    title="GuardianVisa API",
    description="AI-powered visa protection for international students.",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # open for hackathon demo
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

agent = GuardianVisaAgent()


# ---------------------------------------------------------------------------
# Request / Response models
# ---------------------------------------------------------------------------

class VisaCheckRequest(BaseModel):
    student_id: str
    message: str


class VisaCheckResponse(BaseModel):
    risk_level: str
    current_hours: float
    proposed_hours: float
    limit: float
    violation: bool
    consequence: str
    safe_response_draft: str
    alternatives: list[str]


class ScamScanRequest(BaseModel):
    text: str


class ScamScanResponse(BaseModel):
    risk_level: str
    risk_score: int
    red_flags: list[str]
    advice: str
    matched_patterns: list[str]


class EmergencyRequest(BaseModel):
    student_id: str
    situation: str


class EmergencyResponse(BaseModel):
    days_until_visa_expiry: int
    action_plan_7_days: list[dict]
    resources: list[dict]
    draft_email: str


class StudentProfile(BaseModel):
    student_id: str
    name: str | None = None
    visa_type: str | None = None
    visa_expiry: str | None = None
    university: str | None = None
    city: str | None = None


class HealthResponse(BaseModel):
    status: str
    version: str


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _visa_response(r: VisaRiskResponse) -> VisaCheckResponse:
    return VisaCheckResponse(
        risk_level=r.risk_level,
        current_hours=r.current_hours,
        proposed_hours=r.proposed_hours,
        limit=r.limit,
        violation=r.violation,
        consequence=r.consequence,
        safe_response_draft=r.safe_response_draft,
        alternatives=r.alternatives,
    )


def _scam_response(r: ScamRiskResponse) -> ScamScanResponse:
    return ScamScanResponse(
        risk_level=r.risk_level,
        risk_score=r.risk_score,
        red_flags=r.red_flags,
        advice=r.advice,
        matched_patterns=r.matched_patterns,
    )


def _emergency_response(r: EmergencyPlanResponse) -> EmergencyResponse:
    return EmergencyResponse(
        days_until_visa_expiry=r.days_until_visa_expiry,
        action_plan_7_days=r.action_plan_7_days,
        resources=r.resources,
        draft_email=r.draft_email,
    )


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@app.get("/health", response_model=HealthResponse, tags=["system"])
async def health():
    """Liveness probe – always returns 200 when the server is running."""
    return HealthResponse(status="ok", version=app.version)


@app.post("/api/check", response_model=VisaCheckResponse, tags=["visa"])
async def check_visa_hours(body: VisaCheckRequest):
    """
    Analyse whether the described work situation violates the student's visa
    work-hour limits and return risk assessment + safe employer response draft.
    """
    try:
        result = await agent.check_visa_risk(body.student_id, body.message)
        return _visa_response(result)
    except Exception as exc:
        log.exception("Error in /api/check")
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@app.post("/api/scan-scam", response_model=ScamScanResponse, tags=["scam"])
async def scan_scam(body: ScamScanRequest):
    """
    Evaluate supplied text for scam indicators targeting international students
    (fake jobs, housing fraud, visa-fee scams, etc.).
    """
    if not body.text.strip():
        raise HTTPException(status_code=422, detail="text must not be empty")
    try:
        result = await agent.scan_scam(body.text)
        return _scam_response(result)
    except Exception as exc:
        log.exception("Error in /api/scan-scam")
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@app.post("/api/emergency", response_model=EmergencyResponse, tags=["emergency"])
async def emergency_plan(body: EmergencyRequest):
    """
    Generate an urgent 7-day action plan and resource list for a student
    facing an immigration emergency (impending expiry, overstay risk, etc.).
    """
    try:
        result = await agent.get_emergency_plan(body.student_id, body.situation)
        return _emergency_response(result)
    except Exception as exc:
        log.exception("Error in /api/emergency")
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@app.get("/api/student/{student_id}", response_model=StudentProfile, tags=["student"])
async def get_student(student_id: str):
    """Retrieve the student profile document from MongoDB."""
    profile = await db.get_student_profile(student_id)
    if not profile:
        raise HTTPException(status_code=404, detail=f"Student '{student_id}' not found")
    return StudentProfile(**profile)
