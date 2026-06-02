from __future__ import annotations

from typing import Any

from app.alerts.deduplication import AlertDeduplicator
from app.alerts.rules import AlertRuleEngine
from app.core.config import settings
from app.services.alert_service import AlertService
from app.services.signal_service import SignalService


class AlertEvaluator:
    def __init__(
        self,
        signal_service: SignalService,
        alert_rule_engine: AlertRuleEngine,
        alert_deduplicator: AlertDeduplicator,
        workspace_id: str | None = None,
        user_id: str | None = None,
    ) -> None:
        self.signal_service = signal_service
        self.alert_rule_engine = alert_rule_engine
        self.alert_deduplicator = alert_deduplicator
        self.workspace_id = workspace_id
        self.user_id = user_id
        self.alert_service = AlertService(signal_service.db_session, workspace_id, user_id)

    def evaluate_symbol(self, symbol: str, timeframe: str, limit: int) -> dict[str, Any]:
        previous_signal = self.signal_service.get_latest_signal(
            symbol=symbol,
            timeframe=timeframe,
        )
        current_signal = self.signal_service.generate_and_store_latest_signal(
            symbol=symbol,
            timeframe=timeframe,
            limit=limit,
        )
        candidates = self.alert_rule_engine.evaluate_signal(
            current_signal,
            previous_signal=previous_signal,
            config={
                "signal_score_threshold": settings.ALERT_SIGNAL_SCORE_THRESHOLD,
                "high_risk_threshold": settings.ALERT_HIGH_RISK_THRESHOLD,
            },
        )
        for candidate in candidates:
            candidate["workspace_id"] = self.workspace_id
            candidate["created_by_user_id"] = self.user_id
        new_candidates = self.alert_deduplicator.filter_new_alerts(
            candidates,
            window_minutes=settings.ALERT_DEDUP_WINDOW_MINUTES,
        )
        alerts = self.alert_service.create_alerts(new_candidates)
        return {
            "symbol": symbol,
            "timeframe": timeframe,
            "generated_alerts": len(alerts),
            "deduplicated_alerts": len(candidates) - len(new_candidates),
            "alerts": alerts,
        }

    def evaluate_many(
        self,
        symbols: list[str],
        timeframe: str,
        limit: int,
    ) -> dict[str, Any]:
        results = [
            self.evaluate_symbol(symbol=symbol, timeframe=timeframe, limit=limit)
            for symbol in symbols
        ]
        return {
            "symbols": symbols,
            "timeframe": timeframe,
            "results": results,
            "generated_alerts": sum(item["generated_alerts"] for item in results),
            "deduplicated_alerts": sum(item["deduplicated_alerts"] for item in results),
            "alerts": [alert for item in results for alert in item["alerts"]],
        }
