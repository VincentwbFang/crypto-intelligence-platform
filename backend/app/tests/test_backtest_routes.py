from collections.abc import Generator
from datetime import UTC, datetime

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.db.base import Base
from app.db.session import get_db
from app.main import app
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


@pytest.fixture()
def client(db_session: Session) -> Generator[TestClient, None, None]:
    def override_get_db() -> Generator[Session, None, None]:
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    try:
        yield TestClient(app)
    finally:
        app.dependency_overrides.clear()


def request_payload() -> dict:
    return {
        "symbol": "BTC/USDT",
        "timeframe": "1h",
        "strategy_name": "ema_crossover",
        "start_date": datetime(2025, 1, 1, tzinfo=UTC).isoformat(),
        "end_date": datetime(2025, 1, 10, tzinfo=UTC).isoformat(),
        "initial_capital": 10_000,
        "fee_bps": 10,
        "slippage_bps": 5,
        "max_position_pct": 1.0,
        "parameters": {"fast_ema": 5, "slow_ema": 10},
    }


def test_get_backtest_strategies_returns_strategy_list(client: TestClient) -> None:
    response = client.get("/backtests/strategies")
    assert response.status_code == 200
    assert response.json()["data"]


def test_backtest_route_lifecycle(client: TestClient, db_session: Session) -> None:
    seed_ohlcv(db_session, count=160)

    run_response = client.post("/backtests/run", json=request_payload())
    assert run_response.status_code == 200
    run_id = run_response.json()["run_id"]

    assert client.get("/backtests").json()["data"]
    assert client.get(f"/backtests/{run_id}").status_code == 200
    assert client.get(f"/backtests/{run_id}/trades").status_code == 200
    assert client.get(f"/backtests/{run_id}/equity-curve").status_code == 200
    explain = client.get(f"/backtests/{run_id}/explain")
    assert explain.status_code == 200
    assert explain.json()["enabled"] is False

    delete_response = client.delete(f"/backtests/{run_id}")
    assert delete_response.status_code == 200
    assert delete_response.json()["deleted"] is True
