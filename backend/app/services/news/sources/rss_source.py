from __future__ import annotations

import logging
import re
import xml.etree.ElementTree as ET
from datetime import UTC, datetime
from email.utils import parsedate_to_datetime
from html import unescape
from typing import Any
from urllib.parse import urlparse

import httpx

from app.services.news.sources.base import NewsSource, NewsSourceItem

logger = logging.getLogger(__name__)


class RSSNewsSource(NewsSource):
    source_type = "rss"

    def __init__(self, feed_urls: list[str], timeout_seconds: float = 10.0) -> None:
        self.feed_urls = feed_urls
        self.timeout_seconds = timeout_seconds

    def fetch(self, limit: int) -> list[NewsSourceItem]:
        items: list[NewsSourceItem] = []
        for feed_url in self.feed_urls:
            if len(items) >= limit:
                break
            try:
                response = httpx.get(feed_url, timeout=self.timeout_seconds, follow_redirects=True)
                response.raise_for_status()
                items.extend(self._parse_feed(response.text, feed_url, limit - len(items)))
            except Exception as exc:
                logger.warning("RSS news source failed for %s: %s", feed_url, exc)
        return items[:limit]

    def _parse_feed(self, raw_xml: str, feed_url: str, limit: int) -> list[NewsSourceItem]:
        try:
            root = ET.fromstring(raw_xml)
        except ET.ParseError as exc:
            logger.warning("RSS feed parse failed for %s: %s", feed_url, exc)
            return []

        source = _source_from_feed(root, feed_url)
        entries = root.findall(".//item")
        if not entries:
            entries = root.findall(".//{http://www.w3.org/2005/Atom}entry")

        normalized: list[NewsSourceItem] = []
        for entry in entries[:limit]:
            title = _clean_text(_find_text(entry, "title"))
            url = _find_link(entry)
            if not title or not url:
                continue
            summary = _clean_text(
                _find_text(entry, "description")
                or _find_text(entry, "summary")
                or _find_text(entry, "{http://www.w3.org/2005/Atom}summary")
            )
            content = _clean_text(
                _find_text(entry, "{http://purl.org/rss/1.0/modules/content/}encoded")
                or _find_text(entry, "{http://www.w3.org/2005/Atom}content")
            )
            normalized.append(
                {
                    "title": title,
                    "url": url,
                    "source": source,
                    "published_at": _parse_datetime(
                        _find_text(entry, "pubDate")
                        or _find_text(entry, "published")
                        or _find_text(entry, "{http://www.w3.org/2005/Atom}published")
                        or _find_text(entry, "updated")
                        or _find_text(entry, "{http://www.w3.org/2005/Atom}updated")
                    ),
                    "summary_raw": summary,
                    "content_raw": content,
                    "language": _find_text(entry, "language"),
                    "symbols_hint": [],
                    "source_type": self.source_type,
                }
            )
        return normalized


def _find_text(element: ET.Element, tag: str) -> str | None:
    child = element.find(tag)
    if child is None and not tag.startswith("{"):
        child = element.find(f".//{{*}}{tag}")
    if child is None:
        return None
    return child.text or None


def _find_link(element: ET.Element) -> str | None:
    link = _find_text(element, "link")
    if link:
        return link.strip()
    atom_link = element.find("{http://www.w3.org/2005/Atom}link")
    if atom_link is not None:
        return atom_link.attrib.get("href")
    return None


def _source_from_feed(root: ET.Element, feed_url: str) -> str:
    title = _find_text(root, "title")
    if title:
        return _clean_text(title)[:128]
    parsed = urlparse(feed_url)
    return parsed.netloc.replace("www.", "") or "rss"


def _parse_datetime(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        parsed = parsedate_to_datetime(value)
        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=UTC)
        return parsed.astimezone(UTC)
    except Exception:
        try:
            parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
            return parsed.astimezone(UTC)
        except Exception:
            return None


def _clean_text(value: Any) -> str:
    if not value:
        return ""
    text = re.sub(r"<[^>]+>", " ", unescape(str(value)))
    return re.sub(r"\s+", " ", text).strip()
