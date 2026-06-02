from datetime import UTC, datetime

from app.services.news.scoring import NewsScoringService
from app.services.news.text_safety import sanitize_news_summary_text


def test_news_scoring_marks_critical_risk() -> None:
    item = {
        "title": "Major exchange hack triggers stablecoin depeg concerns",
        "summary_raw": "The exploit affected liquidity and market risk appetite.",
        "content_raw": None,
        "published_at": datetime.now(UTC),
    }
    entities = {
        "symbols": ["BTC"],
        "sectors": ["EXCHANGE", "STABLECOIN"],
    }

    score = NewsScoringService().score(item, entities)

    assert score["urgency_level"] == "critical"
    assert score["impact_score"] >= 85
    assert score["sentiment_score"] < 0
    assert score["impact_direction"] == "bearish"


def test_news_scoring_does_not_mark_generic_crisis_as_critical() -> None:
    item = {
        "title": "Bitcoin faces an identity crisis as DeFi builders debate direction",
        "summary_raw": "Developers discussed product focus and market narratives.",
        "content_raw": None,
        "published_at": datetime.now(UTC),
    }
    entities = {
        "symbols": ["BTC"],
        "sectors": ["DEFI"],
    }

    score = NewsScoringService().score(item, entities)

    assert score["urgency_level"] != "critical"


def test_news_summary_text_sanitizes_target_like_claims() -> None:
    text = sanitize_news_summary_text("Analyst says price target is $224K fair value.")

    assert "$224K" not in text
    assert "price target" not in text.lower()
    assert "fair value" not in text.lower()
