from __future__ import annotations

import re
from datetime import UTC, datetime
from typing import Any

HIGH_IMPACT_PATTERNS = (
    "etf approval",
    "etf rejection",
    "etf delay",
    "sec lawsuit",
    "cftc lawsuit",
    "settlement",
    "exchange hack",
    "exchange outage",
    "bankruptcy",
    "stablecoin depeg",
    "reserve issue",
    "insolvency",
    "liquidation",
    "fed rate",
    "cpi",
    "pce",
    "chain exploit",
    "bridge hack",
    "tether",
    "circle",
    "regulatory",
    "spot etf flow",
    "government selling",
)

CRITICAL_PATTERNS = (
    "exchange hack",
    "protocol hack",
    "bridge hack",
    "chain hack",
    "chain exploit",
    "protocol exploit",
    "smart contract exploit",
    "bridge exploit",
    "depeg",
    "bankruptcy",
    "insolvency",
    "sec lawsuit",
    "etf rejection",
    "exchange outage",
    "reserve issue",
)

POSITIVE_TERMS = (
    "approval",
    "approved",
    "inflows",
    "partnership",
    "settlement reached",
    "wins",
    "record volume",
    "adoption",
    "launches",
)

NEGATIVE_TERMS = (
    "rejection",
    "delay",
    "lawsuit",
    "hack",
    "exploit",
    "outage",
    "bankruptcy",
    "depeg",
    "liquidation",
    "selling",
    "charges",
)

CRYPTO_TERMS = (
    "crypto",
    "bitcoin",
    "ethereum",
    "stablecoin",
    "blockchain",
    "token",
    "exchange",
    "defi",
    "etf",
)


class NewsScoringService:
    def score(self, item: dict[str, Any], entities: dict[str, Any]) -> dict[str, Any]:
        text = _normalize(
            " ".join(
                str(value or "")
                for value in (item.get("title"), item.get("summary_raw"), item.get("content_raw"))
            )
        )
        relevance_score = _clamp(
            35
            + len(entities.get("symbols") or []) * 12
            + len(entities.get("sectors") or []) * 8
            + sum(1 for term in CRYPTO_TERMS if term in text) * 5
        )
        impact_score = _impact_score(text, entities)
        sentiment_score = _sentiment_score(text)
        time_decay_score = _time_decay_score(item.get("published_at"))
        urgency_level = _urgency_level(text, impact_score)
        impact_direction = _impact_direction(sentiment_score)
        return {
            "relevance_score": relevance_score,
            "impact_score": impact_score,
            "sentiment_score": sentiment_score,
            "urgency_level": urgency_level,
            "time_decay_score": time_decay_score,
            "affected_symbols": entities.get("symbols") or [],
            "impact_direction": impact_direction,
        }


def _impact_score(text: str, entities: dict[str, Any]) -> float:
    base = 25 + len(entities.get("symbols") or []) * 8 + len(entities.get("sectors") or []) * 7
    base += sum(10 for pattern in HIGH_IMPACT_PATTERNS if pattern in text)
    base += sum(15 for pattern in CRITICAL_PATTERNS if pattern in text)
    return _clamp(base)


def _sentiment_score(text: str) -> float:
    positive = sum(1 for term in POSITIVE_TERMS if term in text)
    negative = sum(1 for term in NEGATIVE_TERMS if term in text)
    return max(-100.0, min(100.0, (positive - negative) * 22.0))


def _urgency_level(text: str, impact_score: float) -> str:
    if any(pattern in text for pattern in CRITICAL_PATTERNS) or impact_score >= 90:
        return "critical"
    if impact_score >= 75 or any(pattern in text for pattern in HIGH_IMPACT_PATTERNS):
        return "high"
    if impact_score >= 50:
        return "medium"
    return "low"


def _impact_direction(sentiment_score: float) -> str:
    if sentiment_score >= 25:
        return "bullish"
    if sentiment_score <= -25:
        return "bearish"
    if -25 < sentiment_score < 25:
        return "neutral"
    return "mixed"


def _time_decay_score(published_at: datetime | None) -> float:
    if published_at is None:
        return 50.0
    now = datetime.now(UTC)
    if published_at.tzinfo is None:
        published_at = published_at.replace(tzinfo=UTC)
    age_hours = max(0.0, (now - published_at.astimezone(UTC)).total_seconds() / 3600)
    if age_hours <= 1:
        return 100.0
    if age_hours >= 72:
        return 10.0
    return round(max(10.0, 100.0 - age_hours * 1.25), 2)


def _normalize(value: str) -> str:
    return re.sub(r"\s+", " ", value.lower()).strip()


def _clamp(value: float) -> float:
    return round(max(0.0, min(100.0, float(value))), 2)
