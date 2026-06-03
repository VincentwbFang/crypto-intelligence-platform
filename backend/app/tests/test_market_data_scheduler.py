from __future__ import annotations

from datetime import UTC, datetime, timedelta
from types import SimpleNamespace

import pytest
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import OHLCV
from app.tasks import market_data_tasks
from app.tasks.market_data_tasks import MarketDataScheduler, update_market_data_once


class FakeCCXTMarketClient:
    def __init__(self, exchange_id: str) -> None:
        self.exchange_id = exchange_id

    def load_markets(self) -> dict[str, dict]:
        return {"BTC/USDT": {}, "ETH/USDT": {}, "BAD/USDT": {}}

    def fetch_ohlcv(
        self,
        symbol: str,
        timeframe: str,
        limit: int = 200,
        since: datetime | None = None,
    ) -> list[dict]:
        if symbol == "BAD/USDT":
            raise RuntimeError("source unavailable")
        timestamp = (since or datetime(2026, 6, 3, 12, tzinfo=UTC)) + timedelta(hours=1)
        return [
            {
                "exchange": self.exchange_id,
                "symbol": symbol,
                "timeframe": timeframe,
                "timestamp": timestamp,
                "open": 100.0,
                "high": 110.0,
                "low": 90.0,
                "close": 105.0,
                "volume": 1000.0,
            }
        ][:limit]


class FakeMarketUniverseService:
    def __init__(self, exchange_id: str, market_client: object | None = None) -> None:
        self.exchange_id = exchange_id

    def get_top_market_symbols(self, top_n: int) -> dict:
        assert top_n == 3
        return {
            "exchange": self.exchange_id,
            "top_n": top_n,
            "quote": "USDT",
            "source": "test",
            "symbols": ["BTC/USDT", "ETH/USDT", "BAD/USDT"],
            "skipped": [],
        }


def test_market_data_scheduler_does_not_start_when_disabled() -> None:
    settings = SimpleNamespace(
        ENABLE_MARKET_DATA_SCHEDULER=False,
        MARKET_DATA_UPDATE_INTERVAL_SECONDS=3600,
        MARKET_DATA_UPDATE_ON_STARTUP=False,
    )
    scheduler = MarketDataScheduler(settings_obj=settings, task=lambda: {"ok": True})

    scheduler.start()

    assert scheduler.scheduler.running is False
    assert scheduler.scheduler.get_jobs() == []


def test_market_data_scheduler_run_once_uses_task() -> None:
    settings = SimpleNamespace(
        ENABLE_MARKET_DATA_SCHEDULER=True,
        MARKET_DATA_UPDATE_INTERVAL_SECONDS=3600,
        MARKET_DATA_UPDATE_ON_STARTUP=False,
    )
    scheduler = MarketDataScheduler(settings_obj=settings, task=lambda: {"updated": 3})

    assert scheduler.run_once() == {"updated": 3}


def test_update_market_data_once_ingests_symbols_and_isolates_failures(
    db_session: Session,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(market_data_tasks, "CCXTMarketClient", FakeCCXTMarketClient)
    monkeypatch.setattr(market_data_tasks, "MarketUniverseService", FakeMarketUniverseService)
    monkeypatch.setattr(market_data_tasks.settings, "DEFAULT_EXCHANGE", "okx")
    monkeypatch.setattr(market_data_tasks.settings, "MARKET_DATA_UPDATE_TIMEFRAME", "1h")
    monkeypatch.setattr(market_data_tasks.settings, "MARKET_DATA_UPDATE_LIMIT", 200)
    monkeypatch.setattr(market_data_tasks.settings, "MARKET_DATA_UPDATE_USE_TOP_MARKET_CAP", True)
    monkeypatch.setattr(market_data_tasks.settings, "MARKET_DATA_UPDATE_TOP_N", 3)
    monkeypatch.setattr(market_data_tasks.settings, "MARKET_DATA_UPDATE_ROLLING_DAYS", 35)
    monkeypatch.setattr(market_data_tasks.settings, "MARKET_DATA_UPDATE_MAX_BATCHES_PER_SYMBOL", 1)

    result = update_market_data_once(db_session)

    rows = db_session.scalars(select(OHLCV).order_by(OHLCV.symbol)).all()
    assert [row.symbol for row in rows] == ["BTC/USDT", "ETH/USDT"]
    assert result["inserted"] == {"BTC/USDT": 1, "ETH/USDT": 1}
    assert result["details"]["BTC/USDT"]["batches"] == 1
    assert result["rolling_days"] == 35
    assert result["failures"]["BAD/USDT"] == "Unexpected market data update failure."
