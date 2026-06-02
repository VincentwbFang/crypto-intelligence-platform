from collections.abc import Generator

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.alerts.deduplication import AlertDeduplicator
from app.alerts.evaluator import AlertEvaluator
from app.alerts.rules import AlertRuleEngine
from app.db.base import Base


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


class FakeSignalService:
    def __init__(self, db_session: Session) -> None:
        self.db_session = db_session
        self.generated_symbols: list[str] = []

    def get_latest_signal(self, symbol: str, timeframe: str) -> dict | None:
        return None

    def generate_and_store_latest_signal(
        self,
        symbol: str,
        timeframe: str,
        limit: int,
    ) -> dict:
        self.generated_symbols.append(symbol)
        return make_signal(symbol=symbol, timeframe=timeframe)


def make_signal(symbol: str = "SOL/USDT", timeframe: str = "1h") -> dict:
    return {
        "symbol": symbol,
        "timeframe": timeframe,
        "timestamp": "2026-05-10T12:00:00+00:00",
        "scores": {
            "trend_score": 80.0,
            "momentum_score": 68.0,
            "volume_score": 60.0,
            "volatility_risk_score": 40.0,
            "relative_strength_score": 72.0,
            "overall_signal_score": 74.0,
        },
        "signal_direction": "bullish",
        "setup_type": "trend_continuation",
        "risk_level": "medium",
        "indicators": {},
        "relative_strength": {},
        "risk_notes": [],
        "data_quality": {
            "candle_count": 200,
            "min_required_candles": 60,
            "has_sufficient_data": True,
            "missing_indicator_warning": False,
        },
        "explanation": "Deterministic signal.",
    }


def make_evaluator(db_session: Session) -> AlertEvaluator:
    return AlertEvaluator(
        signal_service=FakeSignalService(db_session),  # type: ignore[arg-type]
        alert_rule_engine=AlertRuleEngine(),
        alert_deduplicator=AlertDeduplicator(db_session),
    )


def test_evaluator_generates_alerts_from_signal_service_output(db_session: Session) -> None:
    result = make_evaluator(db_session).evaluate_symbol("SOL/USDT", "1h", 200)

    assert result["symbol"] == "SOL/USDT"
    assert result["generated_alerts"] >= 1
    assert result["alerts"][0]["id"] is not None


def test_evaluator_handles_multiple_symbols(db_session: Session) -> None:
    result = make_evaluator(db_session).evaluate_many(["SOL/USDT", "ETH/USDT"], "1h", 200)

    assert result["symbols"] == ["SOL/USDT", "ETH/USDT"]
    assert len(result["results"]) == 2
    assert result["generated_alerts"] >= 2


def test_evaluator_returns_summary(db_session: Session) -> None:
    result = make_evaluator(db_session).evaluate_symbol("SOL/USDT", "1h", 200)

    assert {"symbol", "timeframe", "generated_alerts", "deduplicated_alerts", "alerts"} <= set(
        result
    )


def test_evaluator_does_not_call_ai_or_notifications(db_session: Session) -> None:
    evaluator = make_evaluator(db_session)

    result = evaluator.evaluate_symbol("SOL/USDT", "1h", 200)

    assert "notifications" not in result
    assert all("ai_explanation" not in alert for alert in result["alerts"])
