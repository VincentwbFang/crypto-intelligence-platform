from __future__ import annotations

import logging
from collections.abc import Callable
from datetime import UTC, datetime, timedelta
from typing import Any

from apscheduler.schedulers.background import BackgroundScheduler
from sqlalchemy.orm import Session

from app.core.config import settings
from app.data.exchanges.ccxt_client import CCXTMarketClient, MarketDataError
from app.data.ingestion.ohlcv_ingestor import OHLCVIngestor
from app.db.session import SessionLocal
from app.observability.metrics import track_feature_event
from app.services.market_universe_service import MarketUniverseService

logger = logging.getLogger(__name__)

MARKET_DATA_JOB_ID = "market_data_update"


def update_market_data_once(
    db_session: Session | None = None,
    *,
    symbols: list[str] | None = None,
) -> dict[str, Any]:
    owns_session = db_session is None
    db = db_session or SessionLocal()
    try:
        market_client = CCXTMarketClient(settings.DEFAULT_EXCHANGE)
        update_symbols, skipped = _resolve_symbols(market_client, symbols)
        ingestor = OHLCVIngestor(db_session=db, market_client=market_client)

        results: dict[str, int] = {}
        details: dict[str, dict[str, Any]] = {}
        failures: dict[str, str] = {}
        for symbol in update_symbols:
            try:
                if settings.MARKET_DATA_UPDATE_ROLLING_DAYS > 0:
                    backfill_result = ingestor.backfill_symbol(
                        symbol=symbol,
                        timeframe=settings.MARKET_DATA_UPDATE_TIMEFRAME,
                        start_at=datetime.now(UTC)
                        - timedelta(days=settings.MARKET_DATA_UPDATE_ROLLING_DAYS),
                        batch_limit=settings.MARKET_DATA_UPDATE_LIMIT,
                        max_batches=settings.MARKET_DATA_UPDATE_MAX_BATCHES_PER_SYMBOL,
                    )
                    results[symbol] = int(backfill_result["inserted"])
                    details[symbol] = backfill_result
                else:
                    results[symbol] = ingestor.ingest_symbol(
                        symbol=symbol,
                        timeframe=settings.MARKET_DATA_UPDATE_TIMEFRAME,
                        limit=settings.MARKET_DATA_UPDATE_LIMIT,
                    )
            except MarketDataError as exc:
                failures[symbol] = str(exc)
                logger.warning("Skipped scheduled market data update for %s: %s", symbol, exc)
            except Exception:
                failures[symbol] = "Unexpected market data update failure."
                logger.exception("Failed scheduled market data update for %s", symbol)

        track_feature_event("market_data_update")
        return {
            "exchange": settings.DEFAULT_EXCHANGE,
            "timeframe": settings.MARKET_DATA_UPDATE_TIMEFRAME,
            "limit": settings.MARKET_DATA_UPDATE_LIMIT,
            "symbols": update_symbols,
            "inserted": results,
            "details": details,
            "skipped": skipped,
            "failures": failures,
            "rolling_days": settings.MARKET_DATA_UPDATE_ROLLING_DAYS,
            "updated_at": datetime.now(UTC).isoformat(),
        }
    finally:
        if owns_session:
            db.close()


class MarketDataScheduler:
    def __init__(
        self,
        settings_obj=settings,
        task: Callable[[], dict[str, Any]] | None = None,
    ) -> None:
        self.settings = settings_obj
        self.task = task or update_market_data_once
        self.scheduler = BackgroundScheduler(timezone="UTC")

    def start(self) -> None:
        if not self.settings.ENABLE_MARKET_DATA_SCHEDULER:
            logger.info("Market data scheduler is disabled.")
            return
        if self.scheduler.get_job(MARKET_DATA_JOB_ID) is None:
            job_kwargs: dict[str, Any] = {}
            if self.settings.MARKET_DATA_UPDATE_ON_STARTUP:
                job_kwargs["next_run_time"] = datetime.now(UTC)
            self.scheduler.add_job(
                self.run_once,
                "interval",
                seconds=self.settings.MARKET_DATA_UPDATE_INTERVAL_SECONDS,
                id=MARKET_DATA_JOB_ID,
                replace_existing=True,
                max_instances=1,
                coalesce=True,
                **job_kwargs,
            )
        if not self.scheduler.running:
            self.scheduler.start()
            logger.info(
                "Market data scheduler started with %s second interval.",
                self.settings.MARKET_DATA_UPDATE_INTERVAL_SECONDS,
            )

    def run_once(self) -> dict[str, Any]:
        logger.info("Running scheduled market data update.")
        return self.task()

    def shutdown(self) -> None:
        if self.scheduler.running:
            self.scheduler.shutdown(wait=False)
            logger.info("Market data scheduler stopped.")


def _resolve_symbols(
    market_client: CCXTMarketClient,
    symbols: list[str] | None,
) -> tuple[list[str], list[dict[str, str]]]:
    if symbols:
        return list(dict.fromkeys(symbols)), []
    if settings.MARKET_DATA_UPDATE_USE_TOP_MARKET_CAP:
        universe = MarketUniverseService(
            exchange_id=settings.DEFAULT_EXCHANGE,
            market_client=market_client,
        ).get_top_market_symbols(top_n=settings.MARKET_DATA_UPDATE_TOP_N)
        return universe["symbols"], universe["skipped"]
    return settings.market_top_symbols_list[: settings.MARKET_DATA_UPDATE_TOP_N], []
