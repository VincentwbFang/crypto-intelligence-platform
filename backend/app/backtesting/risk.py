from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class BacktestRiskConfig:
    initial_capital: float
    max_position_pct: float
    fee_bps: float
    slippage_bps: float


def validate_risk_config(config: BacktestRiskConfig) -> None:
    if config.initial_capital <= 0:
        raise ValueError("initial_capital must be greater than 0.")
    if config.max_position_pct <= 0 or config.max_position_pct > 1:
        raise ValueError("max_position_pct must be greater than 0 and less than or equal to 1.")
    if config.fee_bps < 0:
        raise ValueError("fee_bps must be greater than or equal to 0.")
    if config.slippage_bps < 0:
        raise ValueError("slippage_bps must be greater than or equal to 0.")


def calculate_position_size(equity: float, price: float, max_position_pct: float) -> float:
    if equity <= 0 or price <= 0:
        return 0.0
    return (equity * max_position_pct) / price


def apply_fee(notional: float, fee_bps: float) -> float:
    return max(notional, 0.0) * max(fee_bps, 0.0) / 10_000


def apply_slippage(price: float, side: str, slippage_bps: float) -> float:
    adjustment = max(slippage_bps, 0.0) / 10_000
    if side == "buy":
        return price * (1 + adjustment)
    if side == "sell":
        return price * (1 - adjustment)
    raise ValueError("side must be 'buy' or 'sell'.")
