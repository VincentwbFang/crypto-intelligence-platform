from types import SimpleNamespace

from app.alerts.scheduler import AlertScheduler


class FakeEvaluator:
    def __init__(self) -> None:
        self.called = False

    def evaluate_many(self, symbols: list[str], timeframe: str, limit: int) -> dict:
        self.called = True
        return {
            "symbols": symbols,
            "timeframe": timeframe,
            "results": [],
            "generated_alerts": 0,
            "deduplicated_alerts": 0,
            "alerts": [],
        }


class FakeNotificationService:
    def __init__(self) -> None:
        self.notified = False

    def notify_many(self, alerts: list[dict]) -> list[dict]:
        self.notified = True
        return [{"status": "sent", "deliveries": []}]


def make_settings(enabled: bool = False) -> SimpleNamespace:
    return SimpleNamespace(
        ENABLE_ALERT_SCHEDULER=enabled,
        ALERT_EVALUATION_INTERVAL_SECONDS=300,
        alert_default_symbols_list=["BTC/USDT", "ETH/USDT"],
        ALERT_DEFAULT_TIMEFRAME="1h",
        SIGNAL_DEFAULT_LIMIT=200,
        ENABLE_WEBHOOK_NOTIFICATIONS=False,
        ENABLE_EMAIL_NOTIFICATIONS=False,
    )


def test_scheduler_does_not_start_when_disabled() -> None:
    scheduler = AlertScheduler(
        evaluator=FakeEvaluator(),  # type: ignore[arg-type]
        notification_service=FakeNotificationService(),  # type: ignore[arg-type]
        settings=make_settings(enabled=False),
    )

    scheduler.start()

    assert scheduler.scheduler.running is False


def test_scheduler_run_once_uses_factory_and_closes_session() -> None:
    cleanup_called = False
    evaluator = FakeEvaluator()

    def factory():
        def cleanup() -> None:
            nonlocal cleanup_called
            cleanup_called = True

        return evaluator, cleanup

    scheduler = AlertScheduler(
        evaluator=None,
        notification_service=FakeNotificationService(),  # type: ignore[arg-type]
        settings=make_settings(enabled=True),
        evaluator_factory=factory,
    )

    result = scheduler.run_once()

    assert evaluator.called is True
    assert cleanup_called is True
    assert result["symbols"] == ["BTC/USDT", "ETH/USDT"]
