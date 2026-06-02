from types import SimpleNamespace

from app.alerts.notification import NotificationService


ALERT = {
    "id": 1,
    "symbol": "SOL/USDT",
    "timeframe": "1h",
    "alert_type": "high_signal_score",
    "severity": "medium",
    "title": "High signal score detected",
    "message": "High signal score detected for research monitoring.",
}


def make_settings(
    webhook_enabled: bool = False,
    webhook_url: str | None = None,
    email_enabled: bool = False,
) -> SimpleNamespace:
    return SimpleNamespace(
        ENABLE_WEBHOOK_NOTIFICATIONS=webhook_enabled,
        ALERT_WEBHOOK_URL=webhook_url,
        ENABLE_EMAIL_NOTIFICATIONS=email_enabled,
    )


def test_console_log_notification_returns_success() -> None:
    result = NotificationService(make_settings()).notify_alert(ALERT)

    assert result["status"] == "sent"
    assert result["deliveries"][0] == {"channel": "log", "status": "sent"}


def test_webhook_notification_is_skipped_when_disabled() -> None:
    result = NotificationService(make_settings(webhook_enabled=False)).notify_alert(ALERT)

    webhook = next(item for item in result["deliveries"] if item["channel"] == "webhook")
    assert webhook["status"] == "skipped"


def test_webhook_notification_uses_mocked_httpx_when_enabled(monkeypatch) -> None:
    calls = []

    class FakeResponse:
        def raise_for_status(self) -> None:
            return None

    def fake_post(url: str, json: dict, timeout: float) -> FakeResponse:
        calls.append({"url": url, "json": json, "timeout": timeout})
        return FakeResponse()

    monkeypatch.setattr("app.alerts.notification.httpx.post", fake_post)

    result = NotificationService(
        make_settings(webhook_enabled=True, webhook_url="https://example.test/webhook")
    ).notify_alert(ALERT)

    webhook = next(item for item in result["deliveries"] if item["channel"] == "webhook")
    assert webhook["status"] == "sent"
    assert calls[0]["json"]["event"] == "crypto_alert"


def test_webhook_failure_does_not_crash(monkeypatch) -> None:
    def fake_post(url: str, json: dict, timeout: float) -> None:
        raise RuntimeError("network down")

    monkeypatch.setattr("app.alerts.notification.httpx.post", fake_post)

    result = NotificationService(
        make_settings(webhook_enabled=True, webhook_url="https://example.test/webhook")
    ).notify_alert(ALERT)

    webhook = next(item for item in result["deliveries"] if item["channel"] == "webhook")
    assert webhook["status"] == "failed"


def test_notification_result_includes_status() -> None:
    result = NotificationService(make_settings()).notify_alert(ALERT)

    assert "status" in result
