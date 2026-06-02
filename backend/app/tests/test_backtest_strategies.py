import pytest

from app.backtesting.strategies import get_strategy
from app.tests.backtest_fixtures import make_ohlcv_dataframe


def test_ema_crossover_generates_signal_column() -> None:
    df = get_strategy("ema_crossover").generate_signals(
        make_ohlcv_dataframe(),
        {"fast_ema": 5, "slow_ema": 10},
    )
    assert "signal" in df.columns
    assert set(df["signal"].unique()).issubset({0, 1})


def test_rsi_mean_reversion_generates_signal_column() -> None:
    df = get_strategy("rsi_mean_reversion").generate_signals(
        make_ohlcv_dataframe(step=-0.5),
        {"rsi_period": 5, "oversold": 45, "exit_rsi": 55},
    )
    assert "signal" in df.columns


def test_breakout_generates_signal_column() -> None:
    df = get_strategy("breakout").generate_signals(
        make_ohlcv_dataframe(),
        {"lookback": 10, "volume_zscore_threshold": -1},
    )
    assert "signal" in df.columns


def test_relative_strength_generates_signal_column_with_reference_data() -> None:
    target = make_ohlcv_dataframe(step=2.0)
    reference = make_ohlcv_dataframe(step=0.5)
    df = get_strategy("relative_strength").generate_signals(
        target,
        {"reference_df": reference, "lookback": 12, "threshold": 0.1},
    )
    assert "signal" in df.columns
    assert df["signal"].max() == 1


def test_unsupported_strategy_raises_clear_error() -> None:
    with pytest.raises(ValueError):
        get_strategy("not_real")
