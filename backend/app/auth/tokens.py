from __future__ import annotations

import base64
import hashlib
import hmac
import json
import secrets
from datetime import UTC, datetime, timedelta
from typing import Any

from app.core.config import settings


def create_access_token(user_id: str, workspace_id: str | None) -> str:
    now = datetime.now(UTC)
    payload = {
        "sub": user_id,
        "workspace_id": workspace_id,
        "type": "access",
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)).timestamp()),
    }
    return _encode_jwt(payload)


def create_refresh_token() -> tuple[str, str]:
    raw_token = secrets.token_urlsafe(48)
    return raw_token, hash_refresh_token(raw_token)


def verify_access_token(token: str) -> dict[str, Any]:
    payload = _decode_jwt(token)
    if payload.get("type") != "access":
        raise ValueError("Invalid token type.")
    exp = int(payload.get("exp", 0))
    if exp < int(datetime.now(UTC).timestamp()):
        raise ValueError("Access token has expired.")
    if not payload.get("sub"):
        raise ValueError("Access token is missing subject.")
    return payload


def hash_refresh_token(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def verify_refresh_token(raw_token: str, token_hash: str) -> bool:
    return hmac.compare_digest(hash_refresh_token(raw_token), token_hash)


def _encode_jwt(payload: dict[str, Any]) -> str:
    secret = _jwt_secret()
    header = {"alg": settings.JWT_ALGORITHM, "typ": "JWT"}
    signing_input = ".".join(
        [
            _b64_json(header),
            _b64_json(payload),
        ]
    )
    signature = hmac.new(
        secret.encode("utf-8"),
        signing_input.encode("ascii"),
        hashlib.sha256,
    ).digest()
    return f"{signing_input}.{_b64(signature)}"


def _decode_jwt(token: str) -> dict[str, Any]:
    try:
        header_b64, payload_b64, signature_b64 = token.split(".", 2)
    except ValueError as exc:
        raise ValueError("Malformed access token.") from exc
    signing_input = f"{header_b64}.{payload_b64}"
    expected = hmac.new(
        _jwt_secret().encode("utf-8"),
        signing_input.encode("ascii"),
        hashlib.sha256,
    ).digest()
    actual = _unb64(signature_b64)
    if not hmac.compare_digest(actual, expected):
        raise ValueError("Invalid access token signature.")
    header = json.loads(_unb64(header_b64))
    if header.get("alg") != settings.JWT_ALGORITHM:
        raise ValueError("Unsupported access token algorithm.")
    return json.loads(_unb64(payload_b64))


def _jwt_secret() -> str:
    if settings.JWT_SECRET_KEY:
        return settings.JWT_SECRET_KEY
    raise ValueError("JWT_SECRET_KEY must be configured.")


def _b64_json(value: dict[str, Any]) -> str:
    return _b64(json.dumps(value, separators=(",", ":"), sort_keys=True).encode("utf-8"))


def _b64(value: bytes) -> str:
    return base64.urlsafe_b64encode(value).decode("ascii").rstrip("=")


def _unb64(value: str) -> bytes:
    padding = "=" * (-len(value) % 4)
    return base64.urlsafe_b64decode((value + padding).encode("ascii"))
