import json

import pytest

from app.backtesting.engine import BacktestEngine
from app.tests.backtest_fixtures import make_ohlcv_dataframe


def test_long_only_backtest_runs_successfully() -> None:
    result = BacktestEngine(min_candles=20).run_backtest(
        symbol="BTC/USDT",
        timeframe="1h",
        df=make_ohlcv_dataframe(120),
        strategy_name="ema_crossover",
        parameters={"fast_ema": 5, "slow_ema": 10},
        initial_capital=10_000,
        fee_bps=10,
        slippage_bps=5,
        max_position_pct=1.0,
    )
    assert result["metrics"]["final_equity"] > 0
    assert result["data_quality"]["has_sufficient_data"] is True
    assert result["disclaimer"]


def test_no_trades_case_returns_safe_metrics() -> None:
    result = BacktestEngine(min_candles=20).run_backtest(
        symbol="BTC/USDT",
        timeframe="1h",
        df=make_ohlcv_dataframe(120),
        strategy_name="breakout",
        parameters={"lookback": 20, "volume_zscore_threshold": 100},
        initial_capital=10_000,
        fee_bps=10,
        slippage_bps=5,
        max_position_pct=1.0,
    )
    assert result["metrics"]["total_trades"] == 0
    assert result["metrics"]["win_rate"] == 0


def test_open_position_closes_at_end_of_backtest() -> None:
    result = BacktestEngine(min_candles=20).run_backtest(
        symbol="BTC/USDT",
        timeframe="1h",
        df=make_ohlcv_dataframe(120),
        strategy_name="ema_crossover",
        parameters={"fast_ema": 5, "slow_ema": 10},
        initial_capital=10_000,
        fee_bps=0,
        slippage_bps=0,
        max_position_pct=1.0,
    )
    assert result["trades"]
    assert result["trades"][-1]["exit_reason"] == "end_of_backtest"


def test_no_lookahead_execution_rule_is_respected() -> None:
    result = BacktestEngine(min_candles=20).run_backtest(
        symbol="BTC/USDT",
        timeframe="1h",
        df=make_ohlcv_dataframe(80),
        strategy_name="ema_crossover",
        parameters={"fast_ema": 3, "slow_ema": 5},
        initial_capital=10_000,
        fee_bps=0,
        slippage_bps=0,
        max_position_pct=1.0,
    )
    trade = result["trades"][0]
    assert trade["entry_time"] > result["data_quality"]["start_date"]


def test_insufficient_data_raises_structured_error() -> None:
    with pytest.raises(ValueError):
        BacktestEngine(min_candles=100).run_backtest(
            symbol="BTC/USDT",
            timeframe="1h",
            df=make_ohlcv_dataframe(10),
            strategy_name="ema_crossover",
            parameters={"fast_ema": 3, "slow_ema": 5},
            initial_capital=10_000,
            fee_bps=0,
            slippage_bps=0,
            max_position_pct=1.0,
        )


def test_output_is_json_serializable() -> None:
    result = BacktestEngine(min_candles=20).run_backtest(
        symbol="BTC/USDT",
        timeframe="1h",
        df=make_ohlcv_dataframe(80),
        strategy_name="ema_crossover",
        parameters={"fast_ema": 3, "slow_ema": 5},
        initial_capital=10_000,
        fee_bps=0,
        slippage_bps=0,
        max_position_pct=1.0,
    )
    json.dumps(result)
