from app.core.config import settings
from app.paper_trading.risk import PaperRiskManager


def test_max_position_pct_enforced() -> None:
    risk = PaperRiskManager(settings).check_max_position_size(
        {"equity": 1000},
        {"side": "buy", "notional": 500},
    )

    assert risk["approved"] is False


def test_max_position_pct_includes_existing_position() -> None:
    risk = PaperRiskManager(settings).check_max_position_size(
        {"equity": 1000},
        {"side": "buy", "notional": 100},
        {"symbol": "BTC/USDT", "market_value": 200, "status": "open"},
    )

    assert risk["approved"] is False


def test_max_open_positions_allows_existing_symbol_but_blocks_new_symbol() -> None:
    positions = [
        {"symbol": f"ASSET{index}/USDT", "status": "open"}
        for index in range(settings.PAPER_MAX_OPEN_POSITIONS)
    ]
    manager = PaperRiskManager(settings)

    existing = manager.check_max_open_positions(
        {},
        positions,
        {"side": "buy", "symbol": "ASSET0/USDT"},
    )
    new_symbol = manager.check_max_open_positions(
        {},
        positions,
        {"side": "buy", "symbol": "NEW/USDT"},
    )

    assert existing["approved"] is True
    assert new_symbol["approved"] is False


def test_no_shorting_enforced() -> None:
    risk = PaperRiskManager(settings).check_no_shorting(
        {"side": "sell", "quantity": 1},
        {"quantity": 0.5, "status": "open"},
    )

    assert risk["approved"] is False


def test_no_leverage_enforced() -> None:
    risk = PaperRiskManager(settings).check_no_leverage({"leverage": 2})

    assert risk["approved"] is False


def test_daily_loss_check_rejects_when_breached() -> None:
    risk = PaperRiskManager(settings).check_daily_loss_limit(
        {"initial_balance": 1000, "realized_pnl": -100}
    )

    assert risk["approved"] is False
