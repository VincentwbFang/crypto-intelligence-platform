import logging
from datetime import UTC, datetime, timedelta
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
            inserted_count = self.ingest_records(records)
            self.db_session.commit()
            return inserted_count
        except Exception:
            self.db_session.rollback()
            logger.exception("Failed to ingest OHLCV for %s %s", symbol, timeframe)
            raise

    def ingest_records(self, records: list[dict[str, Any]]) -> int:
        if not records:
            return 0

        unique_records: dict[tuple[str, str, str, object], dict[str, Any]] = {}
        for record in records:
            key = (
                record["exchange"],
                record["symbol"],
                record["timeframe"],
                _timestamp_key(record["timestamp"]),
            )
            unique_records[key] = record

        inserted_count = 0
        grouped: dict[tuple[str, str, str], list[dict[str, Any]]] = {}
        for record in unique_records.values():
            grouped.setdefault(
                (record["exchange"], record["symbol"], record["timeframe"]),
                [],
            ).append(record)

        for (exchange, symbol, timeframe), group_records in grouped.items():
            timestamps = _timestamp_lookup_values(
                [record["timestamp"] for record in group_records]
            )
            existing_timestamps = set(
                _timestamp_key(timestamp)
                for timestamp in self.db_session.scalars(
                    select(OHLCV.timestamp).where(
                        OHLCV.exchange == exchange,
                        OHLCV.symbol == symbol,
                        OHLCV.timeframe == timeframe,
                        OHLCV.timestamp.in_(timestamps),
                    )
                ).all()
            )
            for record in group_records:
                if _timestamp_key(record["timestamp"]) in existing_timestamps:
                    continue
                self.db_session.add(_record_to_ohlcv(record))
                inserted_count += 1

        return inserted_count

    def backfill_symbol(
        self,
        symbol: str,
        timeframe: str,
        start_at: datetime,
        end_at: datetime | None = None,
        batch_limit: int = 300,
        max_batches: int | None = None,
    ) -> dict[str, Any]:
        end_at = end_at or datetime.now(UTC)
        if start_at.tzinfo is None:
            start_at = start_at.replace(tzinfo=UTC)
        if end_at.tzinfo is None:
            end_at = end_at.replace(tzinfo=UTC)
        if start_at >= end_at:
            raise ValueError("start_at must be before end_at")

        timeframe_ms = _timeframe_to_milliseconds(self.market_client, timeframe)
        cursor = start_at.astimezone(UTC)
        total_fetched = 0
        total_inserted = 0
        batches = 0
        last_timestamp: datetime | None = None

        try:
            while cursor < end_at.astimezone(UTC):
                if max_batches is not None and batches >= max_batches:
                    break
                records = self.market_client.fetch_ohlcv(
                    symbol=symbol,
                    timeframe=timeframe,
                    limit=batch_limit,
                    since=cursor,
                )
                records = [
                    record
                    for record in records
                    if _as_utc(record["timestamp"]) < end_at.astimezone(UTC)
                ]
                if not records:
                    break

                batches += 1
                total_fetched += len(records)
                inserted = self.ingest_records(records)
                total_inserted += inserted
                self.db_session.commit()

                latest_timestamp = max(_as_utc(record["timestamp"]) for record in records)
                if last_timestamp is not None and latest_timestamp <= last_timestamp:
                    break
                last_timestamp = latest_timestamp
                cursor = latest_timestamp + timedelta(milliseconds=timeframe_ms)

                if len(records) < batch_limit:
                    break

            return {
                "symbol": symbol,
                "timeframe": timeframe,
                "start_at": start_at.isoformat(),
                "end_at": end_at.isoformat(),
                "fetched": total_fetched,
                "inserted": total_inserted,
                "duplicates": max(0, total_fetched - total_inserted),
                "batches": batches,
                "last_timestamp": last_timestamp.isoformat() if last_timestamp else None,
            }
        except Exception:
            self.db_session.rollback()
            logger.exception("Failed to backfill OHLCV for %s %s", symbol, timeframe)
            raise

    def backfill_many(
        self,
        symbols: list[str],
        timeframe: str,
        start_at: datetime,
        end_at: datetime | None = None,
        batch_limit: int = 300,
        max_batches_per_symbol: int | None = None,
    ) -> dict[str, dict[str, Any]]:
        results: dict[str, dict[str, Any]] = {}
        for symbol in symbols:
            try:
                results[symbol] = self.backfill_symbol(
                    symbol=symbol,
                    timeframe=timeframe,
                    start_at=start_at,
                    end_at=end_at,
                    batch_limit=batch_limit,
                    max_batches=max_batches_per_symbol,
                )
            except Exception as exc:
                logger.exception("Skipping failed OHLCV backfill for %s", symbol)
                results[symbol] = {
                    "symbol": symbol,
                    "timeframe": timeframe,
                    "inserted": 0,
                    "fetched": 0,
                    "duplicates": 0,
                    "batches": 0,
                    "error": str(exc),
                }
        return results

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


def _record_to_ohlcv(record: dict[str, Any]) -> OHLCV:
    return OHLCV(
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


def _timeframe_to_milliseconds(market_client: Any, timeframe: str) -> int:
    if hasattr(market_client, "timeframe_to_milliseconds"):
        return int(market_client.timeframe_to_milliseconds(timeframe))
    fallback = {
        "1m": 60_000,
        "5m": 5 * 60_000,
        "15m": 15 * 60_000,
        "30m": 30 * 60_000,
        "1h": 60 * 60_000,
        "4h": 4 * 60 * 60_000,
        "1d": 24 * 60 * 60_000,
    }
    if timeframe not in fallback:
        raise ValueError(f"Unsupported timeframe: {timeframe}")
    return fallback[timeframe]


def _as_utc(value: datetime) -> datetime:
    if value.tzinfo is None:
        return value.replace(tzinfo=UTC)
    return value.astimezone(UTC)


def _timestamp_key(value: datetime) -> datetime:
    return _as_utc(value)


def _timestamp_lookup_values(values: list[datetime]) -> list[datetime]:
    lookup_values: list[datetime] = []
    seen: set[tuple[datetime, bool]] = set()
    for value in values:
        utc_value = _as_utc(value)
        variants = (value, utc_value, utc_value.replace(tzinfo=None))
        for variant in variants:
            key = (_as_utc(variant), variant.tzinfo is None)
            if key in seen:
                continue
            seen.add(key)
            lookup_values.append(variant)
    return lookup_values
