from collections.abc import AsyncGenerator, Callable
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.trustedhost import TrustedHostMiddleware

from app.api.routes_ai import router as ai_router
from app.api.routes_alerts import router as alerts_router
from app.api.routes_auth import router as auth_router
from app.api.routes_backtesting import router as backtesting_router
from app.api.routes_health import router as health_router
from app.api.routes_market import router as market_router
from app.api.routes_news import router as news_router
from app.api.routes_paper_trading import router as paper_trading_router
from app.api.routes_signals import router as signals_router
from app.api.routes_system import router as system_router
from app.api.routes_usage import router as usage_router
from app.api.routes_users import router as users_router
from app.api.routes_watchlists import router as watchlists_router
from app.api.routes_workspaces import router as workspaces_router
from app.api.market_comparison import router as market_comparison_router
from app.api.relative_strength_alerts import router as relative_strength_alerts_router
from app.alerts.deduplication import AlertDeduplicator
from app.alerts.evaluator import AlertEvaluator
from app.alerts.notification import NotificationService
from app.alerts.rules import AlertRuleEngine
from app.alerts.scheduler import AlertScheduler
from app.core.config import settings
from app.core.logging import configure_logging
from app.db.session import SessionLocal
from app.observability.health import register_exception_handlers
from app.observability.metrics import MetricsMiddleware
from app.observability.middleware import RequestIDMiddleware, RequestLoggingMiddleware
from app.observability.sentry import setup_sentry
from app.observability.tracing import setup_tracing
from app.security.headers import SecurityHeadersMiddleware
from app.security.rate_limit import RateLimitMiddleware
from app.services.signal_service import SignalService
from app.tasks.market_data_tasks import MarketDataScheduler
from app.tasks.calculate_relative_strength import RelativeStrengthScheduler
from app.tasks.news_tasks import NewsScheduler


@asynccontextmanager
async def lifespan(application: FastAPI) -> AsyncGenerator[None, None]:
    if settings.ENABLE_ALERT_SCHEDULER:
        scheduler = AlertScheduler(
            evaluator=None,
            notification_service=NotificationService(settings),
            settings=settings,
            evaluator_factory=_build_scheduler_evaluator,
        )
        scheduler.start()
        application.state.alert_scheduler = scheduler
    if settings.ENABLE_RELATIVE_STRENGTH_SCHEDULER:
        relative_strength_scheduler = RelativeStrengthScheduler(settings)
        relative_strength_scheduler.start()
        application.state.relative_strength_scheduler = relative_strength_scheduler
    if settings.ENABLE_MARKET_DATA_SCHEDULER:
        market_data_scheduler = MarketDataScheduler(settings)
        market_data_scheduler.start()
        application.state.market_data_scheduler = market_data_scheduler
    if settings.ENABLE_NEWS_SCHEDULER:
        news_scheduler = NewsScheduler(settings)
        news_scheduler.start()
        application.state.news_scheduler = news_scheduler
    try:
        yield
    finally:
        scheduler = getattr(application.state, "alert_scheduler", None)
        if scheduler is not None:
            scheduler.shutdown()
        relative_strength_scheduler = getattr(
            application.state,
            "relative_strength_scheduler",
            None,
        )
        if relative_strength_scheduler is not None:
            relative_strength_scheduler.shutdown()
        market_data_scheduler = getattr(application.state, "market_data_scheduler", None)
        if market_data_scheduler is not None:
            market_data_scheduler.shutdown()
        news_scheduler = getattr(application.state, "news_scheduler", None)
        if news_scheduler is not None:
            news_scheduler.shutdown()


def create_app() -> FastAPI:
    configure_logging(settings.LOG_LEVEL)
    setup_sentry(settings)

    application = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        debug=settings.DEBUG,
        lifespan=lifespan,
    )
    register_exception_handlers(application)
    if settings.trusted_hosts_list:
        application.add_middleware(
            TrustedHostMiddleware,
            allowed_hosts=settings.trusted_hosts_list,
        )
    application.add_middleware(SecurityHeadersMiddleware)
    application.add_middleware(MetricsMiddleware)
    application.add_middleware(RateLimitMiddleware)
    application.add_middleware(RequestLoggingMiddleware)
    application.add_middleware(RequestIDMiddleware)
    application.add_middleware(
        CORSMiddleware,
        allow_origins=settings.frontend_origins_list,
        allow_credentials=False,
        allow_methods=["GET", "POST", "PATCH", "DELETE"],
        allow_headers=["Content-Type", "Authorization", "X-Request-ID"],
    )
    setup_tracing(application, settings)
    application.include_router(health_router, prefix="/health")
    application.include_router(system_router)
    application.include_router(auth_router, prefix="/auth")
    application.include_router(users_router, prefix="/users")
    application.include_router(workspaces_router, prefix="/workspaces")
    application.include_router(watchlists_router, prefix="/watchlists")
    application.include_router(usage_router, prefix="/usage")
    application.include_router(market_router, prefix="/market")
    application.include_router(ai_router, prefix="/ai")
    application.include_router(signals_router, prefix="/signals")
    application.include_router(alerts_router, prefix="/alerts")
    application.include_router(backtesting_router, prefix="/backtests")
    application.include_router(paper_trading_router, prefix="/paper")
    application.include_router(market_comparison_router, prefix="/api/market-comparison")
    application.include_router(
        relative_strength_alerts_router,
        prefix="/api/alerts/relative-strength",
    )
    application.include_router(news_router, prefix="/api/news")
    return application


app = create_app()


def _build_scheduler_evaluator() -> tuple[AlertEvaluator, Callable[[], None]]:
    db = SessionLocal()
    evaluator = AlertEvaluator(
        signal_service=SignalService(db),
        alert_rule_engine=AlertRuleEngine(),
        alert_deduplicator=AlertDeduplicator(db),
    )
    return evaluator, db.close
