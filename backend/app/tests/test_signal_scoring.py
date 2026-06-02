import pandas as pd

from app.indicators.technicals import add_all_indicators
from app.signals.scoring import (
    calculate_momentum_score,
    calculate_trend_score,
    calculate_volume_score,
    calculate_volatility_risk_score,
)
from app.signals.risk_engine import detect_overbought_risk
from app.tests.signal_fixtures import make_ohlcv_rows


def latest_row(rows: list[dict]) -> dict:
    return add_all_indicators(pd.DataFrame(rows)).to_dict(orient="records")[-1]


def test_trend_score_is_high_in_uptrend() -> None:
    row = latest_row(make_ohlcv_rows(count=220, step=0.6))

    assert calculate_trend_score(row) >= 70


def test_trend_score_is_low_in_downtrend() -> None:
    row = latest_row(make_ohlcv_rows(count=220, start_price=220, step=-0.6))

    assert calculate_trend_score(row) <= 45


def test_rsi_above_75_triggers_overbought_logic() -> None:
    row = latest_row(make_ohlcv_rows(count=220, step=1.0))

    assert detect_overbought_risk(row) is True


def test_scores_are_between_zero_and_one_hundred() -> None:
    rows = add_all_indicators(pd.DataFrame(make_ohlcv_rows(count=220))).to_dict(
        orient="records"
    )
    row = rows[-1]
    scores = [
        calculate_trend_score(row),
        calculate_momentum_score(row),
        calculate_volume_score(row),
        calculate_volatility_risk_score(row, rows),
    ]

    assert all(0 <= score <= 100 for score in scores)


def test_volatility_risk_increases_when_candle_ranges_expand() -> None:
    normal_rows = add_all_indicators(pd.DataFrame(make_ohlcv_rows(count=220))).to_dict(
        orient="records"
    )
    expanded_rows = add_all_indicators(
        pd.DataFrame(make_ohlcv_rows(count=220, expanded_last_range=True))
    ).to_dict(orient="records")

    normal_score = calculate_volatility_risk_score(normal_rows[-1], normal_rows)
    expanded_score = calculate_volatility_risk_score(expanded_rows[-1], expanded_rows)

    assert expanded_score > normal_score

