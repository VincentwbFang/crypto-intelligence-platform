from collections.abc import Generator
from datetime import UTC, datetime, timedelta

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.alerts.deduplication import AlertDeduplicator
from app.db.base import Base
from app.db.models import Alert


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


def make_alert(dedup_key: str, created_at: datetime, alert_type: str = "high_risk") -> Alert:
    return Alert(
        symbol="SOL/USDT",
        timeframe="1h",
        timestamp=created_at,
        alert_type=alert_type,
        severity="high",
        title="Elevated risk detected",
        message="Risk level increased for research monitoring.",
        status="open",
        source="signal_engine",
        risk_level="high",
        setup_type="trend_continuation",
        dedup_key=dedup_key,
        raw_payload={},
        created_at=created_at,
        updated_at=created_at,
    )


def test_duplicate_alert_within_dedup_window_is_filtered(db_session: Session) -> None:
    dedup_key = "SOL/USDT:1h:high_risk:trend_continuation:high"
    db_session.add(make_alert(dedup_key, datetime.now(UTC) - timedelta(minutes=10)))
    db_session.commit()

    new_alerts = AlertDeduplicator(db_session).filter_new_alerts(
        [{"dedup_key": dedup_key}],
        window_minutes=60,
    )

    assert new_alerts == []


def test_same_dedup_key_outside_window_is_allowed(db_session: Session) -> None:
    dedup_key = "SOL/USDT:1h:high_risk:trend_continuation:high"
    db_session.add(make_alert(dedup_key, datetime.now(UTC) - timedelta(hours=2)))
    db_session.commit()

    new_alerts = AlertDeduplicator(db_session).filter_new_alerts(
        [{"dedup_key": dedup_key}],
        window_minutes=60,
    )

    assert len(new_alerts) == 1


def test_different_alert_type_is_not_deduplicated(db_session: Session) -> None:
    db_session.add(
        make_alert(
            "SOL/USDT:1h:high_risk:trend_continuation:high",
            datetime.now(UTC) - timedelta(minutes=10),
            alert_type="high_risk",
        )
    )
    db_session.commit()

    new_alerts = AlertDeduplicator(db_session).filter_new_alerts(
        [{"dedup_key": "SOL/USDT:1h:trend_damage:trend_continuation:high"}],
        window_minutes=60,
    )

    assert len(new_alerts) == 1
