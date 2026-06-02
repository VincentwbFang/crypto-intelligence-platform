from sqlalchemy.orm import Session

from app.services.paper_trading_service import PaperTradingService
from app.tests.paper_fixtures import buy_order, create_account, seed_latest_ohlcv, sell_order


def test_buy_order_opens_and_updates_position(db_session: Session) -> None:
    seed_latest_ohlcv(db_session)
    service = PaperTradingService(db_session)
    account = create_account(db_session)

    service.submit_order(buy_order(account["account_id"], 500))
    service.submit_order(buy_order(account["account_id"], 500))
    positions = service.list_positions(account["account_id"])

    assert len(positions) == 1
    assert positions[0]["quantity"] > 0


def test_sell_order_reduces_and_full_sell_closes_position(db_session: Session) -> None:
    seed_latest_ohlcv(db_session)
    service = PaperTradingService(db_session)
    account = create_account(db_session)
    service.submit_order(buy_order(account["account_id"], 500))
    position = service.list_positions(account["account_id"])[0]

    service.submit_order(sell_order(account["account_id"], position["market_value"]))
    positions = service.list_positions(account["account_id"])
    trades = service.list_trades(account["account_id"])

    assert positions == []
    assert len(trades) == 1
    assert trades[0]["realized_pnl"] is not None
