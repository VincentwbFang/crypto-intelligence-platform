from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field, model_validator

from app.backtesting.strategies import STRATEGIES
from app.core.config import settings


class BacktestRunRequest(BaseModel):
    symbol: str
    timeframe: str = settings.BACKTEST_DEFAULT_TIMEFRAME
    strategy_name: str
    start_date: datetime
    end_date: datetime
    initial_capital: float = Field(default=settings.BACKTEST_DEFAULT_INITIAL_CAPITAL, gt=0)
    fee_bps: float = Field(default=settings.BACKTEST_DEFAULT_FEE_BPS, ge=0)
    slippage_bps: float = Field(default=settings.BACKTEST_DEFAULT_SLIPPAGE_BPS, ge=0)
    max_position_pct: float = Field(
        default=settings.BACKTEST_DEFAULT_MAX_POSITION_PCT,
        gt=0,
        le=1,
    )
    parameters: dict[str, Any] = Field(default_factory=dict)

    @model_validator(mode="after")
    def validate_request(self) -> "BacktestRunRequest":
        if self.start_date >= self.end_date:
            raise ValueError("start_date must be before end_date.")
        if self.strategy_name not in STRATEGIES:
            raise ValueError(f"Unsupported strategy_name: {self.strategy_name}")
        return self


class BacktestMetricsResponse(BaseModel):
    initial_capital: float
    final_equity: float
    total_return_pct: float
    max_drawdown_pct: float
    sharpe_ratio: float | None = None
    win_rate: float
    profit_factor: float | None = None
    total_trades: int
    average_trade_return_pct: float
    average_holding_period_bars: float
    exposure_time_pct: float


class BacktestTradeResponse(BaseModel):
    id: int | None = None
    run_id: str | None = None
    symbol: str
    side: str
    entry_time: str
    entry_price: float
    exit_time: str
    exit_price: float
    quantity: float
    notional: float
    fee: float
    slippage: float
    pnl: float
    pnl_pct: float
    holding_period_bars: int
    exit_reason: str
    created_at: str | None = None


class EquityCurvePoint(BaseModel):
    timestamp: str
    equity: float
    cash: float
    position_value: float
    drawdown_pct: float


class BacktestRunResponse(BaseModel):
    run_id: str
    symbol: str
    timeframe: str
    strategy_name: str
    parameters: dict[str, Any]
    initial_capital: float
    final_equity: float | None = None
    total_return_pct: float | None = None
    max_drawdown_pct: float | None = None
    sharpe_ratio: float | None = None
    win_rate: float | None = None
    profit_factor: float | None = None
    total_trades: int | None = None
    status: str
    started_at: str | None = None
    completed_at: str | None = None
    error_message: str | None = None
    created_at: str | None = None


class BacktestDetailResponse(BacktestRunResponse):
    metrics: BacktestMetricsResponse | dict[str, Any] | None = None
    trades: list[BacktestTradeResponse] = Field(default_factory=list)
    equity_curve: list[EquityCurvePoint] = Field(default_factory=list)
    data_quality: dict[str, Any] | None = None
    disclaimer: str | None = None


class BacktestListResponse(BaseModel):
    data: list[BacktestRunResponse]


class BacktestStrategyInfo(BaseModel):
    name: str
    description: str
    default_parameters: dict[str, Any]
    supported_positioning: str


class BacktestStrategiesResponse(BaseModel):
    data: list[BacktestStrategyInfo]


class BacktestTradesResponse(BaseModel):
    run_id: str
    data: list[BacktestTradeResponse]


class BacktestEquityCurveResponse(BaseModel):
    run_id: str
    data: list[EquityCurvePoint]


class BacktestDeleteResponse(BaseModel):
    run_id: str
    deleted: bool


class AIBacktestExplanationResponse(BaseModel):
    enabled: bool
    message: str | None = None
    error: str | None = None
    plain_english_summary: str | None = None
    performance_interpretation: list[str] | None = None
    risk_interpretation: list[str] | None = None
    strategy_behavior: list[str] | None = None
    main_weaknesses: list[str] | None = None
    what_to_validate_next: list[str] | None = None
    limitations: list[str] | None = None
    disclaimer: str | None = None
    compliance_warnings: list[str] | None = None
