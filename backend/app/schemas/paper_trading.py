from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field

from app.core.config import settings


class PaperAccountCreateRequest(BaseModel):
    name: str = "Main Paper Account"
    initial_balance: float = Field(default=settings.PAPER_DEFAULT_INITIAL_BALANCE, gt=0)


class PaperAccountResponse(BaseModel):
    id: int | None = None
    account_id: str
    name: str
    initial_balance: float
    cash_balance: float
    equity: float
    realized_pnl: float
    unrealized_pnl: float
    total_fees: float
    status: str
    created_at: str | None = None
    updated_at: str | None = None


class PaperOrderCreateRequest(BaseModel):
    account_id: str
    symbol: str
    timeframe: str = "1h"
    side: Literal["buy", "sell"]
    order_type: Literal["market"] = "market"
    notional: float = Field(gt=0)
    reason: str | None = "Manual research-only simulated order"


class PaperOrderResponse(BaseModel):
    id: int | None = None
    order_id: str
    account_id: str
    symbol: str
    timeframe: str
    side: str
    order_type: str
    quantity: float | None = None
    notional: float
    requested_price: float | None = None
    filled_price: float | None = None
    status: str
    source: str | None = None
    signal_id: str | None = None
    reason: str | None = None
    fee: float | None = None
    slippage: float | None = None
    created_at: str | None = None
    filled_at: str | None = None
    cancelled_at: str | None = None
    risk: dict[str, Any] | None = None


class PaperPositionResponse(BaseModel):
    id: int | None = None
    account_id: str
    symbol: str
    quantity: float
    average_entry_price: float
    current_price: float
    market_value: float
    unrealized_pnl: float
    unrealized_pnl_pct: float
    opened_at: str | None = None
    updated_at: str | None = None
    status: str


class PaperTradeResponse(BaseModel):
    id: int | None = None
    trade_id: str | None = None
    account_id: str | None = None
    symbol: str
    side: str
    entry_time: str | None = None
    entry_price: float
    exit_time: str | None = None
    exit_price: float | None = None
    quantity: float | None = None
    notional: float | None = None
    fee: float | None = None
    slippage: float | None = None
    realized_pnl: float | None = None
    realized_pnl_pct: float | None = None
    source: str | None = None
    strategy_name: str | None = None
    exit_reason: str | None = None
    created_at: str | None = None


class PaperEquitySnapshotResponse(BaseModel):
    id: int | None = None
    account_id: str
    timestamp: str | None = None
    cash_balance: float
    equity: float
    realized_pnl: float
    unrealized_pnl: float
    total_fees: float
    open_positions_count: int
    created_at: str | None = None


class PaperPortfolioResponse(BaseModel):
    account: PaperAccountResponse
    positions: list[PaperPositionResponse]
    open_orders: list[PaperOrderResponse]
    equity_snapshot: PaperEquitySnapshotResponse | None = None


class PaperPerformanceResponse(BaseModel):
    initial_balance: float
    current_equity: float
    total_return_pct: float
    realized_pnl: float
    unrealized_pnl: float
    total_fees: float
    total_trades: int
    win_rate: float
    profit_factor: float | None = None
    max_drawdown_pct: float
    open_positions_count: int
    exposure_pct: float


class SignalPaperExecutionRequest(BaseModel):
    symbol: str
    timeframe: str = "1h"
    limit: int = Field(default=settings.SIGNAL_DEFAULT_LIMIT, ge=1, le=1000)


class SignalPaperExecutionResponse(BaseModel):
    enabled: bool
    message: str | None = None
    signal: dict[str, Any] | None = None
    action_taken: str | None = None
    order: PaperOrderResponse | dict[str, Any] | None = None
    reason: str | None = None
    disclaimer: str


class AIPaperTradingExplanationResponse(BaseModel):
    enabled: bool
    message: str | None = None
    error: str | None = None
    plain_english_summary: str | None = None
    performance_observations: list[str] | None = None
    risk_observations: list[str] | None = None
    position_notes: list[str] | None = None
    what_to_monitor: list[str] | None = None
    limitations: list[str] | None = None
    disclaimer: str | None = None
    compliance_warnings: list[str] | None = None


class PaperAccountListResponse(BaseModel):
    data: list[PaperAccountResponse]


class PaperOrderListResponse(BaseModel):
    data: list[PaperOrderResponse]


class PaperPositionListResponse(BaseModel):
    data: list[PaperPositionResponse]


class PaperTradeListResponse(BaseModel):
    data: list[PaperTradeResponse]
