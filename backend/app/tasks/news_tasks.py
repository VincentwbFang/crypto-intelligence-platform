from __future__ import annotations

import logging
from typing import Any

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

from app.core.config import settings
from app.db.session import SessionLocal
from app.services.news.news_alert_service import NewsAlertService
from app.services.news.news_broadcast_service import NewsBroadcastService
from app.services.news.news_service import NewsService

logger = logging.getLogger(__name__)


def fetch_crypto_news() -> dict[str, Any]:
    db = SessionLocal()
    try:
        logger.info("Fetching crypto news")
        return NewsService(db).fetch_news()
    except Exception:
        logger.exception("fetch_crypto_news task failed")
        return {"error": "fetch_crypto_news failed"}
    finally:
        db.close()


def analyze_unprocessed_news() -> dict[str, Any]:
    db = SessionLocal()
    try:
        logger.info("Analyzing unprocessed crypto news")
        result = NewsService(db).analyze_unprocessed_news()
        alerts = NewsAlertService(db).create_alerts_for_recent_news()
        result["alerts_created"] = len(alerts)
        return result
    except Exception:
        logger.exception("analyze_unprocessed_news task failed")
        return {"error": "analyze_unprocessed_news failed"}
    finally:
        db.close()


def generate_intraday_briefing() -> dict[str, Any]:
    db = SessionLocal()
    try:
        logger.info("Generating intraday news briefing")
        return NewsBroadcastService(db).generate_briefing("intraday")
    except Exception:
        logger.exception("generate_intraday_briefing task failed")
        return {"error": "generate_intraday_briefing failed"}
    finally:
        db.close()


def generate_morning_briefing() -> dict[str, Any]:
    db = SessionLocal()
    try:
        logger.info("Generating morning news briefing")
        return NewsBroadcastService(db).generate_briefing("morning")
    except Exception:
        logger.exception("generate_morning_briefing task failed")
        return {"error": "generate_morning_briefing failed"}
    finally:
        db.close()


def check_breaking_news_alerts() -> dict[str, Any]:
    db = SessionLocal()
    try:
        logger.info("Checking breaking news alerts")
        alerts = NewsAlertService(db).create_alerts_for_recent_news()
        broadcast = NewsBroadcastService(db).generate_breaking_for_latest_critical()
        return {"alerts_created": len(alerts), "broadcast": broadcast}
    except Exception:
        logger.exception("check_breaking_news_alerts task failed")
        return {"error": "check_breaking_news_alerts failed"}
    finally:
        db.close()


class NewsScheduler:
    def __init__(self, settings_obj=settings) -> None:
        self.settings = settings_obj
        self.scheduler = BackgroundScheduler(timezone=settings_obj.NEWS_TIMEZONE)

    def start(self) -> None:
        if not self.settings.ENABLE_NEWS_SCHEDULER:
            return
        self._add_interval_job(
            fetch_crypto_news,
            "fetch_crypto_news",
            self.settings.NEWS_FETCH_INTERVAL_MINUTES,
        )
        self._add_interval_job(
            analyze_unprocessed_news,
            "analyze_unprocessed_news",
            self.settings.NEWS_ANALYZE_INTERVAL_MINUTES,
        )
        self._add_interval_job(
            generate_intraday_briefing,
            "generate_intraday_briefing",
            self.settings.NEWS_BRIEFING_INTERVAL_MINUTES,
        )
        self._add_interval_job(check_breaking_news_alerts, "check_breaking_news_alerts", 5)
        hour, minute = _parse_hhmm(self.settings.NEWS_MORNING_BRIEFING_TIME)
        if self.scheduler.get_job("generate_morning_briefing") is None:
            self.scheduler.add_job(
                generate_morning_briefing,
                CronTrigger(hour=hour, minute=minute, timezone=self.settings.NEWS_TIMEZONE),
                id="generate_morning_briefing",
                replace_existing=True,
                max_instances=1,
                coalesce=True,
            )
        if not self.scheduler.running:
            self.scheduler.start()
            logger.info("News scheduler started")

    def shutdown(self) -> None:
        if self.scheduler.running:
            self.scheduler.shutdown(wait=False)
            logger.info("News scheduler stopped")

    def _add_interval_job(self, func: Any, job_id: str, minutes: int) -> None:
        if self.scheduler.get_job(job_id) is None:
            self.scheduler.add_job(
                func,
                "interval",
                minutes=minutes,
                id=job_id,
                replace_existing=True,
                max_instances=1,
                coalesce=True,
            )


def _parse_hhmm(value: str) -> tuple[int, int]:
    try:
        hour_raw, minute_raw = value.split(":", 1)
        hour = min(max(int(hour_raw), 0), 23)
        minute = min(max(int(minute_raw), 0), 59)
        return hour, minute
    except Exception:
        return 8, 30
