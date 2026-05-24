from __future__ import annotations

from app.domain.models import RiskScore, Severity


class ActionEngine:
    def generate(self, message: str, risk: RiskScore, retrieved_context: list[dict]) -> dict:
        citations = [ctx.get("citation", "") for ctx in retrieved_context if ctx.get("citation")]
        return {
            "tasks": self._task_list(risk),
            "timeline": self._timeline(risk),
            "draft_email": self._draft_email(message, risk),
            "escalation_plan": self._escalation(risk),
            "compliance_checklist": self._checklist(risk),
            "citations": citations,
        }

    def _task_list(self, risk: RiskScore) -> list[dict]:
        tasks = [
            {"task": "Update student visa and sponsorship profile", "priority": "HIGH"},
            {"task": "Review policy citations and legal obligations", "priority": "MEDIUM"},
            {"task": "Prepare communication draft for university/legal office", "priority": "MEDIUM"},
        ]
        if risk.severity in (Severity.HIGH, Severity.CRITICAL):
            tasks.insert(0, {"task": "Trigger emergency legal workflow", "priority": "URGENT"})
        return tasks

    def _timeline(self, risk: RiskScore) -> list[dict]:
        day1 = "Immediate mitigation and document collection"
        if risk.severity == Severity.CRITICAL:
            day1 = "Immediate escalation and legal outreach"
        return [
            {"day": 1, "focus": day1},
            {"day": 2, "focus": "University and legal advisor coordination"},
            {"day": 3, "focus": "Compliance submission and follow-up"},
        ]

    def _draft_email(self, message: str, risk: RiskScore) -> str:
        urgency = "URGENT" if risk.severity in (Severity.HIGH, Severity.CRITICAL) else "Time-sensitive"
        return (
            f"Subject: {urgency} support request for student visa compliance\n\n"
            f"Dear International Student Office,\n\n"
            f"I need support regarding: {message[:220]}\n"
            f"Current assessed severity: {risk.severity.value}.\n"
            "Please advise immediate compliant next steps and available emergency pathways.\n\n"
            "Kind regards,\nStudent"
        )

    def _escalation(self, risk: RiskScore) -> list[str]:
        if risk.severity == Severity.CRITICAL:
            return ["Create critical alert", "Trigger legal resource escalation", "24h follow-up monitor"]
        if risk.severity == Severity.HIGH:
            return ["Create high-priority alert", "Trigger legal support workflow"]
        return ["Continue periodic monitoring"]

    def _checklist(self, risk: RiskScore) -> list[str]:
        checklist = [
            "Verify current visa expiry and sponsorship status",
            "Check weekly work-hour compliance against visa cap",
            "Preserve all evidence of communication and offers",
        ]
        if risk.breakdown.scam >= 40:
            checklist.append("Report suspicious communication to fraud authority")
        return checklist

