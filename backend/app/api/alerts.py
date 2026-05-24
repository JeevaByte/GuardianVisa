from __future__ import annotations

from fastapi import APIRouter, Depends

from app.api.deps import get_memory_repo
from app.repositories.memory_repository import MemoryRepository
from app.schemas.api import AlertResponse

router = APIRouter(prefix="/api", tags=["alerts"])


@router.get("/alerts", response_model=list[AlertResponse])
async def list_alerts(user_id: str | None = None, repo: MemoryRepository = Depends(get_memory_repo)) -> list[AlertResponse]:
    alerts = await repo.list_open_alerts(user_id=user_id)
    return [AlertResponse(**item) for item in alerts]

