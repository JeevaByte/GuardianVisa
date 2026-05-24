from __future__ import annotations

from fastapi import APIRouter, Depends

from app.api.deps import get_planner_workflow
from app.schemas.api import LegacyEmergencyRequest, LegacyScamRequest, LegacyVisaRequest
from app.workflows.planner_workflow import PlannerWorkflow

router = APIRouter(prefix="/api", tags=["legacy"])


@router.post("/check")
async def legacy_check(req: LegacyVisaRequest, workflow: PlannerWorkflow = Depends(get_planner_workflow)):
    state = await workflow.execute(req.student_id, req.message)
    return {
        "risk_level": state.risk.severity.value,
        "current_hours": 18,
        "proposed_hours": state.outputs.get("visa_agent", {}).get("proposed_hours", 0),
        "limit": 20,
        "violation": state.risk.breakdown.compliance >= 50,
        "consequence": "; ".join(state.risk.reasons),
        "safe_response_draft": state.outputs.get("communication_agent", {}).get("draft", ""),
        "alternatives": state.risk.triggered_actions,
    }


@router.post("/scan-scam")
async def legacy_scan(req: LegacyScamRequest, workflow: PlannerWorkflow = Depends(get_planner_workflow)):
    state = await workflow.execute("anonymous_user", req.text)
    scam = state.outputs.get("scam_agent", {})
    return {
        "risk_level": state.risk.severity.value,
        "risk_score": int(state.risk.breakdown.scam),
        "red_flags": scam.get("red_flags", []),
        "advice": "Follow compliance-safe actions and verify sources before responding.",
        "matched_patterns": scam.get("red_flags", []),
    }


@router.post("/emergency")
async def legacy_emergency(req: LegacyEmergencyRequest, workflow: PlannerWorkflow = Depends(get_planner_workflow)):
    state = await workflow.execute(req.student_id, req.situation)
    timeline = state.outputs.get("action_engine", {}).get("timeline", [])
    return {
        "days_until_visa_expiry": state.outputs.get("visa_agent", {}).get("days_until_expiry") or 30,
        "action_plan_7_days": [
            {"day": i + 1, "action": item.get("focus", "Follow escalation plan"), "priority": "HIGH"}
            for i, item in enumerate(timeline[:7])
        ],
        "resources": state.outputs.get("legal_agent", {}).get("legal_resources", []),
        "draft_email": state.outputs.get("communication_agent", {}).get("draft", ""),
    }

