from __future__ import annotations

import re
from typing import Any

PRICE_LIKE_PATTERN = re.compile(
    r"[$€£]\s?\d[\d,]*(?:\.\d+)?\s?(?:k|m|b|K|M|B)?"
    r"|\b\d[\d,]*(?:\.\d+)?\s?(?:usd|usdt)\b",
    re.IGNORECASE,
)

UNSAFE_MARKET_CLAIMS = {
    "price target": "估值观点",
    "target price": "估值观点",
    "fair value": "估值观点",
    "guaranteed": "不确定",
    "risk-free": "存在风险",
    "all in": "高风险表达",
    "buy now": "直接交易指令",
    "sell now": "直接交易指令",
    "short here": "直接交易指令",
    "long here": "直接交易指令",
    "use leverage": "杠杆相关高风险表达",
}


def sanitize_news_summary_text(value: Any) -> str:
    """Keep analysis copy informational and avoid repeating target-like claims."""

    text = str(value or "")
    text = PRICE_LIKE_PATTERN.sub("具体价格数字", text)
    for phrase, replacement in UNSAFE_MARKET_CLAIMS.items():
        text = re.sub(re.escape(phrase), replacement, text, flags=re.IGNORECASE)
    return re.sub(r"\s+", " ", text).strip()


def sanitize_news_summary_payload(payload: dict[str, Any]) -> dict[str, Any]:
    sanitized = dict(payload)
    for key in ("headline_cn", "summary_cn", "why_it_matters"):
        if key in sanitized:
            sanitized[key] = sanitize_news_summary_text(sanitized[key])
    watch_points = sanitized.get("watch_points")
    if isinstance(watch_points, list):
        sanitized["watch_points"] = [sanitize_news_summary_text(point) for point in watch_points]
    sanitized["not_financial_advice"] = True
    return sanitized
