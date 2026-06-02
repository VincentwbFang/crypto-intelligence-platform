from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import datetime
from typing import Literal, TypedDict

SourceType = Literal["rss", "gdelt", "newsapi", "cryptopanic"]


class NewsSourceItem(TypedDict):
    title: str
    url: str
    source: str
    published_at: datetime | None
    summary_raw: str | None
    content_raw: str | None
    language: str | None
    symbols_hint: list[str]
    source_type: SourceType


class NewsSource(ABC):
    source_type: SourceType

    @abstractmethod
    def fetch(self, limit: int) -> list[NewsSourceItem]:
        """Fetch normalized news items from the source."""
