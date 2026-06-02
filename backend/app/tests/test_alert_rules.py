import json

from app.alerts.rules import AlertRuleEngine


def make_signal(**overrides: object) -> dict:
    signal = {
        "symbol": "SOL/USDT",
        "timeframe": "1h",
        "timestamp": "2026-05-10T12:00:00+00:00",
        "latest_close": 125.0,
        "scores": {
            "trend_score": 78.0,
            "momentum_score": 64.0,
            "volume_score": 55.0,
            "volatility_risk_score": 42.0,
            "relative_strength_score": 70.0,
            "overall_signal_score": 72.0,
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
    signal.update(overrides)
    return signal


def alert_types(signal: dict, previous_signal: dict | None = None) -> set[str]:
    alerts = AlertRuleEngine().evaluate_signal(signal, previous_signal=previous_signal)
    return {alert["alert_type"] for alert in alerts}


def test_high_signal_score_alert_triggers() -> None:
    assert "high_signal_score" in alert_types(make_signal())


def test_high_risk_alert_triggers() -> None:
    signal = make_signal(risk_level="high")

    assert "high_risk" in alert_types(signal)


def test_relative_strength_alert_triggers() -> None:
    signal = make_signal()

    assert "relative_strength" in alert_types(signal)


def test_weak_breakout_alert_triggers() -> None:
    signal = make_signal(
        setup_type="breakout_watch",
        scores={
            **make_signal()["scores"],
            "volume_score": 42.0,
        },
    )

    assert "weak_breakout" in alert_types(signal)


def test_trend_damage_alert_triggers() -> None:
    signal = make_signal(
        signal_direction="bearish",
        risk_level="high",
        scores={
            **make_signal()["scores"],
            "trend_score": 30.0,
            "overall_signal_score": 35.0,
            "relative_strength_score": 35.0,
        },
    )

    assert "trend_damage" in alert_types(signal)


def test_insufficient_data_alert_triggers_with_low_severity() -> None:
    signal = make_signal(
        scores={**make_signal()["scores"], "overall_signal_score": 20.0},
        data_quality={
            "candle_count": 20,
            "min_required_candles": 60,
            "has_sufficient_data": False,
            "missing_indicator_warning": True,
        },
    )

    alerts = AlertRuleEngine().evaluate_signal(signal)
    insufficient_alert = next(
        alert for alert in alerts if alert["alert_type"] == "insufficient_data"
    )

    assert insufficient_alert["severity"] == "low"


def test_signal_change_alert_triggers() -> None:
    previous = make_signal(signal_direction="neutral")
    current = make_signal(signal_direction="bullish")

    assert "signal_change" in alert_types(current, previous_signal=previous)


def test_alert_messages_do_not_contain_forbidden_trading_advice() -> None:
    alerts = AlertRuleEngine().evaluate_signal(make_signal(risk_level="high"))
    text = json.dumps(alerts).lower()

    for phrase in (
        "buy now",
        "sell now",
        "short here",
        "long here",
        "use leverage",
        "guaranteed",
        "all in",
        "price target",
    ):
        assert phrase not in text
