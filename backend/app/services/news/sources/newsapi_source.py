from __future__ import annotations

import logging
from datetime import UTC, datetime

import httpx

from app.services.news.sources.base import NewsSource, NewsSourceItem

logger = logging.getLogger(__name__)


class NewsAPISource(NewsSource):
    source_type = "newsapi"

    def __init__(self, api_key: str | None, query: str, timeout_seconds: float = 10.0) -> None:
        self.api_key = api_key
        self.query = query
        self.timeout_seconds = timeout_seconds

    @property
    def enabled(self) -> bool:
        return bool(self.api_key)

    def fetch(self, limit: int) -> list[NewsSourceItem]:
        if not self.enabled:
            return []
        params = {
            "q": self.query,
            "language": "en",
            "sortBy": "publishedAt",
            "pageSize": min(limit, 100),
            "apiKey": self.api_key,
        }
        try:
            response = httpx.get(
                "https://newsapi.org/v2/everything",
                params=params,
                timeout=self.timeout_seconds,
            )
            response.raise_for_status()
            payload = response.json()
        except Exception as exc:
            logger.warning("NewsAPI source failed: %s", exc)
            return []

        items: list[NewsSourceItem] = []
        for article in payload.get("articles", [])[:limit]:
            title = article.get("title")
            url = article.get("url")
            if not title or not url:
                continue
            items.append(
                {
                    "title": str(title),
                    "url": str(url),
                    "source": str((article.get("source") or {}).get("name") or "NewsAPI"),
                    "published_at": _parse_iso(article.get("publishedAt")),
                    "summary_raw": article.get("description"),
                    "content_raw": article.get("content"),
                    "language": "en",
                    "symbols_hint": [],
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
