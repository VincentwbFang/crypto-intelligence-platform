from __future__ import annotations

import logging
from collections.abc import Callable
from typing import Any

from apscheduler.schedulers.background import BackgroundScheduler
from sqlalchemy.orm import Session

from app.core.config import settings
from app.data.exchanges.ccxt_client import MarketDataError, CCXTMarketClient
from app.data.ingestion.ohlcv_ingestor import OHLCVIngestor
from app.db.session import SessionLocal
from app.services.relative_strength_alert_service import RelativeStrengthAlertService
from app.services.relative_strength_service import RelativeStrengthService

logger = logging.getLogger(__name__)


def calculate_relative_strength_once(
    db_session: Session | None = None,
    *,
    refresh_market_data: bool = True,
) -> dict[str, Any]:
    owns_session = db_session is None
    db = db_session or SessionLocal()
    try:
        symbols = _configured_symbols()
        skipped: dict[str, str] = {}
        inserted: dict[str, int] = {}
        if refresh_market_data:
            client = CCXTMarketClient(settings.DEFAULT_EXCHANGE)
            ingestor = OHLCVIngestor(db, client)
            for symbol in symbols:
                try:
                    inserted[symbol] = ingestor.ingest_symbol(
                        symbol=symbol,
                        timeframe=settings.RELATIVE_STRENGTH_TIMEFRAME,
                        limit=settings.RELATIVE_STRENGTH_LOOKBACK_LIMIT,
                    )
                except MarketDataError as exc:
                    skipped[symbol] = str(exc)
                    logger.warning("Skipped relative strength ingestion for %s: %s", symbol, exc)
                except Exception as exc:
                    skipped[symbol] = "Unexpected ingestion failure."
                    logger.exception("Failed relative strength ingestion for %s", symbol)

        service = RelativeStrengthService(db)
        snapshots = service.calculate_and_store(
            symbols=settings.relative_strength_symbols_list,
            base_symbol=settings.RELATIVE_STRENGTH_BASE_SYMBOL,
            timeframe=settings.RELATIVE_STRENGTH_TIMEFRAME,
        )
        alerts = RelativeStrengthAlertService(db).evaluate_and_create_alerts(snapshots)
        return {
            "symbols": settings.relative_strength_symbols_list,
            "base_symbol": settings.RELATIVE_STRENGTH_BASE_SYMBOL,
            "timeframe": settings.RELATIVE_STRENGTH_TIMEFRAME,
            "inserted": inserted,
            "skipped": skipped,
            "snapshot_count": len(snapshots),
            "alert_count": len(alerts),
            "alerts": alerts,
        }
    finally:
        if owns_session:
            db.close()


class RelativeStrengthScheduler:
    def __init__(
        self,
        settings_obj=settings,
        task: Callable[[], dict[str, Any]] | None = None,
    ) -> None:
        self.settings = settings_obj
        self.task = task or calculate_relative_strength_once
        self.scheduler = BackgroundScheduler(timezone="UTC")

    def start(self) -> None:
        if not self.settings.ENABLE_RELATIVE_STRENGTH_SCHEDULER:
            return
        if self.scheduler.get_job("relative_strength_calculation") is None:
            self.scheduler.add_job(
                self.run_once,
                "interval",
                seconds=self.settings.RELATIVE_STRENGTH_INTERVAL_SECONDS,
                id="relative_strength_calculation",
                replace_existing=True,
                max_instances=1,
                coalesce=True,
            )
        if not self.scheduler.running:
            self.scheduler.start()
            logger.info("Relative strength scheduler started")

    def run_once(self) -> dict[str, Any]:
        logger.info("Running relative strength calculation")
        return self.task()

    def shutdown(self) -> None:
        if self.scheduler.running:
            self.scheduler.shutdown(wait=False)
            logger.info("Relative strength scheduler stopped")


def _configured_symbols() -> list[str]:
    symbols = [settings.RELATIVE_STRENGTH_BASE_SYMBOL, *settings.relative_strength_symbols_list]
    return list(dict.fromkeys(symbols))
