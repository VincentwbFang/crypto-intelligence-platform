from __future__ import annotations

import hashlib
import re
from datetime import timedelta
from difflib import SequenceMatcher
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.models import NewsItem


def normalize_title(title: str) -> str:
    normalized = re.sub(r"[^a-z0-9\s]", " ", title.lower())
    return re.sub(r"\s+", " ", normalized).strip()


def hash_title(title: str) -> str:
    return hashlib.sha256(normalize_title(title).encode("utf-8")).hexdigest()


def title_similarity(left: str, right: str) -> float:
    return SequenceMatcher(None, normalize_title(left), normalize_title(right)).ratio()


class NewsDeduper:
    def __init__(self, db_session: Session) -> None:
        self.db_session = db_session

    def find_duplicate(self, item: dict[str, Any]) -> NewsItem | None:
        url = item.get("url")
        title = item.get("title") or ""
        if url:
            existing = self.db_session.scalar(select(NewsItem).where(NewsItem.url == url).limit(1))
            if existing is not None:
                return existing

        title_hash = hash_title(title)
        existing_title = self.db_session.scalar(
            select(NewsItem).where(NewsItem.hash_title == title_hash).limit(1)
        )
        if existing_title is not None:
            return existing_title

        published_at = item.get("published_at")
        if published_at is not None:
            cutoff = published_at - timedelta(hours=24)
            candidates = self.db_session.scalars(
                select(NewsItem)
                .where(
                    NewsItem.source == item.get("source"),
                    NewsItem.published_at >= cutoff,
                    NewsItem.published_at <= published_at + timedelta(hours=24),
                )
                .limit(200)
            ).all()
        else:
            candidates = self.db_session.scalars(select(NewsItem).limit(200)).all()

        threshold = settings.NEWS_DEDUPE_TITLE_SIMILARITY
        for candidate in candidates:
            if candidate.source == item.get("source") and normalize_title(candidate.title) == normalize_title(title):
                return candidate
            if title_similarity(candidate.title, title) >= threshold:
                return candidate
        return None

    def record_duplicate(self, item: dict[str, Any]) -> NewsItem | None:
        duplicate = self.find_duplicate(item)
        if duplicate is None:
            return None
        duplicate.duplicate_count += 1
        self.db_session.add(duplicate)
        return duplicate
