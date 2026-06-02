from collections.abc import Generator
from datetime import UTC, datetime
from decimal import Decimal

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.db.models import NewsAlert, NewsAnalysis, NewsBroadcast, NewsItem
from app.db.session import get_db
from app.main import app
from app.services.news.deduper import hash_title


@pytest.fixture()
def client(db_session: Session) -> Generator[TestClient, None, None]:
    def override_get_db() -> Generator[Session, None, None]:
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    try:
        yield TestClient(app)
    finally:
        app.dependency_overrides.clear()


def test_news_latest_api_returns_items(db_session: Session, client: TestClient) -> None:
    item = _seed_news(db_session)
    _seed_analysis(db_session, item.id)

    response = client.get("/api/news/latest", params={"limit": 10, "symbol": "BTC"})

    assert response.status_code == 200
    payload = response.json()
    assert len(payload["data"]) == 1
    assert payload["data"][0]["analysis"]["symbols"] == ["BTC"]


def test_news_briefing_api_returns_broadcast(db_session: Session, client: TestClient) -> None:
    db_session.add(
        NewsBroadcast(
            broadcast_type="intraday",
            title="加密市场盘中快报",
            content_cn="BTC 相关新闻影响市场风险偏好。",
            top_symbols=["BTC"],
            top_news_ids=[1],
            overall_sentiment="neutral",
        )
    )
    db_session.commit()

    response = client.get("/api/news/briefing", params={"type": "intraday"})

    assert response.status_code == 200
    assert response.json()["data"]["title"] == "加密市场盘中快报"


def test_news_alerts_api_returns_alerts(db_session: Session, client: TestClient) -> None:
    item = _seed_news(db_session)
    analysis = _seed_analysis(db_session, item.id)
    db_session.add(
        NewsAlert(
            news_item_id=item.id,
            alert_type="critical_news",
            severity="critical",
            message_cn="【突发新闻】测试新闻",
            is_sent=False,
            sent_channels=[],
        )
    )
    db_session.commit()

    response = client.get("/api/news/alerts")

    assert response.status_code == 200
    assert response.json()["data"][0]["analysis"]["urgency_level"] == analysis.urgency_level


def _seed_news(db_session: Session) -> NewsItem:
    now = datetime.now(UTC)
    item = NewsItem(
        title="SEC delays spot Bitcoin ETF decision",
        url=f"https://example.com/news-{now.timestamp()}",
        source="Example",
        source_type="rss",
        published_at=now,
        published_at_estimated=False,
        fetched_at=now,
        summary_raw="ETF decision delayed.",
        content_raw=None,
        language="en",
        hash_title=hash_title("SEC delays spot Bitcoin ETF decision"),
        duplicate_count=0,
    )
    db_session.add(item)
    db_session.commit()
    return item


def _seed_analysis(db_session: Session, news_item_id: int) -> NewsAnalysis:
    analysis = NewsAnalysis(
        news_item_id=news_item_id,
        symbols=["BTC"],
        sectors=["ETF", "REGULATION"],
        main_symbol="BTC",
        relevance_score=Decimal("90"),
        impact_score=Decimal("85"),
        sentiment_score=Decimal("-30"),
        urgency_level="high",
        time_decay_score=Decimal("100"),
        impact_direction="bearish",
        ai_summary_json={"headline_cn": "SEC 延迟现货 Bitcoin ETF 决定"},
        analyzed_at=datetime.now(UTC),
    )
    db_session.add(analysis)
    db_session.commit()
    return analysis
