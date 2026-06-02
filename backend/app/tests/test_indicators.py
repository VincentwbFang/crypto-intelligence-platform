import pandas as pd

from app.indicators.technicals import add_all_indicators
from app.tests.signal_fixtures import make_ohlcv_rows


def test_indicator_columns_are_created() -> None:
    df = pd.DataFrame(make_ohlcv_rows(count=220))

    result = add_all_indicators(df)

    for column in (
        "ema_20",
        "ema_50",
        "ema_200",
        "rsi_14",
        "macd",
        "macd_signal",
        "macd_histogram",
        "atr_14",
        "volume_zscore_20",
        "realized_volatility_20",
        "rolling_high_20",
        "rolling_low_20",
    ):
        assert column in result.columns


def test_rsi_is_within_range_when_enough_data_exists() -> None:
    df = pd.DataFrame(make_ohlcv_rows(count=80))

    result = add_all_indicators(df)
    rsi = result["rsi_14"].dropna()

    assert not rsi.empty
    assert rsi.between(0, 100).all()


def test_atr_is_non_negative() -> None:
    df = pd.DataFrame(make_ohlcv_rows(count=80))

    result = add_all_indicators(df)

    assert (result["atr_14"].dropna() >= 0).all()


def test_insufficient_data_does_not_crash() -> None:
    df = pd.DataFrame(make_ohlcv_rows(count=10))

    result = add_all_indicators(df)

    assert len(result) == 10
    assert result["ema_200"].isna().all()

