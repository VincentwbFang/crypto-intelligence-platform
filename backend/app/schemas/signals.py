from typing import Any

from pydantic import BaseModel


class SignalScores(BaseModel):
    trend_score: float
    momentum_score: float
    volume_score: float
    volatility_risk_score: float
    relative_strength_score: float
    overall_signal_score: float


class SignalIndicators(BaseModel):
    ema_20: float | None = None
    ema_50: float | None = None
    ema_200: float | None = None
    rsi_14: float | None = None
    macd: float | None = None
    macd_signal: float | None = None
    macd_histogram: float | None = None
    atr_14: float | None = None
    volume_zscore_20: float | None = None
    realized_volatility_20: float | None = None


class RelativeStrengthResult(BaseModel):
    reference_symbol: str
    return_24h: float | None = None
    reference_return_24h: float | None = None
    relative_return_24h: float | None = None
    return_7d: float | None = None
    reference_return_7d: float | None = None
    relative_return_7d: float | None = None
    relative_strength_score: float
    explanation: str


class DataQualityResult(BaseModel):
    candle_count: int
    min_required_candles: int
    has_sufficient_data: bool
    missing_indicator_warning: bool


class AISignalExplanationResponse(BaseModel):
    enabled: bool
    message: str | None = None
    error: str | None = None
    plain_english_summary: str | None = None
    why_this_signal: list[str] | None = None
    main_risks: list[str] | None = None
    what_to_monitor: list[str] | None = None
    confidence_commentary: str | None = None
    limitations: list[str] | None = None
    disclaimer: str | None = None
    compliance_warnings: list[str] | None = None


class SignalResponse(BaseModel):
    symbol: str
    timeframe: str
    timestamp: str | None = None
    latest_close: float | None = None
    scores: SignalScores
    signal_direction: str
    setup_type: str
    risk_level: str
    indicators: SignalIndicators
    relative_strength: RelativeStrengthResult
    risk_notes: list[str]
    data_quality: DataQualityResult
    explanation: str
    ai_explanation: AISignalExplanationResponse | dict[str, Any] | None = None


class SignalRankResponse(BaseModel):
    symbols: list[str]
    timeframe: str
    data: list[SignalResponse]

