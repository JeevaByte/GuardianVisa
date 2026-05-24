from __future__ import annotations

import asyncio
import logging

from app.agents.timeline_monitoring_agent import TimelineMonitoringAgent
from app.core.events import EventBus
from app.repositories.memory_repository import MemoryRepository

log = logging.getLogger(__name__)


class MonitoringService:
    def __init__(self, repo: MemoryRepository, event_bus: EventBus):
        self.repo = repo
        self.event_bus = event_bus
        self.monitor_agent = TimelineMonitoringAgent(repo)
        self._task: asyncio.Task | None = None

    def start(self, interval_seconds: int) -> None:
        if self._task and not self._task.done():
            return
        self._task = asyncio.create_task(self._loop(interval_seconds))

    async def _loop(self, interval_seconds: int) -> None:
        while True:
            try:
                result = await self.monitor_agent.run_cycle()
                await self.repo.save_monitor_run("timeline_monitoring_agent", result)
                await self.event_bus.publish(
                    self.event_bus.make_event(
                        event_type="monitor.run.completed",
                        status="completed",
                        message=f"Monitoring run completed with {result.get('alerts_created', 0)} alerts",
                        confidence=0.79,
                        payload=result,
                    )
                )
            except asyncio.CancelledError:
                break
            except Exception as exc:
                log.warning("Monitoring loop error: %s", exc)
            await asyncio.sleep(interval_seconds)

    async def stop(self) -> None:
        if self._task and not self._task.done():
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
