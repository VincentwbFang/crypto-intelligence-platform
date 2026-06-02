from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.db.base import Base
from app.db.session import get_db
from app.main import app
from app.tests.signal_fixtures import make_ohlcv_rows, seed_ohlcv


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


def seed_signal_route_data(db_session: Session) -> None:
    seed_ohlcv(
        db_session,
        make_ohlcv_rows(symbol="BTC/USDT", count=220, step=0.2),
    )
    seed_ohlcv(
        db_session,
        make_ohlcv_rows(symbol="SOL/USDT", count=220, step=0.7),
    )
    seed_ohlcv(
        db_session,
        make_ohlcv_rows(symbol="ETH/USDT", count=220, step=0.3),
    )


def test_get_signal_returns_deterministic_signal(
    client: TestClient,
    db_session: Session,
) -> None:
    seed_signal_route_data(db_session)

    response = client.get("/signals/SOL/USDT", params={"timeframe": "1h", "limit": 200})

    assert response.status_code == 200
    payload = response.json()
    assert payload["symbol"] == "SOL/USDT"
    assert payload["scores"]["overall_signal_score"] >= 0
    assert payload["ai_explanation"] is None


def test_post_generate_stores_signal(
    client: TestClient,
    db_session: Session,
) -> None:
    seed_signal_route_data(db_session)

    response = client.post(
        "/signals/SOL/USDT/generate",
        params={"timeframe": "1h", "limit": 200},
    )

    assert response.status_code == 200
    assert response.json()["symbol"] == "SOL/USDT"


def test_get_latest_returns_stored_signal(
    client: TestClient,
    db_session: Session,
) -> None:
    seed_signal_route_data(db_session)
    client.post("/signals/SOL/USDT/generate", params={"timeframe": "1h", "limit": 200})

    response = client.get("/signals/SOL/USDT/latest", params={"timeframe": "1h"})

    assert response.status_code == 200
    assert response.json()["symbol"] == "SOL/USDT"


def test_rank_returns_sorted_symbols(
    client: TestClient,
    db_session: Session,
) -> None:
    seed_signal_route_data(db_session)

    response = client.get(
        "/signals/rank",
        params={"symbols": "SOL/USDT,ETH/USDT,BTC/USDT", "limit": 200},
    )

    assert response.status_code == 200
    data = response.json()["data"]
    scores = [item["scores"]["overall_signal_score"] for item in data]
    assert scores == sorted(scores, reverse=True)


def test_include_ai_explanation_false_does_not_call_ai(
    client: TestClient,
    db_session: Session,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    seed_signal_route_data(db_session)

    def fail_if_called(*args: object, **kwargs: object) -> None:
        raise AssertionError("AI explanation should not be called")

    monkeypatch.setattr(
        "app.api.routes_signals.AISignalExplanationService",
        fail_if_called,
    )

    response = client.get(
        "/signals/SOL/USDT",
        params={"timeframe": "1h", "limit": 200, "include_ai_explanation": False},
    )

    assert response.status_code == 200
    assert response.json()["ai_explanation"] is None

