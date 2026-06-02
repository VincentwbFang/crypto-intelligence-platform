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


def seed_alert_route_data(db_session: Session) -> None:
    seed_ohlcv(db_session, make_ohlcv_rows(symbol="BTC/USDT", count=220, step=0.2))
    seed_ohlcv(db_session, make_ohlcv_rows(symbol="SOL/USDT", count=220, step=0.7))


def create_alert(client: TestClient, db_session: Session) -> int:
    seed_alert_route_data(db_session)
    response = client.post(
        "/alerts/evaluate",
        json={
            "symbols": ["SOL/USDT"],
            "timeframe": "1h",
            "limit": 200,
            "send_notifications": False,
        },
    )
    assert response.status_code == 200
    alerts = response.json()["alerts"]
    assert alerts
    return int(alerts[0]["id"])


def test_post_alerts_evaluate_returns_evaluation_result(
    client: TestClient,
    db_session: Session,
) -> None:
    seed_alert_route_data(db_session)

    response = client.post(
        "/alerts/evaluate",
        json={"symbols": ["SOL/USDT"], "timeframe": "1h", "limit": 200},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["symbols"] == ["SOL/USDT"]
    assert payload["generated_alerts"] >= 1


def test_get_alerts_returns_list(client: TestClient, db_session: Session) -> None:
    create_alert(client, db_session)

    response = client.get("/alerts")

    assert response.status_code == 200
    assert response.json()["data"]


def test_get_alert_returns_one_alert(client: TestClient, db_session: Session) -> None:
    alert_id = create_alert(client, db_session)

    response = client.get(f"/alerts/{alert_id}")

    assert response.status_code == 200
    assert response.json()["id"] == alert_id


def test_patch_alert_status_updates_status(
    client: TestClient,
    db_session: Session,
) -> None:
    alert_id = create_alert(client, db_session)

    response = client.patch(
        f"/alerts/{alert_id}/status",
        json={"status": "acknowledged"},
    )

    assert response.status_code == 200
    assert response.json()["status"] == "acknowledged"


def test_post_alert_resolve_resolves_alert(
    client: TestClient,
    db_session: Session,
) -> None:
    alert_id = create_alert(client, db_session)

    response = client.post(f"/alerts/{alert_id}/resolve")

    assert response.status_code == 200
    assert response.json()["status"] == "resolved"
    assert response.json()["resolved_at"] is not None


def test_get_alert_explain_returns_disabled_response_when_ai_disabled(
    client: TestClient,
    db_session: Session,
) -> None:
    alert_id = create_alert(client, db_session)

    response = client.get(f"/alerts/{alert_id}/explain")

    assert response.status_code == 200
    assert response.json() == {
        "enabled": False,
        "message": "AI alert explanation is disabled.",
        "error": None,
        "plain_english_summary": None,
        "why_triggered": None,
        "risk_context": None,
        "what_to_monitor": None,
        "limitations": None,
        "disclaimer": None,
        "compliance_warnings": None,
    }
