from __future__ import annotations


class EmergencyRecoveryAgent:
    async def run(self, user_message: str, memory_context: dict) -> dict:
        text = user_message.lower()
        terms = ["lost sponsorship", "visa expired", "terminated", "deport", "ice notice", "overstay"]
        matches = [term for term in terms if term in text]
        signal = min(100, 25 + len(matches) * 20) if matches else 10
        return {
            "legal_urgency_signal": signal,
            "incident_matches": matches,
            "analysis": "Emergency immigration incident analyzed.",
        }

