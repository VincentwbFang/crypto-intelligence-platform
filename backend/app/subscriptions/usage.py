from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from sqlalchemy import extract, func, select
from sqlalchemy.orm import Session

from app.db.models import UsageEvent

USAGE_EVENT_TYPES = (
    "ai_explanation",
    "backtest_run",
    "paper_order",
    "alert_evaluation",
    "watchlist_symbol_added",
)


class UsageTrackingService:
    def __init__(self, db_session: Session) -> None:
        self.db_session = db_session

    def record_event(
        self,
        workspace_id: str,
        user_id: str | None,
        event_type: str,
        quantity: int = 1,
        metadata: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        event = UsageEvent(
            workspace_id=workspace_id,
            user_id=user_id,
            event_type=event_type,
            quantity=quantity,
            event_metadata=metadata or {},
        )
        self.db_session.add(event)
        self.db_session.commit()
        self.db_session.refresh(event)
        return self._to_dict(event)

    def get_monthly_usage(self, workspace_id: str, event_type: str) -> int:
        now = datetime.now(UTC)
        statement = select(func.coalesce(func.sum(UsageEvent.quantity), 0)).where(
            UsageEvent.workspace_id == workspace_id,
            UsageEvent.event_type == event_type,
            extract("year", UsageEvent.created_at) == now.year,
            extract("month", UsageEvent.created_at) == now.month,
        )
        return int(self.db_session.scalar(statement) or 0)

    def get_usage_summary(self, workspace_id: str) -> dict[str, Any]:
        usage = {
            event_type: self.get_monthly_usage(workspace_id, event_type)
            for event_type in USAGE_EVENT_TYPES
        }
        return {"workspace_id": workspace_id, "usage": usage}

    @staticmethod
    def _to_dict(event: UsageEvent) -> dict[str, Any]:
        return {
            "id": event.id,
            "workspace_id": event.workspace_id,
            "user_id": event.user_id,
            "event_type": event.event_type,
            "quantity": event.quantity,
            "metadata": event.event_metadata or {},
            "created_at": event.created_at.isoformat() if event.created_at else None,
        }
