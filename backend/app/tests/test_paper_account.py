from sqlalchemy.orm import Session

from app.schemas.paper_trading import PaperAccountCreateRequest
from app.services.paper_trading_service import PaperTradingService


def test_create_and_list_accounts(db_session: Session) -> None:
    service = PaperTradingService(db_session)
    account = service.create_account(
        PaperAccountCreateRequest(name="Main Paper Account", initial_balance=10_000)
    )

    assert account["cash_balance"] == 10_000
    assert service.list_accounts()[0]["account_id"] == account["account_id"]


def test_pause_activate_and_close_account(db_session: Session) -> None:
    service = PaperTradingService(db_session)
    account = service.create_account(
        PaperAccountCreateRequest(name="Main Paper Account", initial_balance=10_000)
    )

    assert service.pause_account(account["account_id"])["status"] == "paused"
    assert service.activate_account(account["account_id"])["status"] == "active"
    assert service.close_account(account["account_id"])["status"] == "closed"
