from __future__ import annotations

from app.core.config import settings
from app.domain.models import RiskBreakdown, RiskScore, Severity


class RiskEngine:
    def __init__(self) -> None:
        self.weights = settings.risk_weights
        self.thresholds = settings.risk_thresholds

    def score(self, signals: dict[str, float]) -> RiskScore:
        normalized_signals = {
            "visa": self._clamp(signals.get("visa", 0.0)),
            "scam": self._clamp(signals.get("scam", 0.0)),
            "legal_urgency": self._clamp(signals.get("legal_urgency", 0.0)),
            "financial": self._clamp(signals.get("financial", 0.0)),
            "compliance": self._clamp(signals.get("compliance", 0.0)),
        }
        weighted = sum(normalized_signals[k] * self.weights.get(k, 0.0) for k in normalized_signals)
        severity = self._severity(weighted)
        confidence = self._confidence(normalized_signals)
        reasons = self._reasons(normalized_signals)
        return RiskScore(
            normalized_score=round(weighted, 2),
            confidence=round(confidence, 2),
            severity=severity,
            breakdown=RiskBreakdown(**normalized_signals),
            reasons=reasons,
            triggered_actions=self._actions(severity),
        )

    @staticmethod
    def _clamp(value: float) -> float:
        return max(0.0, min(100.0, float(value)))

    def _severity(self, score: float) -> Severity:
        if score >= self.thresholds["CRITICAL"]:
            return Severity.CRITICAL
        if score >= self.thresholds["HIGH"]:
            return Severity.HIGH
        if score >= self.thresholds["MEDIUM"]:
            return Severity.MEDIUM
        if score >= self.thresholds["LOW"]:
            return Severity.LOW
        return Severity.SAFE

    @staticmethod
    def _confidence(signals: dict[str, float]) -> float:
        high = sum(1 for value in signals.values() if value >= 50)
        spread = max(signals.values()) - min(signals.values())
        return min(0.55 + high * 0.08 + min(spread / 200.0, 0.2), 0.98)

    @staticmethod
    def _reasons(signals: dict[str, float]) -> list[str]:
        reasons = [f"{k} risk signal is elevated ({v:.0f}/100)" for k, v in signals.items() if v >= 70]
        return reasons or ["No critical signal spikes detected"]

    @staticmethod
    def _actions(severity: Severity) -> list[str]:
        mapping = {
            Severity.SAFE: ["Continue monitoring"],
            Severity.LOW: ["Provide preventive guidance"],
            Severity.MEDIUM: ["Create action checklist", "Schedule follow-up"],
            Severity.HIGH: ["Escalate to legal resource agent", "Generate communication draft"],
            Severity.CRITICAL: ["Immediate alert", "Emergency plan", "Legal escalation"],
        }
        return mapping[severity]

