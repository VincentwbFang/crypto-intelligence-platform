from __future__ import annotations

import socket
from urllib.parse import urlparse

from fastapi import APIRouter, Depends, Response
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.session import get_db
from app.observability.metrics import metrics_registry
from app.schemas.system import (
    SystemHealthResponse,
    SystemLiveResponse,
    SystemReadyResponse,
    SystemVersionResponse,
)

router = APIRouter(tags=["system"])


@router.get("/system/health", response_model=SystemHealthResponse)
def system_health() -> SystemHealthResponse:
    return SystemHealthResponse(
        status="ok",
        service=settings.SERVICE_NAME,
        version=settings.APP_VERSION,
        environment=settings.DEPLOYMENT_ENV,
    )


@router.get("/system/live", response_model=SystemLiveResponse)
def system_live() -> SystemLiveResponse:
    return SystemLiveResponse(status="alive")


@router.get("/system/ready", response_model=SystemReadyResponse)
def system_ready(db: Session = Depends(get_db)) -> SystemReadyResponse:
    checks = {
        "database": _database_check(db),
        "redis": _redis_check(settings.REDIS_URL),
        "config": "ok" if settings.SERVICE_NAME and settings.APP_VERSION else "failed",
    }
    status = "ready" if all(value == "ok" for value in checks.values()) else "not_ready"
    return SystemReadyResponse(status=status, checks=checks)


@router.get("/system/version", response_model=SystemVersionResponse)
def system_version() -> SystemVersionResponse:
    return SystemVersionResponse(
        version=settings.APP_VERSION,
        service=settings.SERVICE_NAME,
        environment=settings.DEPLOYMENT_ENV,
    )


@router.get("/metrics")
def metrics() -> Response:
    if not settings.ENABLE_METRICS:
        return Response("metrics disabled\n", status_code=404, media_type="text/plain")
    return Response(metrics_registry.render(), media_type="text/plain; version=0.0.4")


def _database_check(db: Session) -> str:
    try:
        db.execute(text("SELECT 1"))
        return "ok"
    except Exception:
        return "failed"


def _redis_check(redis_url: str) -> str:
    if not redis_url:
        return "ok"
    parsed = urlparse(redis_url)
    host = parsed.hostname
    port = parsed.port or 6379
    if not host:
        return "failed"
    try:
        with socket.create_connection((host, port), timeout=0.25) as connection:
            connection.sendall(b"PING\r\n")
            response = connection.recv(16)
        return "ok" if response.startswith(b"+PONG") else "failed"
    except Exception:
        return "failed"
