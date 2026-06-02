from typing import Any

from pydantic import BaseModel, Field


class AlertCandidate(BaseModel):
    symbol: str
    timeframe: str
    timestamp: str
    alert_type: str
    severity: str
    title: str
    message: str
    source: str | None = None
    signal_score: float | None = None
    risk_level: str | None = None
    setup_type: str | None = None
    dedup_key: str
    raw_payload: dict[str, Any] | None = None


class AlertResponse(AlertCandidate):
    id: int
    status: str
    created_at: str | None = None
    updated_at: str | None = None
    resolved_at: str | None = None


class AlertListResponse(BaseModel):
    data: list[AlertResponse]


class AlertEvaluateRequest(BaseModel):
    symbols: list[str] = Field(default_factory=list)
    timeframe: str = "1h"
    limit: int = Field(default=200, ge=2, le=1000)
    send_notifications: bool = False


class AlertEvaluateResult(BaseModel):
    symbol: str
    timeframe: str
    generated_alerts: int
    deduplicated_alerts: int
    alerts: list[AlertResponse]


class AlertEvaluateResponse(BaseModel):
    symbols: list[str]
    timeframe: str
    results: list[AlertEvaluateResult]
    generated_alerts: int
    deduplicated_alerts: int
    alerts: list[AlertResponse]
    notifications: list[dict[str, Any]] | None = None


class AlertStatusUpdateRequest(BaseModel):
    status: str


class AIAlertExplanationResponse(BaseModel):
    enabled: bool
    message: str | None = None
    error: str | None = None
    plain_english_summary: str | None = None
    why_triggered: list[str] | None = None
    risk_context: list[str] | None = None
    what_to_monitor: list[str] | None = None
    limitations: list[str] | None = None
    disclaimer: str | None = None
    compliance_warnings: list[str] | None = None


class NotificationTestRequest(BaseModel):
    channel: str = "webhook"


class NotificationResult(BaseModel):
    alert_id: int | None = None
    status: str
    deliveries: list[dict[str, Any]]
