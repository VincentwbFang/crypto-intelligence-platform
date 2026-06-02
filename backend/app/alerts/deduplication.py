from __future__ import annotations

from datetime import UTC, datetime, timedelta
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import Alert

ACTIVE_ALERT_STATUSES = ("open", "acknowledged")


class AlertDeduplicator:
    def __init__(self, db_session: Session) -> None:
        self.db_session = db_session

    def is_duplicate(self, candidate: dict[str, Any], window_minutes: int) -> bool:
        cutoff = datetime.now(UTC) - timedelta(minutes=window_minutes)
        statement = (
            select(Alert)
            .where(
                Alert.dedup_key == candidate["dedup_key"],
                Alert.created_at >= cutoff,
                Alert.status.in_(ACTIVE_ALERT_STATUSES),
            )
            .limit(1)
        )
        if candidate.get("workspace_id"):
            statement = statement.where(Alert.workspace_id == candidate["workspace_id"])
        existing = self.db_session.scalars(statement).first()
        return existing is not None

    def filter_new_alerts(
        self,
        candidates: list[dict[str, Any]],
        window_minutes: int,
    ) -> list[dict[str, Any]]:
        return [
            candidate
            for candidate in candidates
            if not self.is_duplicate(candidate, window_minutes)
        ]
