from datetime import UTC, datetime

from sqlalchemy.orm import Session

from app.db.models import Alert, BacktestRun, PaperAccount
from app.services.alert_service import AlertService
from app.services.backtest_service import BacktestService
from app.services.paper_trading_service import PaperTradingService
from app.services.user_service import UserService


def test_workspace_scoped_resources_are_isolated(db_session: Session) -> None:
    user_a = UserService(db_session).register_user("a@example.com", "Password123", "A")
    user_b = UserService(db_session).register_user("b@example.com", "Password123", "B")
    workspace_a = user_a["default_workspace_id"]
    workspace_b = user_b["default_workspace_id"]
    assert workspace_a and workspace_b and workspace_a != workspace_b

    alert = Alert(
        workspace_id=workspace_a,
        created_by_user_id=user_a["user_id"],
        symbol="BTC/USDT",
        timeframe="1h",
        timestamp=datetime.now(UTC),
        alert_type="high_risk",
        severity="high",
        title="Elevated risk detected",
        message="Risk level increased for research monitoring.",
        status="open",
        dedup_key="tenant-test",
    )
    backtest = BacktestRun(
        workspace_id=workspace_a,
        created_by_user_id=user_a["user_id"],
        run_id="tenant-run",
        symbol="BTC/USDT",
        timeframe="1h",
        strategy_name="ema_crossover",
        parameters={},
        initial_capital=10000,
        status="completed",
    )
    account = PaperAccount(
        workspace_id=workspace_a,
        created_by_user_id=user_a["user_id"],
        account_id="tenant-account",
        name="Tenant Account",
        initial_balance=10000,
        cash_balance=10000,
        equity=10000,
        realized_pnl=0,
        unrealized_pnl=0,
        total_fees=0,
        status="active",
    )
    db_session.add_all([alert, backtest, account])
    db_session.commit()

    assert AlertService(db_session, workspace_a).get_alert(alert.id) is not None
    assert AlertService(db_session, workspace_b).get_alert(alert.id) is None
    assert BacktestService(db_session, workspace_a).get_backtest("tenant-run") is not None
    assert BacktestService(db_session, workspace_b).get_backtest("tenant-run") is None
    try:
        PaperTradingService(db_session, workspace_b).get_account("tenant-account")
    except ValueError:
        assert True
    else:
        raise AssertionError("Paper account should not be visible across workspaces.")
