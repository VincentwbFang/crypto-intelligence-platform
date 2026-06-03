from datetime import UTC, datetime, timedelta
from decimal import Decimal
from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.api import routes_market
from app.db.base import Base
from app.db.models import OHLCV
from app.db.session import get_db
from app.main import app


@pytest.fixture()
def db_session() -> Generator[Session, None, None]:
    engine = create_engine(
        "sqlite+pysqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    session_factory = sessionmaker(bind=engine, expire_on_commit=False)
    session = session_factory()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture()
def client(db_session: Session) -> Generator[TestClient, None, None]:
    def override_get_db() -> Generator[Session, None, None]:
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    try:
        yield TestClient(app)
    finally:
        app.dependency_overrides.clear()


def seed_ohlcv(db_session: Session) -> None:
    start = datetime(2026, 5, 27, 12, tzinfo=UTC)
    rows = [
        OHLCV(
            exchange="binance",
            symbol="BTC/USDT",
            timeframe="1h",
            timestamp=start + timedelta(hours=index),
            open=Decimal(str(68000 + index * 100)),
            high=Decimal(str(68100 + index * 100)),
            low=Decimal(str(67900 + index * 100)),
            close=Decimal(str(68050 + index * 100)),
            volume=Decimal(str(1000 + index)),
        )
        for index in range(3)
    ]
    db_session.add_all(rows)
    db_session.commit()


def test_get_market_ohlcv_returns_data(
    client: TestClient,
    db_session: Session,
) -> None:
    seed_ohlcv(db_session)

    response = client.get(
        "/market/ohlcv",
        params={"symbol": "BTC/USDT", "timeframe": "1h", "limit": 2},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["symbol"] == "BTC/USDT"
    assert payload["timeframe"] == "1h"
    assert len(payload["data"]) == 2
    assert payload["data"][0]["close"] == 68150.0
    assert payload["data"][1]["close"] == 68250.0


def test_get_market_snapshot_returns_computed_snapshot(
    client: TestClient,
    db_session: Session,
) -> None:
    seed_ohlcv(db_session)

    response = client.get(
        "/market/snapshot",
        params={"symbol": "BTC/USDT", "timeframe": "1h"},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["symbol"] == "BTC/USDT"
    assert payload["timeframe"] == "1h"
    assert payload["latest_close"] == 68250.0
    assert payload["previous_close"] == 68150.0
    assert payload["return_pct"] == round(((68250.0 - 68150.0) / 68150.0) * 100, 4)
    assert payload["candle_count"] == 3


def test_post_market_ingest_uses_mocked_market_client(
    client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    class FakeCCXTMarketClient:
        def __init__(self, exchange_id: str) -> None:
            self.exchange_id = exchange_id

        def fetch_ohlcv(
            self,
            symbol: str,
            timeframe: str,
            limit: int = 200,
        ) -> list[dict]:
            return [
                {
                    "exchange": self.exchange_id,
                    "symbol": symbol,
                    "timeframe": timeframe,
                    "timestamp": datetime(2026, 5, 27, 12, tzinfo=UTC),
                    "open": 68000.0,
                    "high": 68100.0,
                    "low": 67900.0,
                    "close": 68050.0,
                    "volume": 1000.0,
                }
            ][:limit]

    monkeypatch.setattr(routes_market, "CCXTMarketClient", FakeCCXTMarketClient)

    response = client.post(
        "/market/ingest",
        json={
            "exchange": "binance",
            "symbols": ["BTC/USDT", "ETH/USDT"],
            "timeframe": "1h",
            "limit": 200,
        },
    )

    assert response.status_code == 200
    assert response.json() == {
        "exchange": "binance",
        "timeframe": "1h",
        "results": {"BTC/USDT": 1, "ETH/USDT": 1},
    }


def test_get_market_universe_uses_mocked_universe_service(
    client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    class FakeMarketUniverseService:
        def __init__(self, exchange_id: str, market_client: object | None = None) -> None:
            self.exchange_id = exchange_id

        def get_top_market_symbols(self, top_n: int) -> dict:
            return {
                "exchange": self.exchange_id,
                "top_n": top_n,
                "quote": "USDT",
                "source": "test",
                "symbols": ["BTC/USDT", "ETH/USDT"],
                "skipped": [{"symbol": "USDT", "reason": "excluded"}],
            }

    monkeypatch.setattr(routes_market, "MarketUniverseService", FakeMarketUniverseService)

    response = client.get("/market/universe", params={"exchange": "okx", "top_n": 2})

    assert response.status_code == 200
    payload = response.json()
    assert payload["exchange"] == "okx"
    assert payload["top_n"] == 2
    assert payload["symbols"] == ["BTC/USDT", "ETH/USDT"]


def test_post_market_backfill_uses_mocked_market_client_and_universe(
    client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    class FakeCCXTMarketClient:
        def __init__(self, exchange_id: str) -> None:
            self.exchange_id = exchange_id

        def load_markets(self) -> dict[str, dict]:
            return {"BTC/USDT": {}, "ETH/USDT": {}}

        def fetch_ohlcv(
            self,
            symbol: str,
            timeframe: str,
            limit: int = 200,
            since: datetime | None = None,
        ) -> list[dict]:
            timestamp = since or datetime(2026, 5, 27, 12, tzinfo=UTC)
            return [
                {
                    "exchange": self.exchange_id,
                    "symbol": symbol,
                    "timeframe": timeframe,
                    "timestamp": timestamp,
                    "open": 68000.0,
                    "high": 68100.0,
                    "low": 67900.0,
                    "close": 68050.0,
                    "volume": 1000.0,
                }
            ][:limit]

        def timeframe_to_milliseconds(self, timeframe: str) -> int:
            assert timeframe == "1h"
            return 60 * 60 * 1000

    class FakeMarketUniverseService:
        def __init__(self, exchange_id: str, market_client: object | None = None) -> None:
            self.exchange_id = exchange_id

        def get_top_market_symbols(self, top_n: int) -> dict:
            assert top_n == 2
            return {
                "exchange": self.exchange_id,
                "top_n": top_n,
                "quote": "USDT",
                "source": "test",
                "symbols": ["BTC/USDT", "ETH/USDT"],
                "skipped": [],
            }

    monkeypatch.setattr(routes_market, "CCXTMarketClient", FakeCCXTMarketClient)
    monkeypatch.setattr(routes_market, "MarketUniverseService", FakeMarketUniverseService)

    response = client.post(
        "/market/backfill",
        json={
            "exchange": "okx",
            "use_top_market_cap": True,
            "top_n": 2,
            "timeframe": "1h",
            "years": 3,
            "batch_limit": 300,
            "max_batches_per_symbol": 1,
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["exchange"] == "okx"
    assert payload["symbols"] == ["BTC/USDT", "ETH/USDT"]
    assert payload["results"]["BTC/USDT"]["inserted"] == 1
    assert payload["results"]["ETH/USDT"]["inserted"] == 1
