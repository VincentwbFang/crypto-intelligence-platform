from __future__ import annotations

import logging
from datetime import UTC, datetime

import httpx

from app.services.news.sources.base import NewsSource, NewsSourceItem

logger = logging.getLogger(__name__)


class CryptoPanicSource(NewsSource):
    source_type = "cryptopanic"

    def __init__(self, api_key: str | None, timeout_seconds: float = 10.0) -> None:
        self.api_key = api_key
        self.timeout_seconds = timeout_seconds

    @property
    def enabled(self) -> bool:
        return bool(self.api_key)

    def fetch(self, limit: int) -> list[NewsSourceItem]:
        if not self.enabled:
            return []
        params = {
            "auth_token": self.api_key,
            "public": "true",
            "kind": "news",
            "currencies": "BTC,ETH,SOL,XRP,BNB,DOGE,ADA,AVAX,LINK,TON,TRX,SUI,HYPE",
        }
        try:
            response = httpx.get(
                "https://cryptopanic.com/api/v1/posts/",
                params=params,
                timeout=self.timeout_seconds,
            )
            response.raise_for_status()
            payload = response.json()
        except Exception as exc:
            logger.warning("CryptoPanic source failed: %s", exc)
            return []

        items: list[NewsSourceItem] = []
        for post in payload.get("results", [])[:limit]:
            title = post.get("title")
            url = post.get("url")
            if not title or not url:
                continue
            currencies = post.get("currencies") or []
            items.append(
                {
                    "title": str(title),
                    "url": str(url),
                    "source": str((post.get("source") or {}).get("title") or "CryptoPanic"),
                    "published_at": _parse_iso(post.get("published_at")),
                    "summary_raw": None,
                    "content_raw": None,
                    "language": None,
                    "symbols_hint": [
                        str(currency.get("code"))
                        for currency in currencies
                        if currency.get("code")
                    ],
                    "source_type": self.source_type,
                }
            )
        return items


def _parse_iso(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(UTC)
    except ValueError:
        return None
