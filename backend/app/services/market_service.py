from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import OHLCV


class MarketService:
    def __init__(self, db_session: Session) -> None:
        self.db_session = db_session

    def get_ohlcv(
        self,
        symbol: str,
        timeframe: str,
        limit: int,
    ) -> list[dict[str, Any]]:
        rows = self.db_session.scalars(
            select(OHLCV)
            .where(OHLCV.symbol == symbol, OHLCV.timeframe == timeframe)
            .order_by(OHLCV.timestamp.desc())
            .limit(limit)
        ).all()

        return [self._row_to_dict(row) for row in reversed(rows)]

    def get_latest_market_snapshot(
        self,
        symbol: str,
        timeframe: str,
        limit: int = 200,
    ) -> dict[str, Any]:
        candles = self.get_ohlcv(symbol=symbol, timeframe=timeframe, limit=limit)
        if len(candles) < 2:
            raise ValueError("At least two OHLCV candles are required for a snapshot.")

        latest = candles[-1]
        previous = candles[-2]
        previous_close = previous["close"]
        latest_close = latest["close"]
        return_pct = 0.0
        if previous_close != 0:
            return_pct = ((latest_close - previous_close) / previous_close) * 100

        return {
            "symbol": symbol,
            "timeframe": timeframe,
            "latest_close": latest_close,
            "previous_close": previous_close,
            "return_pct": round(return_pct, 4),
            "high": latest["high"],
            "low": latest["low"],
            "volume": latest["volume"],
            "candle_count": len(candles),
            "timestamp": latest["timestamp"],
        }

    def _row_to_dict(self, row: OHLCV) -> dict[str, Any]:
        return {
            "exchange": row.exchange,
            "symbol": row.symbol,
            "timeframe": row.timeframe,
            "timestamp": row.timestamp,
            "open": float(row.open),
            "high": float(row.high),
            "low": float(row.low),
            "close": float(row.close),
            "volume": float(row.volume),
        }

