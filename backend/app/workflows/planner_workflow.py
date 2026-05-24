from __future__ import annotations

from app.domain.models import PlannerState
from app.services.planner_service import PlannerService


class PlannerWorkflow:
    """intent_analysis → risk_precheck → task_decomposition → agent_routing → synthesis"""

    def __init__(self, planner_service: PlannerService):
        self.planner_service = planner_service

    async def execute(self, user_id: str, message: str) -> PlannerState:
        return await self.planner_service.run(user_id=user_id, message=message)

