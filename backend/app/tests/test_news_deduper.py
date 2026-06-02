from datetime import UTC, datetime

from sqlalchemy.orm import Session

from app.db.models import NewsItem
from app.services.news.deduper import NewsDeduper, hash_title, title_similarity


def test_title_similarity_detects_near_duplicate() -> None:
    assert title_similarity("Bitcoin ETF approval delayed by SEC", "SEC delays Bitcoin ETF approval") > 0.5


def test_news_deduper_detects_url_duplicate(db_session: Session) -> None:
    item = _news_item(title="Bitcoin ETF decision delayed", url="https://example.com/a")
    db_session.add(item)
    db_session.commit()

    duplicate = NewsDeduper(db_session).find_duplicate(
        {
            "title": "Different headline",
            "url": "https://example.com/a",
            "source": "Example",
            "published_at": datetime.now(UTC),
        }
    )

    assert duplicate is not None
    assert duplicate.id == item.id


def test_news_deduper_increments_duplicate_count(db_session: Session) -> None:
    item = _news_item(title="Solana network outage update", url="https://example.com/b")
    db_session.add(item)
    db_session.commit()

    duplicate = NewsDeduper(db_session).record_duplicate(
        {
            "title": "Solana network outage update",
            "url": "https://example.com/other",
            "source": "Example",
            "published_at": datetime.now(UTC),
        }
    )
    db_session.commit()

    assert duplicate is not None
    assert duplicate.duplicate_count == 1


def _news_item(title: str, url: str) -> NewsItem:
    now = datetime.now(UTC)
    return NewsItem(
        title=title,
        url=url,
        source="Example",
        source_type="rss",
        published_at=now,
        published_at_estimated=False,
        fetched_at=now,
        summary_raw=None,
        content_raw=None,
        language="en",
        hash_title=hash_title(title),
        duplicate_count=0,
    )
