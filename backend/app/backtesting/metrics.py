from __future__ import annotations

import math
from statistics import mean
from typing import Any

import numpy as np


def calculate_total_return(initial_capital: float, final_equity: float) -> float:
    if initial_capital <= 0:
        return 0.0
    return round(((final_equity - initial_capital) / initial_capital) * 100, 6)


def calculate_max_drawdown(equity_curve: list[dict[str, Any]]) -> float:
    if not equity_curve:
        return 0.0
    peak = float(equity_curve[0]["equity"])
    max_drawdown = 0.0
    for point in equity_curve:
        equity = float(point["equity"])
        peak = max(peak, equity)
        drawdown = ((equity - peak) / peak) * 100 if peak else 0.0
        max_drawdown = min(max_drawdown, drawdown)
    return round(max_drawdown, 6)


def calculate_sharpe_ratio(
    equity_curve: list[dict[str, Any]],
    periods_per_year: int,
) -> float | None:
    if len(equity_curve) < 2:
        return None
    equities = np.array([float(point["equity"]) for point in equity_curve], dtype=float)
    returns = np.diff(equities) / equities[:-1]
    returns = returns[np.isfinite(returns)]
    if len(returns) < 2:
        return None
    volatility = float(np.std(returns, ddof=1))
    if volatility == 0:
        return None
    sharpe = (float(np.mean(returns)) / volatility) * math.sqrt(periods_per_year)
    return round(sharpe, 6)


def calculate_win_rate(trades: list[dict[str, Any]]) -> float:
    if not trades:
        return 0.0
    wins = sum(1 for trade in trades if float(trade.get("pnl", 0.0)) > 0)
    return round(wins / len(trades), 6)


def calculate_profit_factor(trades: list[dict[str, Any]]) -> float | None:
    gross_profit = sum(float(trade.get("pnl", 0.0)) for trade in trades if float(trade.get("pnl", 0.0)) > 0)
    gross_loss = abs(sum(float(trade.get("pnl", 0.0)) for trade in trades if float(trade.get("pnl", 0.0)) < 0))
    if gross_loss == 0:
        return None if gross_profit == 0 else round(gross_profit, 6)
    return round(gross_profit / gross_loss, 6)


def calculate_average_trade_return(trades: list[dict[str, Any]]) -> float:
    if not trades:
        return 0.0
    return round(mean(float(trade.get("pnl_pct", 0.0)) for trade in trades), 6)


def calculate_average_holding_period(trades: list[dict[str, Any]]) -> float:
    if not trades:
        return 0.0
    return round(mean(float(trade.get("holding_period_bars", 0.0)) for trade in trades), 6)


def calculate_exposure_time(equity_curve: list[dict[str, Any]]) -> float:
    if not equity_curve:
        return 0.0
    exposed = sum(1 for point in equity_curve if float(point.get("position_value", 0.0)) > 0)
    return round((exposed / len(equity_curve)) * 100, 6)


def periods_per_year_for_timeframe(timeframe: str) -> int:
    if timeframe == "1h":
        return 24 * 365
    if timeframe == "4h":
        return 6 * 365
    if timeframe == "1d":
        return 365
    return 365


def calculate_metrics(
    initial_capital: float,
    final_equity: float,
    equity_curve: list[dict[str, Any]],
    trades: list[dict[str, Any]],
    timeframe: str,
) -> dict[str, Any]:
    return {
        "initial_capital": initial_capital,
        "final_equity": round(final_equity, 6),
        "total_return_pct": calculate_total_return(initial_capital, final_equity),
        "max_drawdown_pct": calculate_max_drawdown(equity_curve),
        "sharpe_ratio": calculate_sharpe_ratio(
            equity_curve,
            periods_per_year_for_timeframe(timeframe),
        ),
        "win_rate": calculate_win_rate(trades),
        "profit_factor": calculate_profit_factor(trades),
        "total_trades": len(trades),
        "average_trade_return_pct": calculate_average_trade_return(trades),
        "average_holding_period_bars": calculate_average_holding_period(trades),
        "exposure_time_pct": calculate_exposure_time(equity_curve),
    }
