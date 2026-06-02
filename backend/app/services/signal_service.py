from datetime import datetime
from decimal import Decimal
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.models import Signal
from app.services.market_service import MarketService
from app.signals.signal_engine import SignalEngine

SIGNAL_TYPE = "technical_signal_v1"


class SignalService:
    def __init__(self, db_session: Session) -> None:
        self.db_session = db_session
        self.market_service = MarketService(db_session)
        self.signal_engine = SignalEngine(settings.SIGNAL_MIN_CANDLES)

    def generate_latest_signal(
        self,
        symbol: str,
        timeframe: str,
        limit: int,
    ) -> dict[str, Any]:
        rows = self.market_service.get_ohlcv(symbol=symbol, timeframe=timeframe, limit=limit)
        reference_rows = self.market_service.get_ohlcv(
            symbol=settings.SIGNAL_REFERENCE_SYMBOL,
            timeframe=timeframe,
            limit=limit,
        )
        return self.signal_engine.generate_signal(
            symbol=symbol,
            timeframe=timeframe,
            rows=rows,
            reference_rows=reference_rows,
        )

    def generate_and_store_latest_signal(
        self,
        symbol: str,
        timeframe: str,
        limit: int,
    ) -> dict[str, Any]:
        signal = self.generate_latest_signal(symbol=symbol, timeframe=timeframe, limit=limit)
        if signal.get("timestamp") is None:
            return signal

        timestamp = self._parse_timestamp(signal["timestamp"])
        existing = self.db_session.scalar(
            select(Signal).where(
                Signal.symbol == symbol,
                Signal.timeframe == timeframe,
                Signal.timestamp == timestamp,
                Signal.signal_type == SIGNAL_TYPE,
            )
        )
        if existing is None:
            self.db_session.add(
                Signal(
                    symbol=symbol,
                    timeframe=timeframe,
                    timestamp=timestamp,
                    signal_type=SIGNAL_TYPE,
                    score=Decimal(str(signal["scores"]["overall_signal_score"])),
                    direction=signal["signal_direction"],
                    reason=signal["explanation"],
                    confidence=Decimal(str(signal["scores"]["overall_signal_score"])),
                    setup_type=signal["setup_type"],
                    risk_level=signal["risk_level"],
                    raw_payload=signal,
                )
            )
        else:
            existing.score = Decimal(str(signal["scores"]["overall_signal_score"]))
            existing.direction = signal["signal_direction"]
            existing.reason = signal["explanation"]
            existing.confidence = Decimal(str(signal["scores"]["overall_signal_score"]))
            existing.setup_type = signal["setup_type"]
            existing.risk_level = signal["risk_level"]
            existing.raw_payload = signal
        self.db_session.commit()
        return signal

    def get_latest_signal(self, symbol: str, timeframe: str) -> dict[str, Any] | None:
        row = self.db_session.scalars(
            select(Signal)
            .where(
                Signal.symbol == symbol,
                Signal.timeframe == timeframe,
                Signal.signal_type == SIGNAL_TYPE,
            )
            .order_by(Signal.timestamp.desc())
            .limit(1)
        ).first()
        if row is None:
            return None
        return row.raw_payload

    def rank_symbols(
        self,
        symbols: list[str],
        timeframe: str,
        limit: int,
    ) -> list[dict[str, Any]]:
        signals = [
            self.generate_latest_signal(symbol=symbol, timeframe=timeframe, limit=limit)
            for symbol in symbols
        ]
        return sorted(
            signals,
            key=lambda item: item["scores"]["overall_signal_score"],
            reverse=True,
        )

    def _parse_timestamp(self, value: str) -> datetime:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))

