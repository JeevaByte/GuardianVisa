from __future__ import annotations

from fastapi import APIRouter, Depends

from app.api.deps import get_risk_engine
from app.schemas.api import RiskPreviewResponse
from app.services.risk_engine import RiskEngine

router = APIRouter(prefix="/api", tags=["risk"])


@router.get("/risk/preview", response_model=RiskPreviewResponse)
async def risk_preview(
    visa: float = 0,
    scam: float = 0,
    legal_urgency: float = 0,
    financial: float = 0,
    compliance: float = 0,
    risk_engine: RiskEngine = Depends(get_risk_engine),
) -> RiskPreviewResponse:
    risk = risk_engine.score(
        {
            "visa": visa,
            "scam": scam,
            "legal_urgency": legal_urgency,
            "financial": financial,
            "compliance": compliance,
        }
    )
    return RiskPreviewResponse(risk=risk)

