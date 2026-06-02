from __future__ import annotations

from datetime import UTC, datetime, timedelta
from typing import Any

from sqlalchemy import desc, exists, select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.models import NewsAlert, NewsAnalysis, NewsItem

ALERT_KEYWORDS = (
    "hack",
    "exploit",
    "depeg",
    "bankruptcy",
    "sec lawsuit",
    "etf rejection",
    "exchange outage",
)


class NewsAlertService:
    def __init__(self, db_session: Session) -> None:
        self.db_session = db_session

    def create_alerts_for_recent_news(self, limit: int = 100) -> list[dict[str, Any]]:
        if not settings.NEWS_ALERT_ENABLED:
            return []
        rows = self.db_session.execute(
            select(NewsItem, NewsAnalysis)
            .join(NewsAnalysis, NewsAnalysis.news_item_id == NewsItem.id)
            .where(~exists().where(NewsAlert.news_item_id == NewsItem.id))
            .order_by(desc(NewsItem.published_at))
            .limit(limit)
        ).all()
        created: list[dict[str, Any]] = []
        for item, analysis in rows:
            trigger = self._trigger_reason(item, analysis)
            if trigger is None:
                continue
            alert = NewsAlert(
                news_item_id=item.id,
                alert_type=trigger["alert_type"],
                severity=trigger["severity"],
                message_cn=self._format_alert_message(item, analysis),
                is_sent=False,
                sent_channels=[],
            )
            self.db_session.add(alert)
            self.db_session.flush()
            created.append(_alert_to_dict(alert, item, analysis))
        self.db_session.commit()
        return created

    def list_alerts(self, limit: int = 50) -> list[dict[str, Any]]:
        rows = self.db_session.execute(
            select(NewsAlert, NewsItem, NewsAnalysis)
            .join(NewsItem, NewsItem.id == NewsAlert.news_item_id)
            .join(NewsAnalysis, NewsAnalysis.news_item_id == NewsItem.id, isouter=True)
            .order_by(desc(NewsAlert.created_at))
            .limit(limit)
        ).all()
        return [_alert_to_dict(alert, item, analysis) for alert, item, analysis in rows]

    def _trigger_reason(self, item: NewsItem, analysis: NewsAnalysis) -> dict[str, str] | None:
        text = f"{item.title} {item.summary_raw or ''} {item.content_raw or ''}".lower()
        symbols = set(analysis.symbols or [])
        sectors = set(analysis.sectors or [])
        if analysis.urgency_level == "critical":
            return {"alert_type": "critical_news", "severity": "critical"}
        if float(analysis.impact_score) >= 85:
            return {"alert_type": "high_impact_news", "severity": "high"}
        if (
            float(analysis.sentiment_score) <= -70
            and (symbols & {"BTC", "ETH"} or sectors & {"STABLECOIN", "EXCHANGE"})
        ):
            return {"alert_type": "negative_core_market_news", "severity": "high"}
        if any(keyword in text for keyword in ALERT_KEYWORDS):
            return {"alert_type": "risk_keyword_news", "severity": "high"}
        if analysis.main_symbol and self._high_news_count(analysis.main_symbol) >= 3:
            return {"alert_type": "clustered_high_news", "severity": "medium"}
        return None

    def _high_news_count(self, symbol: str) -> int:
        cutoff = datetime.now(UTC) - timedelta(minutes=30)
        rows = self.db_session.scalars(
            select(NewsAnalysis)
            .where(
                NewsAnalysis.analyzed_at >= cutoff,
                NewsAnalysis.urgency_level.in_(("high", "critical")),
            )
            .limit(100)
        ).all()
        return sum(1 for row in rows if symbol in (row.symbols or []))

    def _format_alert_message(self, item: NewsItem, analysis: NewsAnalysis) -> str:
        summary = analysis.ai_summary_json or {}
        headline = summary.get("headline_cn") or item.title
        why = summary.get("why_it_matters") or "该新闻可能影响市场情绪、流动性或风险偏好。"
        watch_points = summary.get("watch_points") or ["观察后续确认、成交量和波动率变化。"]
        return (
            f"【突发新闻】{headline}\n"
            f"影响方向：{analysis.impact_direction}\n"
            f"影响币种：{', '.join(analysis.symbols or []) or 'N/A'}\n"
            f"风险等级：{analysis.urgency_level}\n"
            f"为什么重要：{why}\n"
            f"观察点：{'；'.join(str(point) for point in watch_points[:3])}\n"
            "备注：仅供信息分析，不构成投资建议。"
        )


def _alert_to_dict(
    alert: NewsAlert,
    item: NewsItem | None = None,
    analysis: NewsAnalysis | None = None,
) -> dict[str, Any]:
    return {
        "id": alert.id,
        "news_item_id": alert.news_item_id,
        "alert_type": alert.alert_type,
        "severity": alert.severity,
        "message_cn": alert.message_cn,
        "is_sent": alert.is_sent,
        "sent_channels": alert.sent_channels or [],
        "created_at": alert.created_at.isoformat(),
        "news": {
            "title": item.title,
            "url": item.url,
            "source": item.source,
            "published_at": item.published_at.isoformat(),
        }
        if item is not None
        else None,
        "analysis": {
            "symbols": analysis.symbols or [],
            "urgency_level": analysis.urgency_level,
            "impact_score": float(analysis.impact_score),
            "impact_direction": analysis.impact_direction,
        }
        if analysis is not None
        else None,
    }
