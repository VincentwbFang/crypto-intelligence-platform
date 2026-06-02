import logging
from decimal import Decimal
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import OHLCV

logger = logging.getLogger(__name__)


class OHLCVIngestor:
    def __init__(self, db_session: Session, market_client: Any) -> None:
        self.db_session = db_session
        self.market_client = market_client

    def ingest_symbol(
        self,
        symbol: str,
        timeframe: str,
        limit: int = 200,
    ) -> int:
        try:
            records = self.market_client.fetch_ohlcv(symbol, timeframe, limit)
            inserted_count = 0
            seen_keys: set[tuple[str, str, str, object]] = set()

            for record in records:
                key = (
                    record["exchange"],
                    record["symbol"],
                    record["timeframe"],
                    record["timestamp"],
                )
                if key in seen_keys:
                    continue
                seen_keys.add(key)

                exists = self.db_session.scalar(
                    select(OHLCV.id).where(
                        OHLCV.exchange == record["exchange"],
                        OHLCV.symbol == record["symbol"],
                        OHLCV.timeframe == record["timeframe"],
                        OHLCV.timestamp == record["timestamp"],
                    )
                )
                if exists is not None:
                    continue

                self.db_session.add(
                    OHLCV(
                        exchange=record["exchange"],
                        symbol=record["symbol"],
                        timeframe=record["timeframe"],
                        timestamp=record["timestamp"],
                        open=Decimal(str(record["open"])),
                        high=Decimal(str(record["high"])),
                        low=Decimal(str(record["low"])),
                        close=Decimal(str(record["close"])),
                        volume=Decimal(str(record["volume"])),
                    )
                )
                inserted_count += 1

            self.db_session.commit()
            return inserted_count
        except Exception:
            self.db_session.rollback()
            logger.exception("Failed to ingest OHLCV for %s %s", symbol, timeframe)
            raise

    def ingest_many(
        self,
        symbols: list[str],
        timeframe: str,
        limit: int = 200,
    ) -> dict[str, int]:
        return {
            symbol: self.ingest_symbol(symbol=symbol, timeframe=timeframe, limit=limit)
            for symbol in symbols
        }
