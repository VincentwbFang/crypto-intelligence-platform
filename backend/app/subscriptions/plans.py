from __future__ import annotations

from app.core.config import settings

VALID_PLANS = ("free", "pro", "premium")


def get_plan_limits(plan: str) -> dict[str, int | bool]:
    plans = {
        "free": {
            "max_watchlist_symbols": settings.FREE_PLAN_MAX_WATCHLIST_SYMBOLS,
            "max_backtests_per_month": settings.FREE_PLAN_MAX_BACKTESTS_PER_MONTH,
            "max_ai_explanations_per_month": settings.FREE_PLAN_MAX_AI_EXPLANATIONS_PER_MONTH,
            "max_paper_accounts": settings.FREE_PLAN_MAX_PAPER_ACCOUNTS,
            "alert_scheduler_enabled": False,
            "webhook_notifications_enabled": False,
        },
        "pro": {
            "max_watchlist_symbols": settings.PRO_PLAN_MAX_WATCHLIST_SYMBOLS,
            "max_backtests_per_month": settings.PRO_PLAN_MAX_BACKTESTS_PER_MONTH,
            "max_ai_explanations_per_month": settings.PRO_PLAN_MAX_AI_EXPLANATIONS_PER_MONTH,
            "max_paper_accounts": settings.PRO_PLAN_MAX_PAPER_ACCOUNTS,
            "alert_scheduler_enabled": True,
            "webhook_notifications_enabled": True,
        },
        "premium": {
            "max_watchlist_symbols": settings.PREMIUM_PLAN_MAX_WATCHLIST_SYMBOLS,
            "max_backtests_per_month": settings.PREMIUM_PLAN_MAX_BACKTESTS_PER_MONTH,
            "max_ai_explanations_per_month": settings.PREMIUM_PLAN_MAX_AI_EXPLANATIONS_PER_MONTH,
            "max_paper_accounts": settings.PREMIUM_PLAN_MAX_PAPER_ACCOUNTS,
            "alert_scheduler_enabled": True,
            "webhook_notifications_enabled": True,
        },
    }
    return plans.get(plan, plans["free"])
