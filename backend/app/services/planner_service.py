from __future__ import annotations

from app.agents.communication_drafting_agent import CommunicationDraftingAgent
from app.agents.emergency_recovery_agent import EmergencyRecoveryAgent
from app.agents.legal_resource_agent import LegalResourceAgent
from app.agents.notification_agent import NotificationAgent
from app.agents.scam_detection_agent import ScamDetectionAgent
from app.agents.visa_compliance_agent import VisaComplianceAgent
from app.core.events import EventBus
from app.domain.models import PlannerState, PlannerStep
from app.services.action_engine import ActionEngine
from app.services.memory_service import MemoryService
from app.services.rag_service import RAGService
from app.services.risk_engine import RiskEngine


class PlannerService:
    def __init__(
        self,
        memory_service: MemoryService,
        risk_engine: RiskEngine,
        rag_service: RAGService,
        action_engine: ActionEngine,
        event_bus: EventBus,
    ) -> None:
        self.memory_service = memory_service
        self.risk_engine = risk_engine
        self.rag_service = rag_service
        self.action_engine = action_engine
        self.event_bus = event_bus
        self.visa_agent = VisaComplianceAgent()
        self.scam_agent = ScamDetectionAgent()
        self.emergency_agent = EmergencyRecoveryAgent()
        self.legal_agent = LegalResourceAgent()
        self.communication_agent = CommunicationDraftingAgent()
        self.notification_agent = NotificationAgent()

    async def run(self, user_id: str, message: str) -> PlannerState:
        state = PlannerState(user_id=user_id, input_text=message)
        await self._emit(state, "planner.step.started", "in_progress", "Analyzing user intent")

        await self.memory_service.store_user_message(user_id, message)
        state.memory_context = await self.memory_service.get_context(user_id)
        state.timeline.append(
            PlannerStep(step="intent_analysis", status="completed", details="Intent and memory context loaded", confidence=0.86)
        )

        await self._emit(state, "planner.step.started", "in_progress", "Running retrieval context query")
        state.retrieval_context = await self.rag_service.retrieve(message, limit=5)
        state.timeline.append(
            PlannerStep(step="retrieval", status="completed", details="Policy context retrieved", confidence=0.74)
        )

        visa = await self.visa_agent.run(message, state.memory_context)
        scam = await self.scam_agent.run(message, state.memory_context)
        emergency = await self.emergency_agent.run(message, state.memory_context)
        legal = await self.legal_agent.run(message, state.memory_context, state.retrieval_context)

        risk = self.risk_engine.score(
            {
                "visa": visa.get("visa_signal", 0),
                "scam": scam.get("scam_signal", 0),
                "legal_urgency": emergency.get("legal_urgency_signal", 0),
                "financial": 40 if "job" in message.lower() or "fund" in message.lower() else 18,
                "compliance": visa.get("compliance_signal", 0),
            }
        )
        state.risk = risk
        state.timeline.append(
            PlannerStep(step="risk_precheck", status="completed", details="Risk scored with weighted engine", confidence=risk.confidence)
        )
        await self._emit(state, "risk.updated", "completed", f"Risk evaluated: {risk.severity.value}", confidence=risk.confidence)

        action_plan = self.action_engine.generate(message, risk, state.retrieval_context)
        draft = await self.communication_agent.run(message, risk.severity.value)
        notify = await self.notification_agent.run(risk.severity.value, risk.triggered_actions)

        state.outputs = {
            "visa_agent": visa,
            "scam_agent": scam,
            "emergency_agent": emergency,
            "legal_agent": legal,
            "communication_agent": draft,
            "notification_agent": notify,
            "action_engine": action_plan,
        }
        state.actions = action_plan.get("tasks", [])
        state.timeline.extend(
            [
                PlannerStep(step="task_decomposition", status="completed", details="Task list and timeline generated", confidence=0.82),
                PlannerStep(step="agent_routing", status="completed", details="Specialist agents coordinated", confidence=0.8),
                PlannerStep(step="synthesis", status="completed", details="Final response synthesized", confidence=0.84),
            ]
        )

        await self.memory_service.store_agent_message(user_id, str({"risk": state.risk.model_dump(), "actions": state.actions}))
        await self.memory_service.store_memory_summary(
            user_id,
            summary=f"Severity {state.risk.severity.value} scenario processed for message '{message[:90]}'",
            tags=["planner_run", state.risk.severity.value.lower()],
        )
        await self.memory_service.save_trace(user_id, state.model_dump())
        await self._emit(state, "workflow.completed", "completed", "Planner workflow complete", confidence=state.risk.confidence)
        return state

    async def _emit(
        self,
        state: PlannerState,
        event_type: str,
        status: str,
        message: str,
        confidence: float | None = None,
        payload: dict | None = None,
    ) -> None:
        event = self.event_bus.make_event(
            event_type=event_type,
            status=status,
            message=message,
            confidence=confidence,
            payload={"user_id": state.user_id, **(payload or {})},
        )
        await self.event_bus.publish(event)

