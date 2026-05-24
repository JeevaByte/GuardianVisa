from __future__ import annotations

from fastapi import APIRouter

from app.core.config import settings
from app.core.database import mongo_manager
from app.schemas.api import HealthResponse

router = APIRouter(tags=["system"])


@router.get("/health", response_model=HealthResponse)
async def health() -> HealthResponse:
    connected = await mongo_manager.ping()
    return HealthResponse(status="ok", version=settings.app_version, mongo_connected=connected)

