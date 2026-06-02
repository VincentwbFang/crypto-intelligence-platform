from datetime import UTC, datetime, timedelta
from decimal import Decimal
from typing import Literal

from sqlalchemy.orm import Session

from app.db.models import OHLCV


def make_ohlcv_rows(
    symbol: str = "SOL/USDT",
    count: int = 220,
    start_price: float = 100.0,
    step: float = 0.5,
    pattern: Literal["trend", "downtrend", "range"] = "trend",
    volume_base: float = 1000.0,
    expanded_last_range: bool = False,
) -> list[dict]:
    start = datetime(2026, 5, 1, tzinfo=UTC)
    rows = []
    for index in range(count):
        if pattern == "range":
            close = start_price + ((index % 12) - 6) * 0.25
        else:
            close = start_price + index * step
        open_ = close - step * 0.4 if pattern != "range" else close - 0.1
        candle_range = 1.2
        if expanded_last_range and index == count - 1:
            candle_range = 5.0
        high = max(open_, close) + candle_range / 2
        low = min(open_, close) - candle_range / 2
        volume = volume_base + index * 3
        rows.append(
            {
                "exchange": "binance",
                "symbol": symbol,
                "timeframe": "1h",
                "timestamp": start + timedelta(hours=index),
                "open": round(open_, 6),
                "high": round(high, 6),
                "low": round(low, 6),
                "close": round(close, 6),
                "volume": round(volume, 6),
            }
        )
    return rows


def seed_ohlcv(
    db_session: Session,
    rows: list[dict],
) -> None:
    db_session.add_all(
        [
            OHLCV(
                exchange=row["exchange"],
                symbol=row["symbol"],
                timeframe=row["timeframe"],
                timestamp=row["timestamp"],
                open=Decimal(str(row["open"])),
                high=Decimal(str(row["high"])),
                low=Decimal(str(row["low"])),
                close=Decimal(str(row["close"])),
                volume=Decimal(str(row["volume"])),
            )
            for row in rows
        ]
    )
    db_session.commit()

