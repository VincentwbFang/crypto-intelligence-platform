from __future__ import annotations

import logging
from datetime import UTC, datetime

import httpx

from app.services.news.sources.base import NewsSource, NewsSourceItem

logger = logging.getLogger(__name__)


class GDELTNewsSource(NewsSource):
    source_type = "gdelt"

    def __init__(self, query: str, timeout_seconds: float = 10.0) -> None:
        self.query = query
        self.timeout_seconds = timeout_seconds

    def fetch(self, limit: int) -> list[NewsSourceItem]:
        params = {
            "query": self.query,
            "mode": "ArtList",
            "format": "json",
            "maxrecords": min(limit, 250),
            "sort": "HybridRel",
        }
        try:
            response = httpx.get(
                "https://api.gdeltproject.org/api/v2/doc/doc",
                params=params,
                timeout=self.timeout_seconds,
            )
            response.raise_for_status()
            payload = response.json()
        except Exception as exc:
            logger.warning("GDELT news source failed: %s", exc)
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
                    "source": str(article.get("domain") or "GDELT"),
                    "published_at": _parse_gdelt_datetime(article.get("seendate")),
                    "summary_raw": None,
                    "content_raw": None,
                    "language": article.get("language"),
                    "symbols_hint": [],
                    "source_type": self.source_type,
                }
            )
        return items


def _parse_gdelt_datetime(value: str | None) -> datetime | None:
    if not value:
        return None
    for fmt in ("%Y%m%dT%H%M%SZ", "%Y%m%d%H%M%S"):
        try:
            return datetime.strptime(value, fmt).replace(tzinfo=UTC)
        except ValueError:
            continue
    return None
