from __future__ import annotations

import logging
from typing import Any

import httpx

logger = logging.getLogger(__name__)


class NotificationService:
    def __init__(self, settings: Any) -> None:
        self.settings = settings

    def notify_alert(self, alert: dict[str, Any]) -> dict[str, Any]:
        deliveries = [self._notify_log(alert), self._notify_webhook(alert)]
        deliveries.append(self._notify_email_placeholder(alert))
        return {
            "alert_id": alert.get("id"),
            "status": self._overall_status(deliveries),
            "deliveries": deliveries,
        }

    def notify_many(self, alerts: list[dict[str, Any]]) -> list[dict[str, Any]]:
        return [self.notify_alert(alert) for alert in alerts]

    def _notify_log(self, alert: dict[str, Any]) -> dict[str, str]:
        logger.info(
            "Alert notification: %s %s %s",
            alert.get("symbol"),
            alert.get("alert_type"),
            alert.get("severity"),
        )
        return {"channel": "log", "status": "sent"}

    def _notify_webhook(self, alert: dict[str, Any]) -> dict[str, str]:
        if not self.settings.ENABLE_WEBHOOK_NOTIFICATIONS:
            return {"channel": "webhook", "status": "skipped", "reason": "disabled"}
        webhook_url = self.settings.ALERT_WEBHOOK_URL
        if not webhook_url:
            return {"channel": "webhook", "status": "skipped", "reason": "missing_url"}

        payload = {"event": "crypto_alert", "alert": alert}
        last_error = "unknown webhook error"
        for _attempt in range(3):
            try:
                response = httpx.post(webhook_url, json=payload, timeout=10.0)
                response.raise_for_status()
                return {"channel": "webhook", "status": "sent"}
            except Exception as exc:
                last_error = exc.__class__.__name__
                logger.warning("Alert webhook delivery failed: %s", last_error)
        return {"channel": "webhook", "status": "failed", "error": last_error}

    def _notify_email_placeholder(self, alert: dict[str, Any]) -> dict[str, str]:
        if not self.settings.ENABLE_EMAIL_NOTIFICATIONS:
            return {"channel": "email", "status": "skipped", "reason": "disabled"}
        # TODO: Implement SMTP or provider-backed email delivery in a later phase.
        logger.info("Email notification is configured as a placeholder for alert %s", alert.get("id"))
        return {"channel": "email", "status": "skipped", "reason": "not_implemented"}

    def _overall_status(self, deliveries: list[dict[str, str]]) -> str:
        if any(item["status"] == "failed" for item in deliveries):
            return "partial_failure"
        if any(item["status"] == "sent" for item in deliveries):
            return "sent"
        return "skipped"
