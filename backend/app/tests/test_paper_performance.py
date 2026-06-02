from sqlalchemy.orm import Session

from app.services.paper_trading_service import PaperTradingService
from app.tests.paper_fixtures import buy_order, create_account, seed_latest_ohlcv


def test_performance_handles_zero_trades(db_session: Session) -> None:
    account = create_account(db_session)

    performance = PaperTradingService(db_session).get_performance(account["account_id"])

    assert performance["total_trades"] == 0
    assert performance["win_rate"] == 0.0
    assert performance["max_drawdown_pct"] == 0.0


def test_performance_returns_total_return_and_unrealized_pnl(db_session: Session) -> None:
    seed_latest_ohlcv(db_session)
    service = PaperTradingService(db_session)
    account = create_account(db_session)
    service.submit_order(buy_order(account["account_id"], 500))

    performance = service.get_performance(account["account_id"])

    assert "total_return_pct" in performance
    assert "unrealized_pnl" in performance
