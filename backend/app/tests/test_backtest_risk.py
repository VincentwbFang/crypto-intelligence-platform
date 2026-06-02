import pytest

from app.backtesting.risk import (
    BacktestRiskConfig,
    apply_fee,
    apply_slippage,
    calculate_position_size,
    validate_risk_config,
)


def test_position_size_respects_max_position_pct() -> None:
    assert calculate_position_size(10_000, 100, 0.5) == 50


def test_fee_calculation_works() -> None:
    assert apply_fee(10_000, 10) == 10


def test_slippage_worsens_execution() -> None:
    assert apply_slippage(100, "buy", 10) > 100
    assert apply_slippage(100, "sell", 10) < 100


def test_invalid_max_position_pct_fails_validation() -> None:
    with pytest.raises(ValueError):
        validate_risk_config(
            BacktestRiskConfig(
                initial_capital=10_000,
                max_position_pct=1.5,
                fee_bps=10,
                slippage_bps=5,
            )
        )
