from __future__ import annotations

import json
import os
from dataclasses import dataclass, field


@dataclass(slots=True)
class Settings:
    app_name: str = "GuardianVisa Platform API"
    app_version: str = "2.0.0"
    environment: str = field(default_factory=lambda: os.getenv("ENVIRONMENT", "development"))
    mongodb_uri: str = field(default_factory=lambda: os.getenv("MONGODB_URI", "mongodb://localhost:27017"))
    mongodb_db_name: str = field(default_factory=lambda: os.getenv("MONGODB_DB_NAME", "guardianvisa"))
    cors_origins: list[str] = field(default_factory=lambda: os.getenv("CORS_ORIGINS", "*").split(","))
    rate_limit_window_seconds: int = field(default_factory=lambda: int(os.getenv("RATE_LIMIT_WINDOW_SECONDS", "60")))
    rate_limit_max_requests: int = field(default_factory=lambda: int(os.getenv("RATE_LIMIT_MAX_REQUESTS", "120")))
    monitor_interval_seconds: int = field(default_factory=lambda: int(os.getenv("MONITOR_INTERVAL_SECONDS", "900")))
    risk_weights_raw: str = field(default_factory=lambda: os.getenv("RISK_WEIGHTS_JSON", ""))
    risk_thresholds_raw: str = field(default_factory=lambda: os.getenv("RISK_THRESHOLDS_JSON", ""))

    @property
    def risk_weights(self) -> dict[str, float]:
        default = {
            "visa": 0.32,
            "scam": 0.2,
            "legal_urgency": 0.22,
            "financial": 0.12,
            "compliance": 0.14,
        }
        if not self.risk_weights_raw:
            return default
        try:
            parsed = json.loads(self.risk_weights_raw)
            if isinstance(parsed, dict):
                return {**default, **{k: float(v) for k, v in parsed.items()}}
        except Exception:
            pass
        return default

    @property
    def risk_thresholds(self) -> dict[str, int]:
        default = {
            "SAFE": 0,
            "LOW": 20,
            "MEDIUM": 40,
            "HIGH": 65,
            "CRITICAL": 85,
        }
        if not self.risk_thresholds_raw:
            return default
        try:
            parsed = json.loads(self.risk_thresholds_raw)
            if isinstance(parsed, dict):
                return {**default, **{k: int(v) for k, v in parsed.items()}}
        except Exception:
            pass
        return default


settings = Settings()

