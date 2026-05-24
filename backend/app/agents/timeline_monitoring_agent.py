from __future__ import annotations

from datetime import datetime, timezone

from app.repositories.memory_repository import MemoryRepository


class TimelineMonitoringAgent:
    def __init__(self, repo: MemoryRepository):
        self.repo = repo

    async def run_cycle(self) -> dict:
        alerts = []
        users = await self.repo.list_users(limit=100)
        now = datetime.now(timezone.utc)
        for user in users:
            expiry_text = user.get("visa_expiry")
            if not expiry_text:
                continue
            try:
                expiry = datetime.fromisoformat(expiry_text.replace("Z", "+00:00"))
                days = (expiry - now).days
            except Exception:
                continue
            if days <= 30:
                severity = "CRITICAL" if days <= 7 else "HIGH"
                alerts.append(
                    await self.repo.create_alert(
                        user_id=user.get("user_id", "unknown"),
                        severity=severity,
                        message=f"Visa expiry in {days} days.",
                        metadata={"monitor": "visa_expiry", "days": days},
                    )
                )
        return {"run_at": now.isoformat(), "alerts_created": len(alerts), "alerts": alerts}

