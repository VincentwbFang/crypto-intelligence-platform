from datetime import UTC, datetime, timedelta

from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.data.ingestion.ohlcv_ingestor import OHLCVIngestor
from app.db.base import Base
from app.db.models import OHLCV


class FakeMarketClient:
    def __init__(self) -> None:
        self.records = [
            {
                "exchange": "binance",
                "symbol": "BTC/USDT",
                "timeframe": "1h",
                "timestamp": datetime(2026, 5, 27, 12, tzinfo=UTC),
                "open": 68000.0,
                "high": 68100.0,
                "low": 67900.0,
                "close": 68050.0,
                "volume": 1000.5,
            },
            {
                "exchange": "binance",
                "symbol": "BTC/USDT",
                "timeframe": "1h",
                "timestamp": datetime(2026, 5, 27, 13, tzinfo=UTC),
                "open": 68050.0,
                "high": 68200.0,
                "low": 68000.0,
                "close": 68150.0,
                "volume": 1100.5,
            },
        ]

    def fetch_ohlcv(self, symbol: str, timeframe: str, limit: int = 200) -> list[dict]:
        return self.records[:limit]


class FakeBackfillMarketClient:
    def __init__(self) -> None:
        self.exchange_id = "binance"
        self.calls: list[datetime | None] = []
        self.start = datetime(2026, 5, 27, 12, tzinfo=UTC)

    def fetch_ohlcv(
        self,
        symbol: str,
        timeframe: str,
        limit: int = 200,
        since: datetime | None = None,
    ) -> list[dict]:
        self.calls.append(since)
        if len(self.calls) == 1:
            offsets = [0, 1]
        elif len(self.calls) == 2:
            offsets = [1, 2]
        else:
            return []
        return [
            {
                "exchange": self.exchange_id,
                "symbol": symbol,
                "timeframe": timeframe,
                "timestamp": self.start + timedelta(hours=offset),
                "open": 68000.0 + offset,
                "high": 68100.0 + offset,
                "low": 67900.0 + offset,
                "close": 68050.0 + offset,
                "volume": 1000.0 + offset,
            }
            for offset in offsets
        ][:limit]

    def timeframe_to_milliseconds(self, timeframe: str) -> int:
        assert timeframe == "1h"
        return 60 * 60 * 1000


def make_session() -> Session:
    engine = create_engine(
        "sqlite+pysqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    session_factory = sessionmaker(bind=engine, expire_on_commit=False)
    return session_factory()


def test_ingest_symbol_inserts_normalized_records() -> None:
    db = make_session()
    ingestor = OHLCVIngestor(db_session=db, market_client=FakeMarketClient())

    inserted_count = ingestor.ingest_symbol("BTC/USDT", "1h", 200)

    rows = db.scalars(select(OHLCV).order_by(OHLCV.timestamp)).all()
    assert inserted_count == 2
    assert len(rows) == 2
    assert rows[0].exchange == "binance"
    assert rows[0].symbol == "BTC/USDT"
    assert float(rows[0].close) == 68050.0


def test_ingest_symbol_ignores_duplicates() -> None:
    db = make_session()
    ingestor = OHLCVIngestor(db_session=db, market_client=FakeMarketClient())

    first_count = ingestor.ingest_symbol("BTC/USDT", "1h", 200)
    second_count = ingestor.ingest_symbol("BTC/USDT", "1h", 200)

    rows = db.scalars(select(OHLCV)).all()
    assert first_count == 2
    assert second_count == 0
    assert len(rows) == 2


def test_backfill_symbol_paginates_and_ignores_duplicates() -> None:
    db = make_session()
    market_client = FakeBackfillMarketClient()
    ingestor = OHLCVIngestor(db_session=db, market_client=market_client)

    result = ingestor.backfill_symbol(
        symbol="BTC/USDT",
        timeframe="1h",
        start_at=market_client.start,
        end_at=market_client.start + timedelta(hours=4),
        batch_limit=2,
    )

    rows = db.scalars(select(OHLCV).order_by(OHLCV.timestamp)).all()
    assert result["fetched"] == 4
    assert result["inserted"] == 3
    assert result["duplicates"] == 1
    assert result["batches"] == 2
    assert len(rows) == 3
    assert rows[-1].timestamp.replace(tzinfo=UTC) == market_client.start + timedelta(hours=2)


def test_backfill_many_returns_error_per_failed_symbol() -> None:
    class PartiallyFailingClient(FakeBackfillMarketClient):
        def fetch_ohlcv(
            self,
            symbol: str,
            timeframe: str,
            limit: int = 200,
            since: datetime | None = None,
        ) -> list[dict]:
            if symbol == "BAD/USDT":
                raise RuntimeError("symbol unavailable")
            return super().fetch_ohlcv(symbol, timeframe, limit, since)

    db = make_session()
    market_client = PartiallyFailingClient()
    ingestor = OHLCVIngestor(db_session=db, market_client=market_client)

    result = ingestor.backfill_many(
        symbols=["BTC/USDT", "BAD/USDT"],
        timeframe="1h",
        start_at=market_client.start,
        end_at=market_client.start + timedelta(hours=2),
        batch_limit=2,
        max_batches_per_symbol=1,
    )

    assert result["BTC/USDT"]["inserted"] == 2
    assert result["BAD/USDT"]["error"] == "symbol unavailable"
