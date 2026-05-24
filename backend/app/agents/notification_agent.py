from __future__ import annotations


class NotificationAgent:
    async def run(self, severity: str, actions: list[str]) -> dict:
        channel = "email+sms" if severity in {"HIGH", "CRITICAL"} else "email"
        return {"notification_channel": channel, "notification_actions": actions}

