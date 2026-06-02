from datetime import UTC, datetime, timedelta
from decimal import Decimal

from sqlalchemy.orm import Session

from app.db.models import RelativeStrengthAlert, RelativeStrengthSnapshot
from app.services.relative_strength_alert_service import RelativeStrengthAlertService


def test_alert_trigger_logic_detects_relative_strength_breakout(db_session: Session) -> None:
    now = datetime.now(UTC)
    db_session.add(
        _snapshot(symbol="SOL/USDT", score=55, created_at=now - timedelta(hours=2))
    )
    db_session.commit()
    current = _snapshot_dict(symbol="SOL/USDT", score=80, created_at=now)

    candidates = RelativeStrengthAlertService(db_session).evaluate_alert_candidates([current])

    alert_types = {candidate["alert_type"] for candidate in candidates}
    assert "relative_strength_breakout" in alert_types


def test_alert_trigger_logic_detects_abnormal_movement(db_session: Session) -> None:
    now = datetime.now(UTC)
    current = _snapshot_dict(
        symbol="ETH/USDT",
        score=67,
        created_at=now,
        brsi_change_1h=18,
        brsi_change_4h=30,
    )

    candidates = RelativeStrengthAlertService(db_session).evaluate_alert_candidates([current])

    alert_types = {candidate["alert_type"] for candidate in candidates}
    assert "abnormal_1h_movement" in alert_types
    assert "abnormal_4h_movement" in alert_types


def test_duplicate_alert_prevention(db_session: Session) -> None:
    now = datetime.now(UTC)
    db_session.add(
        _snapshot(symbol="SOL/USDT", score=55, created_at=now - timedelta(hours=2))
    )
    db_session.add(
        RelativeStrengthAlert(
            symbol="SOL/USDT",
            alert_type="relative_strength_breakout",
            alert_level="high",
            title="Existing alert",
            message="Existing relative strength alert.",
            brsi_score=Decimal("80"),
            previous_brsi_score=Decimal("55"),
            change_value=Decimal("25"),
            is_read=False,
            created_at=now - timedelta(hours=1),
        )
    )
    db_session.commit()
    current = _snapshot_dict(symbol="SOL/USDT", score=80, created_at=now)

    alerts = RelativeStrengthAlertService(db_session).evaluate_and_create_alerts([current])

    assert alerts == []
    assert RelativeStrengthAlertService(db_session).is_duplicate(
        "SOL/USDT",
        "relative_strength_breakout",
    )


def test_same_alert_type_outside_dedup_window_is_allowed(db_session: Session) -> None:
    now = datetime.now(UTC)
    db_session.add(
        RelativeStrengthAlert(
            symbol="ETH/USDT",
            alert_type="abnormal_1h_movement",
            alert_level="medium",
            title="Old alert",
            message="Old relative strength movement alert.",
            brsi_score=Decimal("60"),
            previous_brsi_score=Decimal("45"),
            change_value=Decimal("15"),
            is_read=True,
            created_at=now - timedelta(hours=7),
        )
    )
    db_session.commit()

    assert not RelativeStrengthAlertService(db_session).is_duplicate(
        "ETH/USDT",
        "abnormal_1h_movement",
    )


def _snapshot(
    *,
    symbol: str,
    score: float,
    created_at: datetime,
) -> RelativeStrengthSnapshot:
    return RelativeStrengthSnapshot(
        symbol=symbol,
        base_symbol="BTC/USDT",
        price=Decimal("100"),
        btc_price=Decimal("100000"),
        brsi_score=Decimal(str(score)),
        status="Strong",
        created_at=created_at,
    )


def _snapshot_dict(
    *,
    symbol: str,
    score: float,
    created_at: datetime,
    brsi_change_1h: float | None = None,
    brsi_change_4h: float | None = None,
) -> dict:
    return {
        "symbol": symbol,
        "base_symbol": "BTC/USDT",
        "brsi_score": score,
        "brsi_change_1h": brsi_change_1h,
        "brsi_change_4h": brsi_change_4h,
        "excess_return_24h": 5.0,
        "created_at": created_at.isoformat(),
    }
