from sqlalchemy.orm import Session

from app.services.user_service import UserService
from app.subscriptions.feature_gates import FeatureGateService
from app.subscriptions.usage import UsageTrackingService


def test_usage_tracking_summary_and_limit(db_session: Session) -> None:
    user = UserService(db_session).register_user("usage@example.com", "Password123", "Usage")
    workspace_id = user["default_workspace_id"]
    assert workspace_id is not None
    usage = UsageTrackingService(db_session)
    usage.record_event(workspace_id, user["user_id"], "backtest_run", quantity=2)
    assert usage.get_monthly_usage(workspace_id, "backtest_run") == 2
    summary = usage.get_usage_summary(workspace_id)
    assert summary["usage"]["backtest_run"] == 2

    gate = FeatureGateService(db_session)
    result = gate.check_usage_limit(
        workspace_id,
        "backtest_run",
        "max_backtests_per_month",
    )
    assert result["allowed"] is True
