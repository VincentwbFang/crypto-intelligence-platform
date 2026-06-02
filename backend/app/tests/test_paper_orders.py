import pytest
from pydantic import ValidationError
from sqlalchemy.orm import Session

from app.schemas.paper_trading import PaperOrderCreateRequest
from app.services.paper_trading_service import PaperTradingService
from app.tests.paper_fixtures import buy_order, create_account, seed_latest_ohlcv, sell_order


def test_create_simulated_market_buy_order(db_session: Session) -> None:
    seed_latest_ohlcv(db_session)
    account = create_account(db_session)

    order = PaperTradingService(db_session).submit_order(buy_order(account["account_id"]))

    assert order["status"] == "filled"
    assert order["filled_price"] > order["requested_price"]


def test_create_simulated_sell_order(db_session: Session) -> None:
    seed_latest_ohlcv(db_session)
    service = PaperTradingService(db_session)
    account = create_account(db_session)
    service.submit_order(buy_order(account["account_id"], 500))

    order = service.submit_order(sell_order(account["account_id"], 200))

    assert order["status"] == "filled"
    assert order["filled_price"] < order["requested_price"]


def test_reject_invalid_order_side_and_type() -> None:
    with pytest.raises(ValidationError):
        PaperOrderCreateRequest(
            account_id="account",
            symbol="BTC/USDT",
            timeframe="1h",
            side="hold",
            order_type="market",
            notional=100,
        )
    with pytest.raises(ValidationError):
        PaperOrderCreateRequest(
            account_id="account",
            symbol="BTC/USDT",
            timeframe="1h",
            side="buy",
            order_type="limit",
            notional=100,
        )


def test_reject_insufficient_cash(db_session: Session) -> None:
    seed_latest_ohlcv(db_session)
    account = create_account(db_session, balance=100)

    order = PaperTradingService(db_session).submit_order(buy_order(account["account_id"], 1000))

    assert order["status"] == "rejected"


def test_reject_sell_without_position(db_session: Session) -> None:
    seed_latest_ohlcv(db_session)
    account = create_account(db_session)

    order = PaperTradingService(db_session).submit_order(sell_order(account["account_id"], 100))

    assert order["status"] == "rejected"


def test_reject_sell_quantity_greater_than_position(db_session: Session) -> None:
    seed_latest_ohlcv(db_session)
    service = PaperTradingService(db_session)
    account = create_account(db_session)
    service.submit_order(buy_order(account["account_id"], 200))

    order = service.submit_order(sell_order(account["account_id"], 1000))

    assert order["status"] == "rejected"
    assert order["risk"]["approved"] is False
