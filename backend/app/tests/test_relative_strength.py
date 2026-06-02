from app.signals.relative_strength import calculate_relative_strength_score
from app.tests.signal_fixtures import make_ohlcv_rows


def test_target_outperforming_btc_has_score_above_neutral() -> None:
    target_rows = make_ohlcv_rows(symbol="SOL/USDT", count=220, step=0.8)
    reference_rows = make_ohlcv_rows(symbol="BTC/USDT", count=220, step=0.2)

    result = calculate_relative_strength_score(target_rows, reference_rows)

    assert result["relative_strength_score"] > 50


def test_target_underperforming_btc_has_score_below_neutral() -> None:
    target_rows = make_ohlcv_rows(symbol="SOL/USDT", count=220, step=0.1)
    reference_rows = make_ohlcv_rows(symbol="BTC/USDT", count=220, step=0.7)

    result = calculate_relative_strength_score(target_rows, reference_rows)

    assert result["relative_strength_score"] < 50


def test_insufficient_data_returns_neutral_score() -> None:
    target_rows = make_ohlcv_rows(symbol="SOL/USDT", count=10, step=0.8)
    reference_rows = make_ohlcv_rows(symbol="BTC/USDT", count=10, step=0.2)

    result = calculate_relative_strength_score(target_rows, reference_rows)

    assert result["relative_strength_score"] == 50.0
    assert "Insufficient data" in result["explanation"]

