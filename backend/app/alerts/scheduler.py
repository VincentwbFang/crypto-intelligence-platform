from __future__ import annotations

from collections.abc import Callable
import logging
from typing import Any

from apscheduler.schedulers.background import BackgroundScheduler

from app.alerts.evaluator import AlertEvaluator
from app.alerts.notification import NotificationService

logger = logging.getLogger(__name__)

ALERT_JOB_ID = "alert_evaluation"
EvaluatorFactory = Callable[[], tuple[AlertEvaluator, Callable[[], None] | None]]


class AlertScheduler:
    def __init__(
        self,
        evaluator: AlertEvaluator | None,
        notification_service: NotificationService,
        settings: Any,
        evaluator_factory: EvaluatorFactory | None = None,
    ) -> None:
        self.evaluator = evaluator
        self.notification_service = notification_service
        self.settings = settings
        self.evaluator_factory = evaluator_factory
        self.scheduler = BackgroundScheduler(timezone="UTC")

    def start(self) -> None:
        if not self.settings.ENABLE_ALERT_SCHEDULER:
            logger.info("Alert scheduler is disabled.")
            return
        if self.scheduler.get_job(ALERT_JOB_ID) is None:
            self.scheduler.add_job(
                self.run_once,
                "interval",
                seconds=self.settings.ALERT_EVALUATION_INTERVAL_SECONDS,
                id=ALERT_JOB_ID,
                replace_existing=True,
            )
        if not self.scheduler.running:
            self.scheduler.start()
            logger.info("Alert scheduler started.")

    def shutdown(self) -> None:
        if self.scheduler.running:
            self.scheduler.shutdown(wait=False)
            logger.info("Alert scheduler stopped.")

    def run_once(self) -> dict[str, Any]:
        evaluator = self.evaluator
        cleanup: Callable[[], None] | None = None
        if self.evaluator_factory is not None:
            evaluator, cleanup = self.evaluator_factory()
        if evaluator is None:
            raise RuntimeError("Alert scheduler evaluator is not configured.")

        try:
            result = evaluator.evaluate_many(
                symbols=self.settings.alert_default_symbols_list,
                timeframe=self.settings.ALERT_DEFAULT_TIMEFRAME,
                limit=self.settings.SIGNAL_DEFAULT_LIMIT,
            )
            notifications: list[dict[str, Any]] = []
            if (
                self.settings.ENABLE_WEBHOOK_NOTIFICATIONS
                or self.settings.ENABLE_EMAIL_NOTIFICATIONS
            ):
                notifications = self.notification_service.notify_many(result["alerts"])
            result["notifications"] = notifications
            return result
        finally:
            if cleanup is not None:
                cleanup()
