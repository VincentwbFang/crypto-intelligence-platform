from pydantic import BaseModel


class PaperTradeExample(BaseModel):
    enabled: bool
    scenario: str | None = None
    entry_condition: str | None = None
    invalidation_condition: str | None = None
    risk_control: str | None = None


class AISignalSummaryResponse(BaseModel):
    enabled: bool
    message: str | None = None
    error: str | None = None
    symbol: str | None = None
    timeframe: str | None = None
    market_bias: str | None = None
    setup_type: str | None = None
    confidence_score: float | None = None
    risk_level: str | None = None
    trend_explanation: str | None = None
    volume_explanation: str | None = None
    volatility_explanation: str | None = None
    invalidation_conditions: list[str] | None = None
    watch_zones: list[str] | None = None
    risk_notes: list[str] | None = None
    paper_trade_example: PaperTradeExample | None = None
    compliance_disclaimer: str | None = None
    compliance_warnings: list[str] | None = None


class ComplianceGuardrailResponse(BaseModel):
    safe: bool
    warnings: list[str]
    sanitized_output: dict
