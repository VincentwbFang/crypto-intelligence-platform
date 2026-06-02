from __future__ import annotations

import logging

logger = logging.getLogger(__name__)


def setup_sentry(settings) -> None:
    if not settings.ENABLE_SENTRY:
        return
    if not settings.SENTRY_DSN:
        logger.warning("Sentry is enabled but SENTRY_DSN is not configured.")
        return
    try:
        import sentry_sdk
    except Exception:
        logger.warning("sentry-sdk is unavailable; Sentry disabled.")
        return
    sentry_sdk.init(
        dsn=settings.SENTRY_DSN,
        environment=settings.SENTRY_ENVIRONMENT,
        release=settings.APP_VERSION,
        traces_sample_rate=settings.SENTRY_TRACES_SAMPLE_RATE,
        send_default_pii=False,
    )

