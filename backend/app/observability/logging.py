from __future__ import annotations

import contextvars
import json
import logging
import logging.config
from datetime import UTC, datetime
from typing import Any

from app.core.config import settings
from app.observability.redaction import redact_sensitive_data

request_id_var: contextvars.ContextVar[str | None] = contextvars.ContextVar(
    "request_id",
    default=None,
)


class JsonLogFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, Any] = {
            "timestamp": datetime.now(UTC).isoformat(),
            "level": record.levelname.lower(),
            "service": settings.SERVICE_NAME,
            "environment": settings.DEPLOYMENT_ENV,
            "version": settings.APP_VERSION,
            "logger": record.name,
            "message": record.getMessage(),
            "request_id": getattr(record, "request_id", None) or request_id_var.get(),
        }
        for field in (
            "user_id",
            "workspace_id",
            "path",
            "method",
            "status_code",
            "duration_ms",
        ):
            value = getattr(record, field, None)
            if value is not None:
                payload[field] = value
        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)
        return json.dumps(redact_sensitive_data(payload), separators=(",", ":"), default=str)


def build_logging_config(log_level: str) -> dict[str, Any]:
    normalized_level = log_level.upper()
    formatter_name = "json" if settings.ENABLE_JSON_LOGGING else "readable"
    return {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "json": {"()": JsonLogFormatter},
            "readable": {
                "format": "%(asctime)s %(levelname)s logger=%(name)s message=%(message)s",
            },
        },
        "filters": {
            "redact": {"()": RedactionFilter},
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "formatter": formatter_name,
                "filters": ["redact"],
            },
        },
        "root": {"handlers": ["console"], "level": normalized_level},
        "loggers": {
            "uvicorn": {"level": normalized_level},
            "uvicorn.error": {"level": normalized_level},
            "uvicorn.access": {"level": "WARNING"},
            "sqlalchemy.engine": {"level": "WARNING"},
        },
    }


class RedactionFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        if settings.LOG_REDACTION_ENABLED:
            record.msg = redact_sensitive_data(record.msg)
            if isinstance(record.args, dict):
                record.args = redact_sensitive_data(record.args)
        return True


def configure_logging(log_level: str = "INFO") -> None:
    logging.config.dictConfig(build_logging_config(log_level))

