from collections.abc import Generator
from datetime import UTC, datetime

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.db.base import Base
from app.schemas.backtesting import BacktestRunRequest
from app.services.backtest_service import BacktestService
from app.tests.backtest_fixtures import seed_ohlcv


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


def make_request(**overrides: object) -> BacktestRunRequest:
    data = {
        "symbol": "BTC/USDT",
        "timeframe": "1h",
        "strategy_name": "ema_crossover",
        "start_date": datetime(2025, 1, 1, tzinfo=UTC),
        "end_date": datetime(2025, 1, 10, tzinfo=UTC),
        "initial_capital": 10_000,
        "fee_bps": 10,
        "slippage_bps": 5,
        "max_position_pct": 1.0,
        "parameters": {"fast_ema": 5, "slow_ema": 10},
    }
    data.update(overrides)
    return BacktestRunRequest(**data)


def test_run_backtest_persists_run_and_trades(db_session: Session) -> None:
    seed_ohlcv(db_session, count=160)
    result = BacktestService(db_session).run_backtest(make_request())

    assert result["status"] == "completed"
    assert result["run_id"]
    assert result["trades"]


def test_failed_backtest_stores_error_message(db_session: Session) -> None:
    result = BacktestService(db_session).run_backtest(make_request())

    assert result["status"] == "failed"
    assert result["error_message"]


def test_get_backtest_returns_full_result(db_session: Session) -> None:
    seed_ohlcv(db_session, count=160)
    service = BacktestService(db_session)
    result = service.run_backtest(make_request())
    detail = service.get_backtest(result["run_id"])

    assert detail is not None
    assert detail["metrics"]
    assert "equity_curve" in detail


def test_list_backtests_filters_correctly(db_session: Session) -> None:
    seed_ohlcv(db_session, count=160)
    service = BacktestService(db_session)
    service.run_backtest(make_request())

    runs = service.list_backtests(symbol="BTC/USDT", strategy_name="ema_crossover")

    assert len(runs) == 1


def test_delete_backtest_deletes_related_data(db_session: Session) -> None:
    seed_ohlcv(db_session, count=160)
    service = BacktestService(db_session)
    result = service.run_backtest(make_request())

    assert service.delete_backtest(result["run_id"]) is True
    assert service.get_backtest(result["run_id"]) is None
