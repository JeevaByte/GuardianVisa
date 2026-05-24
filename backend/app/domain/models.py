from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, Field


class Severity(str, Enum):
    SAFE = "SAFE"
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class RiskBreakdown(BaseModel):
    visa: float = Field(ge=0, le=100)
    scam: float = Field(ge=0, le=100)
    legal_urgency: float = Field(ge=0, le=100)
    financial: float = Field(ge=0, le=100)
    compliance: float = Field(ge=0, le=100)


class RiskScore(BaseModel):
    normalized_score: float = Field(ge=0, le=100)
    confidence: float = Field(ge=0, le=1)
    severity: Severity
    breakdown: RiskBreakdown
    reasons: list[str] = Field(default_factory=list)
    triggered_actions: list[str] = Field(default_factory=list)


class PlannerStep(BaseModel):
    step: str
    status: str
    details: str
    confidence: float | None = None


class PlannerState(BaseModel):
    user_id: str
    input_text: str
    memory_context: dict = Field(default_factory=dict)
    retrieval_context: list[dict] = Field(default_factory=list)
    risk: RiskScore | None = None
    actions: list[dict] = Field(default_factory=list)
    outputs: dict = Field(default_factory=dict)
    timeline: list[PlannerStep] = Field(default_factory=list)

