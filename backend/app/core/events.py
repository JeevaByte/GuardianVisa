from __future__ import annotations

import asyncio
import json
import uuid
from dataclasses import asdict, dataclass
from datetime import datetime, timezone


@dataclass(slots=True)
class ActivityEvent:
    event_id: str
    event_type: str
    status: str
    message: str
    confidence: float | None = None
    payload: dict | None = None
    timestamp: str | None = None

    def to_sse(self) -> str:
        body = asdict(self)
        if not body.get("timestamp"):
            body["timestamp"] = datetime.now(timezone.utc).isoformat()
        return f"event: {self.event_type}\ndata: {json.dumps(body)}\n\n"


class EventBus:
    def __init__(self) -> None:
        self._subscribers: set[asyncio.Queue[str]] = set()

    def make_event(
        self,
        event_type: str,
        status: str,
        message: str,
        confidence: float | None = None,
        payload: dict | None = None,
    ) -> ActivityEvent:
        return ActivityEvent(
            event_id=str(uuid.uuid4()),
            event_type=event_type,
            status=status,
            message=message,
            confidence=confidence,
            payload=payload or {},
            timestamp=datetime.now(timezone.utc).isoformat(),
        )

    async def publish(self, event: ActivityEvent) -> None:
        dead = []
        for queue in self._subscribers:
            try:
                queue.put_nowait(event.to_sse())
            except Exception:
                dead.append(queue)
        for queue in dead:
            self._subscribers.discard(queue)

    async def subscribe(self) -> asyncio.Queue[str]:
        queue: asyncio.Queue[str] = asyncio.Queue(maxsize=256)
        self._subscribers.add(queue)
        return queue

    def unsubscribe(self, queue: asyncio.Queue[str]) -> None:
        self._subscribers.discard(queue)

