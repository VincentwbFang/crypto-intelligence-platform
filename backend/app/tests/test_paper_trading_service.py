from sqlalchemy.orm import Session

from app.services.paper_trading_service import PaperTradingService
from app.tests.paper_fixtures import buy_order, create_account, seed_latest_ohlcv


def test_service_portfolio_refresh_and_disabled_signal_execution(db_session: Session) -> None:
    seed_latest_ohlcv(db_session)
    service = PaperTradingService(db_session)
    account = create_account(db_session)
    order = service.submit_order(buy_order(account["account_id"], 500))

    portfolio = service.get_portfolio(account["account_id"])
    refreshed = service.refresh_portfolio(account["account_id"])
    performance = service.get_performance(account["account_id"])
    signal_result = service.run_signal_paper_execution(account["account_id"], "BTC/USDT", "1h", 10)

    assert order["status"] == "filled"
    assert portfolio["positions"]
    assert refreshed["equity_snapshot"]
    assert performance["current_equity"] > 0
    assert signal_result["enabled"] is False
