from datetime import UTC, datetime

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

