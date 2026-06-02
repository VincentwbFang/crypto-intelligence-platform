from datetime import datetime
from decimal import Decimal

from sqlalchemy import Boolean, DateTime, ForeignKey, JSON, Numeric, String, Text, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Token(Base):
    __tablename__ = "tokens"

    id: Mapped[int] = mapped_column(primary_key=True)
    symbol: Mapped[str] = mapped_column(String(32), index=True, nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    coingecko_id: Mapped[str | None] = mapped_column(String(255), unique=True)
    chain: Mapped[str | None] = mapped_column(String(64), index=True)
    category: Mapped[str | None] = mapped_column(String(64), index=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )


class OHLCV(Base):
    __tablename__ = "ohlcv"
    __table_args__ = (
        UniqueConstraint(
            "exchange",
            "symbol",
            "timeframe",
            "timestamp",
            name="uq_ohlcv_exchange_symbol_timeframe_timestamp",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    exchange: Mapped[str] = mapped_column(String(64), index=True, nullable=False)
    symbol: Mapped[str] = mapped_column(String(32), index=True, nullable=False)
    timeframe: Mapped[str] = mapped_column(String(16), index=True, nullable=False)
    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        index=True,
        nullable=False,
    )
    open: Mapped[Decimal] = mapped_column(Numeric(24, 10), nullable=False)
    high: Mapped[Decimal] = mapped_column(Numeric(24, 10), nullable=False)
    low: Mapped[Decimal] = mapped_column(Numeric(24, 10), nullable=False)
    close: Mapped[Decimal] = mapped_column(Numeric(24, 10), nullable=False)
    volume: Mapped[Decimal] = mapped_column(Numeric(32, 10), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )


class Signal(Base):
    __tablename__ = "signals"
    __table_args__ = (
        UniqueConstraint(
            "symbol",
            "timeframe",
            "timestamp",
            "signal_type",
            name="uq_signals_symbol_timeframe_timestamp_type",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    symbol: Mapped[str] = mapped_column(String(32), index=True, nullable=False)
    timeframe: Mapped[str] = mapped_column(
        String(16),
        index=True,
        nullable=False,
        server_default="1h",
    )
    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        index=True,
        nullable=False,
    )
    signal_type: Mapped[str] = mapped_column(String(64), index=True, nullable=False)
    score: Mapped[Decimal | None] = mapped_column(Numeric(10, 4))
    direction: Mapped[str | None] = mapped_column(String(16))
    reason: Mapped[str | None] = mapped_column(Text)
    confidence: Mapped[Decimal | None] = mapped_column(Numeric(10, 4))
    setup_type: Mapped[str | None] = mapped_column(String(64), index=True)
    risk_level: Mapped[str | None] = mapped_column(String(32), index=True)
    raw_payload: Mapped[dict | None] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )


class Alert(Base):
    __tablename__ = "alerts"

    id: Mapped[int] = mapped_column(primary_key=True)
    workspace_id: Mapped[str | None] = mapped_column(String(64), index=True)
    created_by_user_id: Mapped[str | None] = mapped_column(String(64), index=True)
    symbol: Mapped[str] = mapped_column(String(32), index=True, nullable=False)
    timeframe: Mapped[str] = mapped_column(
        String(16),
        index=True,
        nullable=False,
        server_default="1h",
    )
    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        index=True,
        nullable=False,
    )
    alert_type: Mapped[str] = mapped_column(String(64), index=True, nullable=False)
    severity: Mapped[str] = mapped_column(String(32), index=True, nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(String(32), index=True, nullable=False)
    source: Mapped[str | None] = mapped_column(String(64), index=True)
    signal_score: Mapped[Decimal | None] = mapped_column(Numeric(10, 4))
    risk_level: Mapped[str | None] = mapped_column(String(32), index=True)
    setup_type: Mapped[str | None] = mapped_column(String(64), index=True)
    dedup_key: Mapped[str] = mapped_column(String(512), index=True, nullable=False)
    raw_payload: Mapped[dict | None] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        index=True,
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
    resolved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))


class PaperAccount(Base):
    __tablename__ = "paper_accounts"

    id: Mapped[int] = mapped_column(primary_key=True)
    workspace_id: Mapped[str | None] = mapped_column(String(64), index=True)
    created_by_user_id: Mapped[str | None] = mapped_column(String(64), index=True)
    account_id: Mapped[str] = mapped_column(String(64), unique=True, index=True, nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    initial_balance: Mapped[Decimal] = mapped_column(Numeric(24, 8), nullable=False)
    cash_balance: Mapped[Decimal] = mapped_column(Numeric(24, 8), nullable=False)
    equity: Mapped[Decimal] = mapped_column(Numeric(24, 8), nullable=False)
    realized_pnl: Mapped[Decimal] = mapped_column(Numeric(24, 8), nullable=False, default=0)
    unrealized_pnl: Mapped[Decimal] = mapped_column(Numeric(24, 8), nullable=False, default=0)
    total_fees: Mapped[Decimal] = mapped_column(Numeric(24, 8), nullable=False, default=0)
    status: Mapped[str] = mapped_column(String(32), index=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        index=True,
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )


class PaperOrder(Base):
    __tablename__ = "paper_orders"

    id: Mapped[int] = mapped_column(primary_key=True)
    workspace_id: Mapped[str | None] = mapped_column(String(64), index=True)
    created_by_user_id: Mapped[str | None] = mapped_column(String(64), index=True)
    order_id: Mapped[str] = mapped_column(String(64), unique=True, index=True, nullable=False)
    account_id: Mapped[str] = mapped_column(String(64), index=True, nullable=False)
    symbol: Mapped[str] = mapped_column(String(32), index=True, nullable=False)
    timeframe: Mapped[str] = mapped_column(String(16), nullable=False)
    side: Mapped[str] = mapped_column(String(16), nullable=False)
    order_type: Mapped[str] = mapped_column(String(32), nullable=False)
    quantity: Mapped[Decimal | None] = mapped_column(Numeric(32, 12))
    notional: Mapped[Decimal] = mapped_column(Numeric(32, 10), nullable=False)
    requested_price: Mapped[Decimal | None] = mapped_column(Numeric(24, 10))
    filled_price: Mapped[Decimal | None] = mapped_column(Numeric(24, 10))
    status: Mapped[str] = mapped_column(String(32), index=True, nullable=False)
    source: Mapped[str | None] = mapped_column(String(64))
    signal_id: Mapped[str | None] = mapped_column(String(64))
    reason: Mapped[str | None] = mapped_column(Text)
    fee: Mapped[Decimal | None] = mapped_column(Numeric(24, 10))
    slippage: Mapped[Decimal | None] = mapped_column(Numeric(24, 10))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        index=True,
        server_default=func.now(),
        nullable=False,
    )
    filled_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    cancelled_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))


class PaperPosition(Base):
    __tablename__ = "paper_positions"

    id: Mapped[int] = mapped_column(primary_key=True)
    workspace_id: Mapped[str | None] = mapped_column(String(64), index=True)
    account_id: Mapped[str] = mapped_column(String(64), index=True, nullable=False)
    symbol: Mapped[str] = mapped_column(String(32), index=True, nullable=False)
    quantity: Mapped[Decimal] = mapped_column(Numeric(32, 12), nullable=False)
    average_entry_price: Mapped[Decimal] = mapped_column(Numeric(24, 10), nullable=False)
    current_price: Mapped[Decimal] = mapped_column(Numeric(24, 10), nullable=False)
    market_value: Mapped[Decimal] = mapped_column(Numeric(32, 10), nullable=False)
    unrealized_pnl: Mapped[Decimal] = mapped_column(Numeric(32, 10), nullable=False)
    unrealized_pnl_pct: Mapped[Decimal] = mapped_column(Numeric(12, 6), nullable=False)
    opened_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
    status: Mapped[str] = mapped_column(String(32), index=True, nullable=False)


class PaperTrade(Base):
    __tablename__ = "paper_trades"

    id: Mapped[int] = mapped_column(primary_key=True)
    workspace_id: Mapped[str | None] = mapped_column(String(64), index=True)
    created_by_user_id: Mapped[str | None] = mapped_column(String(64), index=True)
    trade_id: Mapped[str | None] = mapped_column(String(64), unique=True, index=True)
    account_id: Mapped[str | None] = mapped_column(String(64), index=True)
    symbol: Mapped[str] = mapped_column(String(32), index=True, nullable=False)
    side: Mapped[str] = mapped_column(String(16), index=True, nullable=False)
    entry_time: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        index=True,
        nullable=False,
    )
    entry_price: Mapped[Decimal] = mapped_column(Numeric(24, 10), nullable=False)
    exit_time: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    exit_price: Mapped[Decimal | None] = mapped_column(Numeric(24, 10))
    quantity: Mapped[Decimal | None] = mapped_column(Numeric(32, 12))
    notional: Mapped[Decimal | None] = mapped_column(Numeric(32, 10))
    fee: Mapped[Decimal | None] = mapped_column(Numeric(24, 10))
    slippage: Mapped[Decimal | None] = mapped_column(Numeric(24, 10))
    realized_pnl: Mapped[Decimal | None] = mapped_column(Numeric(32, 10))
    realized_pnl_pct: Mapped[Decimal | None] = mapped_column(Numeric(12, 6))
    source: Mapped[str | None] = mapped_column(String(64))
    strategy_name: Mapped[str | None] = mapped_column(String(128), index=True)
    exit_reason: Mapped[str | None] = mapped_column(String(64))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )


class PaperEquitySnapshot(Base):
    __tablename__ = "paper_equity_snapshots"

    id: Mapped[int] = mapped_column(primary_key=True)
    workspace_id: Mapped[str | None] = mapped_column(String(64), index=True)
    account_id: Mapped[str] = mapped_column(String(64), index=True, nullable=False)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True, nullable=False)
    cash_balance: Mapped[Decimal] = mapped_column(Numeric(24, 8), nullable=False)
    equity: Mapped[Decimal] = mapped_column(Numeric(24, 8), nullable=False)
    realized_pnl: Mapped[Decimal] = mapped_column(Numeric(24, 8), nullable=False)
    unrealized_pnl: Mapped[Decimal] = mapped_column(Numeric(24, 8), nullable=False)
    total_fees: Mapped[Decimal] = mapped_column(Numeric(24, 8), nullable=False)
    open_positions_count: Mapped[int] = mapped_column(nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )


class BacktestRun(Base):
    __tablename__ = "backtest_runs"

    id: Mapped[int] = mapped_column(primary_key=True)
    workspace_id: Mapped[str | None] = mapped_column(String(64), index=True)
    created_by_user_id: Mapped[str | None] = mapped_column(String(64), index=True)
    run_id: Mapped[str] = mapped_column(String(64), unique=True, index=True, nullable=False)
    symbol: Mapped[str] = mapped_column(String(32), index=True, nullable=False)
    timeframe: Mapped[str] = mapped_column(String(16), index=True, nullable=False)
    strategy_name: Mapped[str] = mapped_column(String(128), index=True, nullable=False)
    parameters: Mapped[dict | None] = mapped_column(JSON)
    initial_capital: Mapped[Decimal] = mapped_column(Numeric(24, 8), nullable=False)
    final_equity: Mapped[Decimal | None] = mapped_column(Numeric(24, 8))
    total_return_pct: Mapped[Decimal | None] = mapped_column(Numeric(12, 6))
    max_drawdown_pct: Mapped[Decimal | None] = mapped_column(Numeric(12, 6))
    sharpe_ratio: Mapped[Decimal | None] = mapped_column(Numeric(12, 6))
    win_rate: Mapped[Decimal | None] = mapped_column(Numeric(12, 6))
    profit_factor: Mapped[Decimal | None] = mapped_column(Numeric(18, 6))
    total_trades: Mapped[int | None] = mapped_column()
    status: Mapped[str] = mapped_column(String(32), index=True, nullable=False)
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    error_message: Mapped[str | None] = mapped_column(Text)
    metrics: Mapped[dict | None] = mapped_column(JSON)
    equity_curve: Mapped[list | None] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        index=True,
        server_default=func.now(),
        nullable=False,
    )


class BacktestTrade(Base):
    __tablename__ = "backtest_trades"

    id: Mapped[int] = mapped_column(primary_key=True)
    workspace_id: Mapped[str | None] = mapped_column(String(64), index=True)
    run_id: Mapped[str] = mapped_column(String(64), index=True, nullable=False)
    symbol: Mapped[str] = mapped_column(String(32), index=True, nullable=False)
    side: Mapped[str] = mapped_column(String(16), nullable=False)
    entry_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    entry_price: Mapped[Decimal] = mapped_column(Numeric(24, 10), nullable=False)
    exit_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    exit_price: Mapped[Decimal] = mapped_column(Numeric(24, 10), nullable=False)
    quantity: Mapped[Decimal] = mapped_column(Numeric(32, 12), nullable=False)
    notional: Mapped[Decimal] = mapped_column(Numeric(32, 10), nullable=False)
    fee: Mapped[Decimal] = mapped_column(Numeric(24, 10), nullable=False)
    slippage: Mapped[Decimal] = mapped_column(Numeric(24, 10), nullable=False)
    pnl: Mapped[Decimal] = mapped_column(Numeric(32, 10), nullable=False)
    pnl_pct: Mapped[Decimal] = mapped_column(Numeric(12, 6), nullable=False)
    holding_period_bars: Mapped[int] = mapped_column(nullable=False)
    exit_reason: Mapped[str] = mapped_column(String(64), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[str] = mapped_column(String(64), unique=True, index=True, nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    full_name: Mapped[str | None] = mapped_column(String(255))
    password_hash: Mapped[str] = mapped_column(String(512), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_superuser: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    default_workspace_id: Mapped[str | None] = mapped_column(String(64), index=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
    last_login_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))


class Workspace(Base):
    __tablename__ = "workspaces"

    id: Mapped[int] = mapped_column(primary_key=True)
    workspace_id: Mapped[str] = mapped_column(String(64), unique=True, index=True, nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    owner_user_id: Mapped[str] = mapped_column(String(64), index=True, nullable=False)
    plan: Mapped[str] = mapped_column(String(32), index=True, nullable=False)
    status: Mapped[str] = mapped_column(String(32), index=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )


class WorkspaceMember(Base):
    __tablename__ = "workspace_members"
    __table_args__ = (
        UniqueConstraint("workspace_id", "user_id", name="uq_workspace_member"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    workspace_id: Mapped[str] = mapped_column(String(64), index=True, nullable=False)
    user_id: Mapped[str] = mapped_column(String(64), index=True, nullable=False)
    role: Mapped[str] = mapped_column(String(32), index=True, nullable=False)
    status: Mapped[str] = mapped_column(String(32), index=True, nullable=False)
    invited_by_user_id: Mapped[str | None] = mapped_column(String(64), index=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )


class RefreshToken(Base):
    __tablename__ = "refresh_tokens"

    id: Mapped[int] = mapped_column(primary_key=True)
    token_id: Mapped[str] = mapped_column(String(64), unique=True, index=True, nullable=False)
    user_id: Mapped[str] = mapped_column(String(64), index=True, nullable=False)
    token_hash: Mapped[str] = mapped_column(String(128), index=True, nullable=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True, nullable=False)
    revoked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), index=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )


class UserPreference(Base):
    __tablename__ = "user_preferences"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[str] = mapped_column(String(64), unique=True, index=True, nullable=False)
    default_symbol: Mapped[str] = mapped_column(String(32), nullable=False, default="BTC/USDT")
    default_timeframe: Mapped[str] = mapped_column(String(16), nullable=False, default="1h")
    theme: Mapped[str] = mapped_column(String(32), nullable=False, default="system")
    dashboard_layout: Mapped[dict | None] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )


class Watchlist(Base):
    __tablename__ = "watchlists"

    id: Mapped[int] = mapped_column(primary_key=True)
    watchlist_id: Mapped[str] = mapped_column(String(64), unique=True, index=True, nullable=False)
    workspace_id: Mapped[str] = mapped_column(String(64), index=True, nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    created_by_user_id: Mapped[str] = mapped_column(String(64), index=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )


class WatchlistSymbol(Base):
    __tablename__ = "watchlist_symbols"
    __table_args__ = (
        UniqueConstraint("watchlist_id", "symbol", name="uq_watchlist_symbol"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    watchlist_id: Mapped[str] = mapped_column(String(64), index=True, nullable=False)
    symbol: Mapped[str] = mapped_column(String(32), index=True, nullable=False)
    display_order: Mapped[int] = mapped_column(default=0, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )


class UsageEvent(Base):
    __tablename__ = "usage_events"

    id: Mapped[int] = mapped_column(primary_key=True)
    workspace_id: Mapped[str] = mapped_column(String(64), index=True, nullable=False)
    user_id: Mapped[str | None] = mapped_column(String(64), index=True)
    event_type: Mapped[str] = mapped_column(String(64), index=True, nullable=False)
    quantity: Mapped[int] = mapped_column(nullable=False, default=1)
    event_metadata: Mapped[dict | None] = mapped_column("metadata", JSON)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        index=True,
        server_default=func.now(),
        nullable=False,
    )


class WorkspaceSubscription(Base):
    __tablename__ = "workspace_subscriptions"

    id: Mapped[int] = mapped_column(primary_key=True)
    workspace_id: Mapped[str] = mapped_column(String(64), unique=True, index=True, nullable=False)
    plan: Mapped[str] = mapped_column(String(32), index=True, nullable=False)
    status: Mapped[str] = mapped_column(String(32), index=True, nullable=False)
    current_period_start: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    current_period_end: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    external_customer_id: Mapped[str | None] = mapped_column(String(255))
    external_subscription_id: Mapped[str | None] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )


class RelativeStrengthSnapshot(Base):
    __tablename__ = "relative_strength_snapshots"

    id: Mapped[int] = mapped_column(primary_key=True)
    symbol: Mapped[str] = mapped_column(String(32), index=True, nullable=False)
    base_symbol: Mapped[str] = mapped_column(String(32), index=True, nullable=False)
    price: Mapped[Decimal | None] = mapped_column(Numeric(24, 10))
    btc_price: Mapped[Decimal | None] = mapped_column(Numeric(24, 10))
    return_1h: Mapped[Decimal | None] = mapped_column(Numeric(12, 6))
    return_24h: Mapped[Decimal | None] = mapped_column(Numeric(12, 6))
    return_7d: Mapped[Decimal | None] = mapped_column(Numeric(12, 6))
    return_30d: Mapped[Decimal | None] = mapped_column(Numeric(12, 6))
    btc_return_1h: Mapped[Decimal | None] = mapped_column(Numeric(12, 6))
    btc_return_24h: Mapped[Decimal | None] = mapped_column(Numeric(12, 6))
    btc_return_7d: Mapped[Decimal | None] = mapped_column(Numeric(12, 6))
    btc_return_30d: Mapped[Decimal | None] = mapped_column(Numeric(12, 6))
    excess_return_1h: Mapped[Decimal | None] = mapped_column(Numeric(12, 6))
    excess_return_24h: Mapped[Decimal | None] = mapped_column(Numeric(12, 6))
    excess_return_7d: Mapped[Decimal | None] = mapped_column(Numeric(12, 6))
    excess_return_30d: Mapped[Decimal | None] = mapped_column(Numeric(12, 6))
    relative_price: Mapped[Decimal | None] = mapped_column(Numeric(24, 10))
    relative_trend_score: Mapped[Decimal | None] = mapped_column(Numeric(12, 6))
    volume_score: Mapped[Decimal | None] = mapped_column(Numeric(12, 6))
    brsi_score: Mapped[Decimal | None] = mapped_column(Numeric(10, 4))
    brsi_change_1h: Mapped[Decimal | None] = mapped_column(Numeric(10, 4))
    brsi_change_4h: Mapped[Decimal | None] = mapped_column(Numeric(10, 4))
    brsi_change_24h: Mapped[Decimal | None] = mapped_column(Numeric(10, 4))
    status: Mapped[str] = mapped_column(String(32), index=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        index=True,
        server_default=func.now(),
        nullable=False,
    )


class RelativeStrengthAlert(Base):
    __tablename__ = "relative_strength_alerts"

    id: Mapped[int] = mapped_column(primary_key=True)
    symbol: Mapped[str] = mapped_column(String(32), index=True, nullable=False)
    alert_type: Mapped[str] = mapped_column(String(64), index=True, nullable=False)
    alert_level: Mapped[str] = mapped_column(String(32), index=True, nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    brsi_score: Mapped[Decimal | None] = mapped_column(Numeric(10, 4))
    previous_brsi_score: Mapped[Decimal | None] = mapped_column(Numeric(10, 4))
    change_value: Mapped[Decimal | None] = mapped_column(Numeric(10, 4))
    is_read: Mapped[bool] = mapped_column(Boolean, index=True, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        index=True,
        server_default=func.now(),
        nullable=False,
    )


class NewsItem(Base):
    __tablename__ = "news_items"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(512), index=True, nullable=False)
    url: Mapped[str] = mapped_column(String(1024), unique=True, index=True, nullable=False)
    source: Mapped[str] = mapped_column(String(128), index=True, nullable=False)
    source_type: Mapped[str] = mapped_column(String(32), index=True, nullable=False)
    published_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True, nullable=False)
    published_at_estimated: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    fetched_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True, nullable=False)
    summary_raw: Mapped[str | None] = mapped_column(Text)
    content_raw: Mapped[str | None] = mapped_column(Text)
    language: Mapped[str | None] = mapped_column(String(16), index=True)
    hash_title: Mapped[str] = mapped_column(String(128), index=True, nullable=False)
    duplicate_count: Mapped[int] = mapped_column(default=0, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )


class NewsAnalysis(Base):
    __tablename__ = "news_analysis"
    __table_args__ = (
        UniqueConstraint("news_item_id", name="uq_news_analysis_news_item"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    news_item_id: Mapped[int] = mapped_column(
        ForeignKey("news_items.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    symbols: Mapped[list | None] = mapped_column(JSON)
    sectors: Mapped[list | None] = mapped_column(JSON)
    main_symbol: Mapped[str | None] = mapped_column(String(32), index=True)
    relevance_score: Mapped[Decimal] = mapped_column(Numeric(10, 4), nullable=False)
    impact_score: Mapped[Decimal] = mapped_column(Numeric(10, 4), nullable=False)
    sentiment_score: Mapped[Decimal] = mapped_column(Numeric(10, 4), nullable=False)
    urgency_level: Mapped[str] = mapped_column(String(32), index=True, nullable=False)
    time_decay_score: Mapped[Decimal] = mapped_column(Numeric(10, 4), nullable=False)
    impact_direction: Mapped[str] = mapped_column(String(32), index=True, nullable=False)
    ai_summary_json: Mapped[dict | None] = mapped_column(JSON)
    analyzed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True, nullable=False)


class NewsBroadcast(Base):
    __tablename__ = "news_broadcasts"

    id: Mapped[int] = mapped_column(primary_key=True)
    broadcast_type: Mapped[str] = mapped_column(String(32), index=True, nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    content_cn: Mapped[str] = mapped_column(Text, nullable=False)
    top_symbols: Mapped[list | None] = mapped_column(JSON)
    top_news_ids: Mapped[list | None] = mapped_column(JSON)
    overall_sentiment: Mapped[str | None] = mapped_column(String(32), index=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        index=True,
        server_default=func.now(),
        nullable=False,
    )


class NewsAlert(Base):
    __tablename__ = "news_alerts"

    id: Mapped[int] = mapped_column(primary_key=True)
    news_item_id: Mapped[int] = mapped_column(
        ForeignKey("news_items.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    alert_type: Mapped[str] = mapped_column(String(64), index=True, nullable=False)
    severity: Mapped[str] = mapped_column(String(32), index=True, nullable=False)
    message_cn: Mapped[str] = mapped_column(Text, nullable=False)
    is_sent: Mapped[bool] = mapped_column(Boolean, index=True, default=False, nullable=False)
    sent_channels: Mapped[list | None] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        index=True,
        server_default=func.now(),
        nullable=False,
    )
