from __future__ import annotations

from datetime import UTC, datetime
from decimal import Decimal
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import OHLCV


class SimulatedExecutionEngine:
    def __init__(self, db_session: Session, settings: Any) -> None:
        self.db_session = db_session
        self.settings = settings

    def get_latest_price(self, symbol: str, timeframe: str) -> dict[str, Any]:
        row = self.db_session.scalars(
            select(OHLCV)
            .where(OHLCV.symbol == symbol, OHLCV.timeframe == timeframe)
            .order_by(OHLCV.timestamp.desc())
            .limit(1)
        ).first()
        if row is None:
            raise ValueError("No stored OHLCV data is available for simulated execution.")
        return {
            "symbol": row.symbol,
            "timeframe": row.timeframe,
            "timestamp": row.timestamp.isoformat(),
            "latest_close": float(row.close),
        }

    def simulate_market_fill(self, order: dict[str, Any]) -> dict[str, Any]:
        price = self.get_latest_price(order["symbol"], order["timeframe"])
        latest_close = Decimal(str(price["latest_close"]))
        slippage_bps = Decimal(str(self.settings.PAPER_DEFAULT_SLIPPAGE_BPS))
        fee_bps = Decimal(str(self.settings.PAPER_DEFAULT_FEE_BPS))
        notional = Decimal(str(order["notional"]))
        if order["side"] == "buy":
            filled_price = latest_close * (Decimal("1") + slippage_bps / Decimal("10000"))
        else:
            filled_price = latest_close * (Decimal("1") - slippage_bps / Decimal("10000"))
        fee = notional * fee_bps / Decimal("10000")
        slippage = abs(filled_price - latest_close)
        return {
            "symbol": order["symbol"],
            "side": order["side"],
            "requested_price": float(latest_close),
            "filled_price": float(filled_price),
            "fee": float(fee),
            "slippage": float(slippage),
            "timestamp": price["timestamp"] or datetime.now(UTC).isoformat(),
        }
