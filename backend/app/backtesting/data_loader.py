from __future__ import annotations

from datetime import datetime
from typing import Any

import pandas as pd
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import OHLCV

REQUIRED_COLUMNS = ("timestamp", "open", "high", "low", "close", "volume")


class BacktestDataLoader:
    def __init__(self, db_session: Session) -> None:
        self.db_session = db_session

    def load_ohlcv(
        self,
        symbol: str,
        timeframe: str,
        start_date: datetime,
        end_date: datetime,
    ) -> list[dict[str, Any]]:
        rows = self.db_session.scalars(
            select(OHLCV)
            .where(
                OHLCV.symbol == symbol,
                OHLCV.timeframe == timeframe,
                OHLCV.timestamp >= start_date,
                OHLCV.timestamp <= end_date,
            )
            .order_by(OHLCV.timestamp.asc())
        ).all()

        seen: set[datetime] = set()
        result: list[dict[str, Any]] = []
        for row in rows:
            if row.timestamp in seen:
                continue
            seen.add(row.timestamp)
            result.append(
                {
                    "timestamp": row.timestamp,
                    "open": float(row.open),
                    "high": float(row.high),
                    "low": float(row.low),
                    "close": float(row.close),
                    "volume": float(row.volume),
                }
            )
        return result

    def load_dataframe(
        self,
        symbol: str,
        timeframe: str,
        start_date: datetime,
        end_date: datetime,
    ) -> pd.DataFrame:
        rows = self.load_ohlcv(symbol, timeframe, start_date, end_date)
        df = pd.DataFrame(rows, columns=list(REQUIRED_COLUMNS))
        return validate_ohlcv_dataframe(df)


def validate_ohlcv_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    missing = [column for column in REQUIRED_COLUMNS if column not in df.columns]
    if missing:
        raise ValueError(f"Missing required OHLCV columns: {', '.join(missing)}")

    if df.empty:
        return pd.DataFrame(columns=list(REQUIRED_COLUMNS))

    clean = df.copy()
    clean["timestamp"] = pd.to_datetime(clean["timestamp"], utc=True)
    for column in ("open", "high", "low", "close", "volume"):
        clean[column] = pd.to_numeric(clean[column], errors="coerce").astype(float)
    clean = clean.dropna(subset=list(REQUIRED_COLUMNS))
    clean = clean.sort_values("timestamp").drop_duplicates("timestamp", keep="last")
    return clean.reset_index(drop=True)
