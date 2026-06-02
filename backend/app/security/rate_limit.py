from __future__ import annotations

import time
from collections import defaultdict, deque
from dataclasses import dataclass

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse

from app.core.config import settings


@dataclass(frozen=True)
class RateLimitRule:
    max_requests: int
    window_seconds: int


class InMemoryRateLimiter:
    def __init__(self) -> None:
        self._buckets: dict[str, deque[float]] = defaultdict(deque)

    def allow(self, key: str, rule: RateLimitRule) -> bool:
        now = time.time()
        bucket = self._buckets[key]
        while bucket and bucket[0] <= now - rule.window_seconds:
            bucket.popleft()
        if len(bucket) >= rule.max_requests:
            return False
        bucket.append(now)
        return True

    def reset(self) -> None:
        self._buckets.clear()


rate_limiter = InMemoryRateLimiter()


class RateLimitMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if not settings.ENABLE_RATE_LIMITING or _is_exempt(request.url.path):
            return await call_next(request)
        rule = _rule_for_path(request.url.path)
        client = request.client.host if request.client else "unknown"
        key = f"{client}:{_category_for_path(request.url.path)}"
        if not rate_limiter.allow(key, rule):
            return JSONResponse(
                status_code=429,
                content={
                    "error": {
                        "type": "rate_limit_exceeded",
                        "message": "Rate limit exceeded.",
                        "request_id": getattr(request.state, "request_id", None),
                        "details": [{"limit": f"{rule.max_requests}/{rule.window_seconds}s"}],
                    }
                },
                headers={"Retry-After": str(rule.window_seconds)},
            )
        return await call_next(request)


def parse_rate_limit(value: str) -> RateLimitRule:
    amount_text, _, period_text = value.strip().partition("/")
    amount = int(amount_text)
    period = period_text.lower()
    if period.startswith("second"):
        seconds = 1
    elif period.startswith("minute"):
        seconds = 60
    elif period.startswith("hour"):
        seconds = 3600
    else:
        seconds = 60
    return RateLimitRule(max_requests=amount, window_seconds=seconds)


def _rule_for_path(path: str) -> RateLimitRule:
    if path.startswith("/auth"):
        return parse_rate_limit(settings.RATE_LIMIT_AUTH)
    if path.startswith("/ai") or path.endswith("/explain"):
        return parse_rate_limit(settings.RATE_LIMIT_AI)
    if path.startswith("/backtests"):
        return parse_rate_limit(settings.RATE_LIMIT_BACKTEST)
    if path == "/paper/orders":
        return parse_rate_limit(settings.RATE_LIMIT_PAPER_ORDER)
    return parse_rate_limit(settings.RATE_LIMIT_DEFAULT)


def _category_for_path(path: str) -> str:
    if path.startswith("/auth"):
        return "auth"
    if path.startswith("/ai") or path.endswith("/explain"):
        return "ai"
    if path.startswith("/backtests"):
        return "backtest"
    if path == "/paper/orders":
        return "paper_order"
    return "default"


def _is_exempt(path: str) -> bool:
    return path in {"/health", "/health/", "/system/health", "/system/live", "/metrics"}

