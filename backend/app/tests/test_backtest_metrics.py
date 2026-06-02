from app.backtesting.metrics import (
    calculate_max_drawdown,
    calculate_profit_factor,
    calculate_sharpe_ratio,
    calculate_total_return,
    calculate_win_rate,
)


def test_total_return_calculation() -> None:
    assert calculate_total_return(10_000, 11_000) == 10.0


def test_max_drawdown_calculation() -> None:
    curve = [{"equity": 100}, {"equity": 120}, {"equity": 90}]
    assert calculate_max_drawdown(curve) == -25.0


def test_win_rate_calculation() -> None:
    trades = [{"pnl": 10}, {"pnl": -5}, {"pnl": 1}]
    assert calculate_win_rate(trades) == 0.666667


def test_profit_factor_calculation() -> None:
    trades = [{"pnl": 10}, {"pnl": -5}, {"pnl": 5}]
    assert calculate_profit_factor(trades) == 3.0


def test_sharpe_handles_zero_volatility_safely() -> None:
    curve = [{"equity": 100}, {"equity": 100}, {"equity": 100}]
    assert calculate_sharpe_ratio(curve, 365) is None
