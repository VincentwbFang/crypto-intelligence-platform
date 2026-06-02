from collections.abc import Generator
from datetime import UTC, datetime

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.db.base import Base
from app.services.alert_service import AlertService


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


def make_candidate(**overrides: object) -> dict:
    candidate = {
        "symbol": "SOL/USDT",
        "timeframe": "1h",
        "timestamp": datetime(2026, 5, 10, 12, tzinfo=UTC).isoformat(),
        "alert_type": "high_signal_score",
        "severity": "medium",
        "title": "High signal score detected",
        "message": "High signal score detected for research monitoring.",
        "source": "signal_engine",
        "signal_score": 72.0,
        "risk_level": "medium",
        "setup_type": "trend_continuation",
        "dedup_key": "SOL/USDT:1h:high_signal_score:trend_continuation:medium",
        "raw_payload": {"rule": "high_signal_score"},
    }
    candidate.update(overrides)
    return candidate


def test_create_alert_persists_alert(db_session: Session) -> None:
    alert = AlertService(db_session).create_alert(make_candidate())

    assert alert["id"] is not None
    assert alert["symbol"] == "SOL/USDT"
    assert alert["status"] == "open"


def test_list_alerts_filters_by_symbol_severity_and_status(db_session: Session) -> None:
    service = AlertService(db_session)
    service.create_alert(make_candidate())
    service.create_alert(
        make_candidate(
            symbol="BTC/USDT",
            severity="high",
            dedup_key="BTC/USDT:1h:high_risk:trend_continuation:high",
            alert_type="high_risk",
        )
    )

    alerts = service.list_alerts(symbol="SOL/USDT", severity="medium", status="open")

    assert len(alerts) == 1
    assert alerts[0]["symbol"] == "SOL/USDT"


def test_update_alert_status_works(db_session: Session) -> None:
    service = AlertService(db_session)
    alert = service.create_alert(make_candidate())

    updated = service.update_alert_status(alert["id"], "acknowledged")

    assert updated["status"] == "acknowledged"


def test_invalid_status_raises_error(db_session: Session) -> None:
    service = AlertService(db_session)
    alert = service.create_alert(make_candidate())

    with pytest.raises(ValueError):
        service.update_alert_status(alert["id"], "invalid")


def test_mark_alert_resolved_sets_resolved_at(db_session: Session) -> None:
    service = AlertService(db_session)
    alert = service.create_alert(make_candidate())

    resolved = service.mark_alert_resolved(alert["id"])

    assert resolved["status"] == "resolved"
    assert resolved["resolved_at"] is not None
