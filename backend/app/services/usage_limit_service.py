from __future__ import annotations

from typing import Any

from sqlalchemy.orm import Session

from app.subscriptions.feature_gates import FeatureGateService
from app.subscriptions.usage import UsageTrackingService


class UsageLimitService:
    """Convenience facade for plan checks plus usage recording."""

    def __init__(self, db_session: Session) -> None:
        self.db_session = db_session
        self.feature_gates = FeatureGateService(db_session)
        self.usage = UsageTrackingService(db_session)

    def check_feature(self, workspace_id: str, feature_name: str) -> dict[str, Any]:
        return self.feature_gates.check_feature(workspace_id, feature_name)

    def enforce_feature(
        self,
        workspace_id: str,
        feature_name: str,
        event_type: str | None = None,
    ) -> None:
        self.feature_gates.enforce_or_raise(workspace_id, feature_name, event_type)

    def record_usage(
        self,
        workspace_id: str,
        user_id: str | None,
        event_type: str,
        quantity: int = 1,
        metadata: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        return self.usage.record_event(
            workspace_id=workspace_id,
            user_id=user_id,
            event_type=event_type,
            quantity=quantity,
            metadata=metadata,
        )

    def check_and_record(
        self,
        *,
        workspace_id: str,
        user_id: str | None,
        feature_name: str,
        event_type: str,
        quantity: int = 1,
        metadata: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        self.enforce_feature(workspace_id, feature_name, event_type)
        return self.record_usage(workspace_id, user_id, event_type, quantity, metadata)
