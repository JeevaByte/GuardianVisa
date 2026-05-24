from __future__ import annotations

from functools import lru_cache

from app.core.events import EventBus
from app.repositories.memory_repository import MemoryRepository
from app.services.action_engine import ActionEngine
from app.services.memory_service import MemoryService
from app.services.planner_service import PlannerService
from app.services.rag_service import RAGService
from app.services.risk_engine import RiskEngine
from app.workflows.planner_workflow import PlannerWorkflow


@lru_cache
def get_event_bus() -> EventBus:
    return EventBus()


@lru_cache
def get_memory_repo() -> MemoryRepository:
    return MemoryRepository()


@lru_cache
def get_memory_service() -> MemoryService:
    return MemoryService(get_memory_repo())


@lru_cache
def get_risk_engine() -> RiskEngine:
    return RiskEngine()


@lru_cache
def get_rag_service() -> RAGService:
    return RAGService(get_memory_repo())


@lru_cache
def get_action_engine() -> ActionEngine:
    return ActionEngine()


@lru_cache
def get_planner_service() -> PlannerService:
    return PlannerService(
        memory_service=get_memory_service(),
        risk_engine=get_risk_engine(),
        rag_service=get_rag_service(),
        action_engine=get_action_engine(),
        event_bus=get_event_bus(),
    )


@lru_cache
def get_planner_workflow() -> PlannerWorkflow:
    return PlannerWorkflow(get_planner_service())

