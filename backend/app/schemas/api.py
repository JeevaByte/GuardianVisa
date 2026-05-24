from __future__ import annotations

from pydantic import BaseModel, Field

from app.domain.models import PlannerState, RiskScore


class AnalyzeRequest(BaseModel):
    user_id: str = Field(min_length=1)
    message: str = Field(min_length=3, max_length=5000)


class AnalyzeResponse(BaseModel):
    planner_state: PlannerState


class LegacyVisaRequest(BaseModel):
    student_id: str
    message: str


class LegacyScamRequest(BaseModel):
    text: str


class LegacyEmergencyRequest(BaseModel):
    student_id: str
    situation: str


class HealthResponse(BaseModel):
    status: str
    version: str
    mongo_connected: bool


class AlertResponse(BaseModel):
    id: str
    user_id: str
    severity: str
    message: str
    created_at: str


class RiskPreviewResponse(BaseModel):
    risk: RiskScore

