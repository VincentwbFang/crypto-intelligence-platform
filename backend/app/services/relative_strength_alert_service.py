from __future__ import annotations

import logging
from datetime import UTC, datetime, timedelta
from decimal import Decimal
from typing import Any

from sqlalchemy import desc, select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.models import RelativeStrengthAlert, RelativeStrengthSnapshot
from app.services.compliance_guardrail import ComplianceGuardrail
from app.services.deepseek_service import DeepSeekService
from app.services.relative_strength_service import percentile_ranks

logger = logging.getLogger(__name__)

DEDUP_WINDOW_HOURS = 6


class RelativeStrengthAlertService:
    def __init__(
        self,
        db_session: Session,
        deepseek_service: DeepSeekService | None = None,
    ) -> None:
        self.db_session = db_session
        self.deepseek_service = deepseek_service or DeepSeekService(
            enabled=settings.ENABLE_AI_RELATIVE_STRENGTH_ALERT_EXPLANATION
        )

    def evaluate_and_create_alerts(self, snapshots: list[dict[str, Any]]) -> list[dict[str, Any]]:
        candidates = self.evaluate_alert_candidates(snapshots)
        alerts: list[dict[str, Any]] = []
        for candidate in candidates:
            if self.is_duplicate(candidate["symbol"], candidate["alert_type"]):
                continue
            alerts.append(self.create_alert(candidate))
        if alerts:
            self.db_session.commit()
        return alerts

    def evaluate_alert_candidates(self, snapshots: list[dict[str, Any]]) -> list[dict[str, Any]]:
        candidates: list[dict[str, Any]] = []
        excess_24h_percentiles = percentile_ranks(
            {
                snapshot["symbol"]: snapshot.get("excess_return_24h")
                for snapshot in snapshots
                if snapshot.get("brsi_score") is not None
            }
        )
        for snapshot in snapshots:
            score = _safe_float(snapshot.get("brsi_score"))
            if score is None:
                continue
            previous_score = self._get_previous_score(snapshot)
            candidates.extend(self._crossing_alerts(snapshot, score, previous_score))
            candidates.extend(self._movement_alerts(snapshot, score))
            candidates.extend(self._percentile_alerts(snapshot, excess_24h_percentiles))
        return candidates

    def create_alert(self, candidate: dict[str, Any]) -> dict[str, Any]:
        message = self._append_optional_ai_explanation(candidate)
        alert = RelativeStrengthAlert(
            symbol=candidate["symbol"],
            alert_type=candidate["alert_type"],
            alert_level=candidate["alert_level"],
            title=candidate["title"],
            message=message,
            brsi_score=_decimal_or_none(candidate.get("brsi_score")),
            previous_brsi_score=_decimal_or_none(candidate.get("previous_brsi_score")),
            change_value=_decimal_or_none(candidate.get("change_value")),
            is_read=False,
        )
        self.db_session.add(alert)
        self.db_session.flush()
        return _alert_to_dict(alert)

    def list_alerts(self, limit: int = 50, unread_only: bool = False) -> list[dict[str, Any]]:
        statement = select(RelativeStrengthAlert).order_by(desc(RelativeStrengthAlert.created_at))
        if unread_only:
            statement = statement.where(RelativeStrengthAlert.is_read.is_(False))
        rows = self.db_session.scalars(statement.limit(limit)).all()
        return [_alert_to_dict(row) for row in rows]

    def mark_read(self, alert_id: int) -> dict[str, Any] | None:
        alert = self.db_session.get(RelativeStrengthAlert, alert_id)
        if alert is None:
            return None
        alert.is_read = True
        self.db_session.commit()
        self.db_session.refresh(alert)
        return _alert_to_dict(alert)

    def is_duplicate(self, symbol: str, alert_type: str) -> bool:
        cutoff = datetime.now(UTC) - timedelta(hours=DEDUP_WINDOW_HOURS)
        existing = self.db_session.scalar(
            select(RelativeStrengthAlert.id)
            .where(
                RelativeStrengthAlert.symbol == symbol,
                RelativeStrengthAlert.alert_type == alert_type,
                RelativeStrengthAlert.created_at >= cutoff,
            )
            .limit(1)
        )
        return existing is not None

    def _crossing_alerts(
        self,
        snapshot: dict[str, Any],
        score: float,
        previous_score: float | None,
    ) -> list[dict[str, Any]]:
        if previous_score is None:
            return []
        alerts = []
        if score >= 75 and previous_score < 60:
            alerts.append(
                self._build_candidate(
                    snapshot=snapshot,
                    alert_type="relative_strength_breakout",
                    alert_level="high",
                    title="Relative strength breakout detected",
                    message=(
                        f"{snapshot['symbol']} BRSI moved from {previous_score:.1f} "
                        f"to {score:.1f}, showing a strong relative shift versus BTC."
                    ),
                    previous_score=previous_score,
                    change_value=score - previous_score,
                )
            )
        if score <= 35 and previous_score > 50:
            alerts.append(
                self._build_candidate(
                    snapshot=snapshot,
                    alert_type="relative_weakness_warning",
                    alert_level="high",
                    title="Relative weakness warning",
                    message=(
                        f"{snapshot['symbol']} BRSI moved from {previous_score:.1f} "
                        f"to {score:.1f}, showing weaker behavior versus BTC."
                    ),
                    previous_score=previous_score,
                    change_value=score - previous_score,
                )
            )
        return alerts

    def _movement_alerts(self, snapshot: dict[str, Any], score: float) -> list[dict[str, Any]]:
        alerts = []
        change_1h = _safe_float(snapshot.get("brsi_change_1h"))
        change_4h = _safe_float(snapshot.get("brsi_change_4h"))
        if change_1h is not None and abs(change_1h) >= 15:
            alerts.append(
                self._build_candidate(
                    snapshot=snapshot,
                    alert_type="abnormal_1h_movement",
                    alert_level="medium",
                    title="Abnormal 1h BRSI movement",
                    message=(
                        f"{snapshot['symbol']} BRSI changed by {change_1h:.1f} "
                        "points within roughly one hour."
                    ),
                    previous_score=score - change_1h,
                    change_value=change_1h,
                )
            )
        if change_4h is not None and abs(change_4h) >= 25:
            alerts.append(
                self._build_candidate(
                    snapshot=snapshot,
                    alert_type="abnormal_4h_movement",
                    alert_level="medium",
                    title="Abnormal 4h BRSI movement",
                    message=(
                        f"{snapshot['symbol']} BRSI changed by {change_4h:.1f} "
                        "points within roughly four hours."
                    ),
                    previous_score=score - change_4h,
                    change_value=change_4h,
                )
            )
        return alerts

    def _percentile_alerts(
        self,
        snapshot: dict[str, Any],
        excess_24h_percentiles: dict[str, float | None],
    ) -> list[dict[str, Any]]:
        percentile = excess_24h_percentiles.get(snapshot["symbol"])
        if percentile is None:
            return []
        score = _safe_float(snapshot.get("brsi_score"))
        previous_score = self._get_previous_score(snapshot)
        if percentile >= 95:
            return [
                self._build_candidate(
                    snapshot=snapshot,
                    alert_type="top_relative_outperformer",
                    alert_level="info",
                    title="Top relative outperformer",
                    message=(
                        f"{snapshot['symbol']} 24h excess return versus BTC is in the "
                        "top percentile group among tracked coins."
                    ),
                    previous_score=previous_score,
                    change_value=None if score is None or previous_score is None else score - previous_score,
                )
            ]
        if percentile <= 5:
            return [
                self._build_candidate(
                    snapshot=snapshot,
                    alert_type="severe_relative_underperformer",
                    alert_level="medium",
                    title="Severe relative underperformance",
                    message=(
                        f"{snapshot['symbol']} 24h excess return versus BTC is in the "
                        "bottom percentile group among tracked coins."
                    ),
                    previous_score=previous_score,
                    change_value=None if score is None or previous_score is None else score - previous_score,
                )
            ]
        return []

    def _build_candidate(
        self,
        *,
        snapshot: dict[str, Any],
        alert_type: str,
        alert_level: str,
        title: str,
        message: str,
        previous_score: float | None,
        change_value: float | None,
    ) -> dict[str, Any]:
        return {
            "symbol": snapshot["symbol"],
            "alert_type": alert_type,
            "alert_level": alert_level,
            "title": title,
            "message": message,
            "brsi_score": snapshot.get("brsi_score"),
            "previous_brsi_score": previous_score,
            "change_value": change_value,
            "snapshot": snapshot,
        }

    def _get_previous_score(self, snapshot: dict[str, Any]) -> float | None:
        created_at = _parse_datetime(snapshot.get("created_at")) or datetime.now(UTC)
        previous_score = self.db_session.scalar(
            select(RelativeStrengthSnapshot.brsi_score)
            .where(
                RelativeStrengthSnapshot.symbol == snapshot["symbol"],
                RelativeStrengthSnapshot.created_at < created_at,
                RelativeStrengthSnapshot.brsi_score.is_not(None),
            )
            .order_by(desc(RelativeStrengthSnapshot.created_at))
            .limit(1)
        )
        return None if previous_score is None else float(previous_score)

    def _append_optional_ai_explanation(self, candidate: dict[str, Any]) -> str:
        message = str(candidate["message"])
        if not settings.ENABLE_AI_RELATIVE_STRENGTH_ALERT_EXPLANATION:
            return message
        prompt = (
            "Explain this BTC relative strength alert using only the provided JSON. "
            "Do not provide trading instructions, price targets, certainty claims, "
            "or leverage language. Return JSON with keys summary, timeframe_confirmation, "
            "volume_confirmation, risks_to_monitor, disclaimer."
        )
        explanation = self.deepseek_service.generate_json(
            system_prompt=prompt,
            payload={"alert": candidate},
        )
        sanitized = ComplianceGuardrail.validate_ai_output(explanation)["sanitized_output"]
        summary = sanitized.get("summary") if isinstance(sanitized, dict) else None
        if not summary:
            return message
        return f"{message} Explanation: {summary}"


def _alert_to_dict(alert: RelativeStrengthAlert) -> dict[str, Any]:
    return {
        "id": alert.id,
        "symbol": alert.symbol,
        "alert_type": alert.alert_type,
        "alert_level": alert.alert_level,
        "title": alert.title,
        "message": alert.message,
        "brsi_score": _float_or_none(alert.brsi_score),
        "previous_brsi_score": _float_or_none(alert.previous_brsi_score),
        "change_value": _float_or_none(alert.change_value),
        "is_read": alert.is_read,
        "created_at": alert.created_at.isoformat(),
    }


def _parse_datetime(value: Any) -> datetime | None:
    if isinstance(value, datetime):
        return value
    if isinstance(value, str):
        try:
            return datetime.fromisoformat(value)
        except ValueError:
            logger.warning("Invalid relative strength snapshot timestamp: %s", value)
            return None
    return None


def _safe_float(value: Any) -> float | None:
    if value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _float_or_none(value: Any) -> float | None:
    return None if value is None else float(value)


def _decimal_or_none(value: Any) -> Decimal | None:
    return None if value is None else Decimal(str(value))
