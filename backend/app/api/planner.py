from __future__ import annotations

from fastapi import APIRouter, Depends

from app.api.deps import get_planner_workflow
from app.core.security import has_prompt_injection_signal, mask_pii
from app.schemas.api import AnalyzeRequest, AnalyzeResponse
from app.workflows.planner_workflow import PlannerWorkflow

router = APIRouter(prefix="/api", tags=["planner"])


@router.post("/analyze", response_model=AnalyzeResponse)
async def analyze(request: AnalyzeRequest, workflow: PlannerWorkflow = Depends(get_planner_workflow)) -> AnalyzeResponse:
    safe_message = mask_pii(request.message)
    if has_prompt_injection_signal(safe_message):
        safe_message = "Potential malicious prompt content removed. Student requested compliance guidance."
    state = await workflow.execute(user_id=request.user_id, message=safe_message)
    return AnalyzeResponse(planner_state=state)

