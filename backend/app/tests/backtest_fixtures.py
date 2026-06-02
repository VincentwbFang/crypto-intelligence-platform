from __future__ import annotations

from datetime import UTC, datetime, timedelta
from decimal import Decimal

import pandas as pd
from sqlalchemy.orm import Session

from app.db.models import OHLCV


def make_ohlcv_rows(
    count: int = 140,
    symbol: str = "BTC/USDT",
    start_price: float = 100.0,
    step: float = 1.0,
) -> list[dict]:
    start = datetime(2025, 1, 1, tzinfo=UTC)
    rows = []
    for index in range(count):
        close = start_price + index * step
        rows.append(
            {
                "timestamp": start + timedelta(hours=index),
                "open": close - 0.4,
                "high": close + 1.0,
                "low": close - 1.0,
                "close": close,
                "volume": 1000 + index * 3,
                "symbol": symbol,
            }
        )
    return rows


def make_ohlcv_dataframe(count: int = 140, step: float = 1.0) -> pd.DataFrame:
    return pd.DataFrame(make_ohlcv_rows(count=count, step=step))


def seed_ohlcv(
    db_session: Session,
    count: int = 140,
    symbol: str = "BTC/USDT",
    timeframe: str = "1h",
    step: float = 1.0,
) -> None:
    for row in make_ohlcv_rows(count=count, symbol=symbol, step=step):
        db_session.add(
            OHLCV(
                exchange="binance",
                symbol=symbol,
                timeframe=timeframe,
                timestamp=row["timestamp"],
                open=Decimal(str(row["open"])),
                high=Decimal(str(row["high"])),
                low=Decimal(str(row["low"])),
                close=Decimal(str(row["close"])),
                volume=Decimal(str(row["volume"])),
            )
        )
    db_session.commit()
