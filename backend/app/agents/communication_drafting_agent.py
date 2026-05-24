from __future__ import annotations


class CommunicationDraftingAgent:
    async def run(self, user_message: str, severity: str) -> dict:
        urgency = "urgent" if severity in {"HIGH", "CRITICAL"} else "important"
        draft = (
            f"Subject: {urgency.title()} support request regarding student visa compliance\n\n"
            "Dear International Office,\n\n"
            f"I need assistance with the following issue: {user_message[:250]}\n"
            "Could you please advise immediate compliant steps and available support resources?\n\n"
            "Sincerely,\nStudent"
        )
        return {"draft": draft, "analysis": "Communication draft created."}

