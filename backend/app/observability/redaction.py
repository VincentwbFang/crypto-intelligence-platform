from __future__ import annotations

from collections.abc import Mapping
from typing import Any

SENSITIVE_KEYS = (
    "authorization",
    "cookie",
    "set-cookie",
    "x-api-key",
    "openai_api_key",
    "deepseek_api_key",
    "jwt_secret_key",
    "refresh_token",
    "access_token",
    "password",
    "password_hash",
    "token",
    "secret",
    "api_key",
)

REDACTED = "[REDACTED]"


def redact_sensitive_data(data: Any) -> Any:
    if isinstance(data, Mapping):
        return {
            key: REDACTED if _is_sensitive_key(str(key)) else redact_sensitive_data(value)
            for key, value in data.items()
        }
    if isinstance(data, list):
        return [redact_sensitive_data(item) for item in data]
    if isinstance(data, tuple):
        return tuple(redact_sensitive_data(item) for item in data)
    if isinstance(data, str):
        return redact_log_message(data)
    return data


def redact_headers(headers: Mapping[str, Any]) -> dict[str, Any]:
    return {
        key: REDACTED if _is_sensitive_key(key) else value
        for key, value in headers.items()
    }


def redact_log_message(message: str) -> str:
    redacted = message
    for key in SENSITIVE_KEYS:
        redacted = _redact_assignment(redacted, key)
    return redacted


def _is_sensitive_key(key: str) -> bool:
    normalized = key.lower().replace("-", "_")
    return any(sensitive in normalized for sensitive in SENSITIVE_KEYS)


def _redact_assignment(message: str, key: str) -> str:
    lowered = message.lower()
    normalized_key = key.lower()
    index = lowered.find(normalized_key)
    if index == -1:
        return message
    separators = ("=", ":", " ")
    end = index + len(key)
    while end < len(message) and message[end] in separators:
        end += 1
    value_end = end
    while value_end < len(message) and message[value_end] not in (" ", ",", "&", "\n", "\t"):
        value_end += 1
    if value_end <= end:
        return message
    return f"{message[:end]}{REDACTED}{message[value_end:]}"

