from __future__ import annotations

import asyncio

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse

from app.api.deps import get_event_bus
from app.core.events import EventBus

router = APIRouter(prefix="/api", tags=["observability"])


@router.get("/activity/stream")
async def stream_activity(event_bus: EventBus = Depends(get_event_bus)):
    async def event_generator():
        queue = await event_bus.subscribe()
        try:
            yield ": connected\n\n"
            while True:
                try:
                    yield await asyncio.wait_for(queue.get(), timeout=20)
                except asyncio.TimeoutError:
                    yield ": keepalive\n\n"
        finally:
            event_bus.unsubscribe(queue)

    return StreamingResponse(event_generator(), media_type="text/event-stream")

