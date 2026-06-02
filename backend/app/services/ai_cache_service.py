from __future__ import annotations

import hashlib
import json
import time
from dataclasses import dataclass
from typing import Any


@dataclass
class _CacheEntry:
    value: dict[str, Any]
    expires_at: float


class AICacheService:
    """Tiny process-local cache for low-cost, on-demand AI explanations.

    This deliberately avoids adding infrastructure. Redis can replace this class
    later without changing the call sites.
    """

    def __init__(self, default_ttl_seconds: int = 3600) -> None:
        self.default_ttl_seconds = default_ttl_seconds
        self._cache: dict[str, _CacheEntry] = {}

    def make_cache_key(self, namespace: str, payload: dict[str, Any]) -> str:
        encoded = json.dumps(payload, sort_keys=True, default=str).encode("utf-8")
        digest = hashlib.sha256(encoded).hexdigest()
        return f"{namespace}:{digest}"

    def get(self, key: str) -> dict[str, Any] | None:
        entry = self._cache.get(key)
        if entry is None:
            return None
        if entry.expires_at <= time.time():
            self._cache.pop(key, None)
            return None
        return dict(entry.value)

    def set(
        self,
        key: str,
        value: dict[str, Any],
        ttl_seconds: int | None = None,
    ) -> dict[str, Any]:
        ttl = ttl_seconds if ttl_seconds is not None else self.default_ttl_seconds
        self._cache[key] = _CacheEntry(value=dict(value), expires_at=time.time() + ttl)
        return value

    def clear(self) -> None:
        self._cache.clear()


ai_cache_service = AICacheService()
