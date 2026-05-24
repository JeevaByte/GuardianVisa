from __future__ import annotations

import re
from datetime import datetime


class VisaComplianceAgent:
    async def run(self, user_message: str, memory_context: dict) -> dict:
        days_until_expiry = self._extract_days(user_message)
        proposed_hours = self._extract_hours(user_message)
        visa_signal = 20 if days_until_expiry is None else max(30, min(100, 100 - (days_until_expiry * 2.2)))
        compliance_signal = max(0, min(100, proposed_hours * 4))
        return {
            "days_until_expiry": days_until_expiry,
            "proposed_hours": proposed_hours,
            "visa_signal": visa_signal,
            "compliance_signal": compliance_signal,
            "analysis": "Visa expiry and work-hours constraints analyzed.",
        }

    @staticmethod
    def _extract_days(text: str) -> int | None:
        match = re.search(r"(\d{1,3})\s*days?", text.lower())
        if match:
            return int(match.group(1))
        dt_match = re.search(r"(20\d{2}-\d{2}-\d{2})", text)
        if not dt_match:
            return None
        try:
            target = datetime.strptime(dt_match.group(1), "%Y-%m-%d").date()
            return (target - datetime.utcnow().date()).days
        except Exception:
            return None

    @staticmethod
    def _extract_hours(text: str) -> float:
        match = re.search(r"(\d{1,2})\s*hours?", text.lower())
        return float(match.group(1)) if match else 0.0

