from __future__ import annotations

from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import Workspace
from app.subscriptions.plans import get_plan_limits
from app.subscriptions.usage import UsageTrackingService

FEATURE_TO_LIMIT = {
    "watchlist_symbols": "max_watchlist_symbols",
    "backtesting": "max_backtests_per_month",
    "paper_trading": "max_paper_accounts",
    "ai_signal_explanation": "max_ai_explanations_per_month",
    "ai_alert_explanation": "max_ai_explanations_per_month",
    "ai_backtest_explanation": "max_ai_explanations_per_month",
    "ai_paper_trading_explanation": "max_ai_explanations_per_month",
    "alert_scheduler": "alert_scheduler_enabled",
    "webhook_notifications": "webhook_notifications_enabled",
}


class FeatureGateService:
    def __init__(self, db_session: Session) -> None:
        self.db_session = db_session
        self.usage = UsageTrackingService(db_session)

    def get_workspace_plan(self, workspace_id: str) -> str:
        workspace = self.db_session.scalar(
            select(Workspace).where(Workspace.workspace_id == workspace_id)
        )
        return workspace.plan if workspace is not None else "free"

    def get_plan_limits(self, plan: str) -> dict[str, Any]:
        return get_plan_limits(plan)

    def check_feature(self, workspace_id: str, feature_name: str) -> dict[str, Any]:
        plan = self.get_workspace_plan(workspace_id)
        limits = self.get_plan_limits(plan)
        limit_name = FEATURE_TO_LIMIT.get(feature_name)
        if limit_name is None:
            return {"allowed": True, "plan": plan, "feature": feature_name}
        value = limits.get(limit_name)
        if isinstance(value, bool):
            return {"allowed": value, "plan": plan, "feature": feature_name, "limit": value}
        return {"allowed": True, "plan": plan, "feature": feature_name, "limit": value}

    def check_usage_limit(
        self,
        workspace_id: str,
        event_type: str,
        limit_name: str,
        requested_quantity: int = 1,
    ) -> dict[str, Any]:
        plan = self.get_workspace_plan(workspace_id)
        limit = int(self.get_plan_limits(plan).get(limit_name, 0))
        used = self.usage.get_monthly_usage(workspace_id, event_type)
        allowed = used + requested_quantity <= limit
        return {
            "allowed": allowed,
            "plan": plan,
            "limit_name": limit_name,
            "limit": limit,
            "used": used,
            "remaining": max(limit - used, 0),
        }

    def enforce_or_raise(
        self,
        workspace_id: str,
        feature_name: str,
        event_type: str | None = None,
    ) -> None:
        feature = self.check_feature(workspace_id, feature_name)
        if not feature["allowed"]:
            raise PermissionError(f"Feature is not available on the {feature['plan']} plan.")
        if event_type and isinstance(feature.get("limit"), int):
            result = self.check_usage_limit(
                workspace_id,
                event_type,
                str(FEATURE_TO_LIMIT[feature_name]),
            )
            if not result["allowed"]:
                raise PermissionError("Usage limit reached for the current plan.")
