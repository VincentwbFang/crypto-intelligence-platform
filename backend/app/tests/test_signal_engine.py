import json

from app.signals.signal_engine import SignalEngine
from app.tests.signal_fixtures import make_ohlcv_rows


def test_bullish_dataset_returns_bullish_or_mixed_with_high_score() -> None:
    signal = SignalEngine().generate_signal(
        symbol="SOL/USDT",
        timeframe="1h",
        rows=make_ohlcv_rows(symbol="SOL/USDT", count=220, step=0.7),
        reference_rows=make_ohlcv_rows(symbol="BTC/USDT", count=220, step=0.2),
    )

    assert signal["signal_direction"] in {"bullish", "mixed"}
    assert signal["scores"]["overall_signal_score"] >= 55


def test_bearish_dataset_returns_bearish_or_mixed_with_lower_score() -> None:
    signal = SignalEngine().generate_signal(
        symbol="SOL/USDT",
        timeframe="1h",
        rows=make_ohlcv_rows(symbol="SOL/USDT", count=220, start_price=220, step=-0.6),
        reference_rows=make_ohlcv_rows(symbol="BTC/USDT", count=220, step=0.2),
    )

    assert signal["signal_direction"] in {"bearish", "mixed", "neutral"}
    assert signal["scores"]["overall_signal_score"] <= 55


def test_insufficient_data_returns_insufficient_setup_type() -> None:
    signal = SignalEngine().generate_signal(
        symbol="SOL/USDT",
        timeframe="1h",
        rows=make_ohlcv_rows(symbol="SOL/USDT", count=10),
        reference_rows=[],
    )

    assert signal["setup_type"] == "insufficient_data"
    assert signal["data_quality"]["has_sufficient_data"] is False


def test_signal_output_is_json_serializable() -> None:
    signal = SignalEngine().generate_signal(
        symbol="SOL/USDT",
        timeframe="1h",
        rows=make_ohlcv_rows(symbol="SOL/USDT", count=220),
        reference_rows=make_ohlcv_rows(symbol="BTC/USDT", count=220),
    )

    json.dumps(signal)


def test_signal_engine_does_not_call_ai() -> None:
    signal = SignalEngine().generate_signal(
        symbol="SOL/USDT",
        timeframe="1h",
        rows=make_ohlcv_rows(symbol="SOL/USDT", count=80),
        reference_rows=[],
    )

    assert "ai_explanation" not in signal

