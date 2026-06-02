from __future__ import annotations

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

from app.core.config import settings


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        if not settings.ENABLE_SECURITY_HEADERS:
            return response
        response.headers.setdefault("X-Content-Type-Options", "nosniff")
        response.headers.setdefault("X-Frame-Options", "DENY")
        response.headers.setdefault("Referrer-Policy", "no-referrer")
        response.headers.setdefault(
            "Permissions-Policy",
            "camera=(), microphone=(), geolocation=(), payment=()",
        )
        if _is_auth_sensitive_path(request.url.path):
            response.headers.setdefault("Cache-Control", "no-store")
        return response


def _is_auth_sensitive_path(path: str) -> bool:
    return path.startswith(("/auth", "/users", "/workspaces", "/watchlists", "/usage"))

