from __future__ import annotations

from datetime import UTC, datetime
from decimal import Decimal
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.alerts.severity import ALERT_SEVERITIES
from app.db.models import Alert

ALERT_STATUSES = ("open", "acknowledged", "resolved", "dismissed")


class AlertService:
    def __init__(
        self,
        db_session: Session,
        workspace_id: str | None = None,
        user_id: str | None = None,
    ) -> None:
        self.db_session = db_session
        self.workspace_id = workspace_id
        self.user_id = user_id

    def create_alert(self, candidate: dict[str, Any]) -> dict[str, Any]:
        alert = self._build_alert(candidate)
        self.db_session.add(alert)
        self.db_session.commit()
        self.db_session.refresh(alert)
        return self._to_dict(alert)

    def create_alerts(self, candidates: list[dict[str, Any]]) -> list[dict[str, Any]]:
        alerts = [self._build_alert(candidate) for candidate in candidates]
        if not alerts:
            return []
        self.db_session.add_all(alerts)
        self.db_session.commit()
        for alert in alerts:
            self.db_session.refresh(alert)
        return [self._to_dict(alert) for alert in alerts]

    def get_alert(self, alert_id: int) -> dict[str, Any] | None:
        alert = self.db_session.get(Alert, alert_id)
        if alert is None or not self._is_visible(alert):
            return None
        return self._to_dict(alert)

    def list_alerts(
        self,
        symbol: str | None = None,
        timeframe: str | None = None,
        severity: str | None = None,
        alert_type: str | None = None,
        status: str | None = None,
        limit: int = 100,
    ) -> list[dict[str, Any]]:
        statement = select(Alert).order_by(Alert.created_at.desc()).limit(limit)
        if self.workspace_id:
            statement = statement.where(Alert.workspace_id == self.workspace_id)
        if symbol:
            statement = statement.where(Alert.symbol == symbol)
        if timeframe:
            statement = statement.where(Alert.timeframe == timeframe)
        if severity:
            statement = statement.where(Alert.severity == severity)
        if alert_type:
            statement = statement.where(Alert.alert_type == alert_type)
        if status:
            statement = statement.where(Alert.status == status)
        return [self._to_dict(alert) for alert in self.db_session.scalars(statement)]

    def update_alert_status(self, alert_id: int, status: str) -> dict[str, Any]:
        self._validate_status(status)
        alert = self.db_session.get(Alert, alert_id)
        if alert is None or not self._is_visible(alert):
            raise LookupError("Alert not found.")
        alert.status = status
        alert.updated_at = datetime.now(UTC)
        if status == "resolved":
            alert.resolved_at = datetime.now(UTC)
        self.db_session.commit()
        self.db_session.refresh(alert)
        return self._to_dict(alert)

    def mark_alert_resolved(self, alert_id: int) -> dict[str, Any]:
        alert = self.db_session.get(Alert, alert_id)
        if alert is None or not self._is_visible(alert):
            raise LookupError("Alert not found.")
        alert.status = "resolved"
        alert.resolved_at = datetime.now(UTC)
        alert.updated_at = datetime.now(UTC)
        self.db_session.commit()
        self.db_session.refresh(alert)
        return self._to_dict(alert)

    def get_recent_alerts(
        self,
        symbol: str | None = None,
        limit: int = 50,
    ) -> list[dict[str, Any]]:
        statement = select(Alert).order_by(Alert.created_at.desc()).limit(limit)
        if self.workspace_id:
            statement = statement.where(Alert.workspace_id == self.workspace_id)
        if symbol:
            statement = statement.where(Alert.symbol == symbol)
        return [self._to_dict(alert) for alert in self.db_session.scalars(statement)]

    def _build_alert(self, candidate: dict[str, Any]) -> Alert:
        severity = str(candidate.get("severity") or "info").lower()
        status = str(candidate.get("status") or "open").lower()
        self._validate_severity(severity)
        self._validate_status(status)
        return Alert(
            workspace_id=candidate.get("workspace_id") or self.workspace_id,
            created_by_user_id=candidate.get("created_by_user_id") or self.user_id,
            symbol=str(candidate["symbol"]),
            timeframe=str(candidate.get("timeframe") or "1h"),
            timestamp=self._parse_timestamp(candidate["timestamp"]),
            alert_type=str(candidate["alert_type"]),
            severity=severity,
            title=str(candidate.get("title") or "Market alert"),
            message=str(candidate["message"]),
            status=status,
            source=candidate.get("source"),
            signal_score=self._decimal_or_none(candidate.get("signal_score")),
            risk_level=candidate.get("risk_level"),
            setup_type=candidate.get("setup_type"),
            dedup_key=str(candidate["dedup_key"]),
            raw_payload=candidate.get("raw_payload"),
        )

    def _is_visible(self, alert: Alert) -> bool:
        return not self.workspace_id or alert.workspace_id == self.workspace_id

    def _validate_severity(self, severity: str) -> None:
        if severity not in ALERT_SEVERITIES:
            raise ValueError(f"Invalid alert severity: {severity}")

    def _validate_status(self, status: str) -> None:
        if status not in ALERT_STATUSES:
            raise ValueError(f"Invalid alert status: {status}")

    def _decimal_or_none(self, value: Any) -> Decimal | None:
        if value is None:
            return None
        return Decimal(str(value))

    def _parse_timestamp(self, value: str | datetime) -> datetime:
        if isinstance(value, datetime):
            return value
        return datetime.fromisoformat(str(value).replace("Z", "+00:00"))

    def _to_dict(self, alert: Alert) -> dict[str, Any]:
        return {
            "id": alert.id,
            "workspace_id": alert.workspace_id,
            "created_by_user_id": alert.created_by_user_id,
            "symbol": alert.symbol,
            "timeframe": alert.timeframe,
            "timestamp": _isoformat(alert.timestamp),
            "alert_type": alert.alert_type,
            "severity": alert.severity,
            "title": alert.title,
            "message": alert.message,
            "status": alert.status,
            "source": alert.source,
            "signal_score": _float_or_none(alert.signal_score),
            "risk_level": alert.risk_level,
            "setup_type": alert.setup_type,
            "dedup_key": alert.dedup_key,
            "raw_payload": alert.raw_payload,
            "created_at": _isoformat(alert.created_at),
            "updated_at": _isoformat(alert.updated_at),
            "resolved_at": _isoformat(alert.resolved_at),
        }


def _float_or_none(value: Any) -> float | None:
    if value is None:
        return None
    return float(value)


def _isoformat(value: datetime | None) -> str | None:
    if value is None:
        return None
    return value.isoformat()
