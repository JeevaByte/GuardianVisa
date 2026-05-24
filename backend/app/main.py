from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import alerts, health, legacy, planner, risk, stream
from app.api.deps import get_event_bus, get_memory_repo
from app.core.config import settings
from app.core.database import mongo_manager
from app.core.exceptions import register_exception_handlers
from app.core.logging import configure_logging
from app.core.rate_limit import InMemoryRateLimitMiddleware
from app.services.monitoring_service import MonitoringService

configure_logging()


@asynccontextmanager
async def lifespan(app: FastAPI):
    mongo_manager.connect()
    await mongo_manager.ping()
    monitor = MonitoringService(repo=get_memory_repo(), event_bus=get_event_bus())
    app.state.monitor = monitor
    monitor.start(interval_seconds=settings.monitor_interval_seconds)
    yield
    await monitor.stop()
    mongo_manager.close()


app = FastAPI(
    title=settings.app_name,
    description="Autonomous multi-agent protection platform for international students.",
    version=settings.app_version,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins if settings.cors_origins != ["*"] else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(
    InMemoryRateLimitMiddleware,
    window_seconds=settings.rate_limit_window_seconds,
    max_requests=settings.rate_limit_max_requests,
)

register_exception_handlers(app)

app.include_router(health.router)
app.include_router(planner.router)
app.include_router(legacy.router)
app.include_router(alerts.router)
app.include_router(stream.router)
app.include_router(risk.router)

