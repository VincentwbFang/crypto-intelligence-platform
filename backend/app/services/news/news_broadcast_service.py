from __future__ import annotations

from datetime import UTC, datetime, timedelta
from typing import Any

from sqlalchemy import desc, select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.models import NewsAnalysis, NewsBroadcast, NewsItem
from app.services.deepseek_service import DeepSeekService
from app.services.news.news_service import NEWS_SYSTEM_PROMPT
from app.services.news.text_safety import sanitize_news_summary_text


class NewsBroadcastService:
    def __init__(
        self,
        db_session: Session,
        deepseek_service: DeepSeekService | None = None,
    ) -> None:
        self.db_session = db_session
        self.deepseek_service = deepseek_service or DeepSeekService(enabled=settings.NEWS_LLM_ENABLED)

    def generate_briefing(self, broadcast_type: str = "intraday") -> dict[str, Any]:
        rows = self._top_news_for_broadcast(broadcast_type)
        if not rows:
            broadcast = NewsBroadcast(
                broadcast_type=broadcast_type,
                title=_broadcast_title(broadcast_type),
                content_cn="暂无新的高影响加密市场新闻。继续观察 BTC、ETH、稳定币、交易所和监管相关变量。",
                top_symbols=[],
                top_news_ids=[],
                overall_sentiment="neutral",
            )
            self.db_session.add(broadcast)
            self.db_session.commit()
            self.db_session.refresh(broadcast)
            return _broadcast_to_dict(broadcast)

        payload_items = [
            {
                "id": item.id,
                "title": item.title,
                "source": item.source,
                "published_at": item.published_at.isoformat(),
                "summary": item.summary_raw or item.content_raw or item.title,
                "symbols": analysis.symbols or [],
                "impact_score": float(analysis.impact_score),
                "sentiment_score": float(analysis.sentiment_score),
                "urgency_level": analysis.urgency_level,
                "impact_direction": analysis.impact_direction,
            }
            for item, analysis in rows
        ]
        llm_output = self._generate_llm_broadcast(broadcast_type, payload_items)
        content_cn = sanitize_news_summary_text(llm_output.get("content_cn")) if llm_output else None
        top_symbols = _top_symbols([analysis for _, analysis in rows])
        broadcast = NewsBroadcast(
            broadcast_type=broadcast_type,
            title=(
                sanitize_news_summary_text(llm_output.get("title"))
                if llm_output
                else _broadcast_title(broadcast_type)
            ),
            content_cn=content_cn or _fallback_broadcast_content(broadcast_type, payload_items),
            top_symbols=top_symbols,
            top_news_ids=[item.id for item, _ in rows],
            overall_sentiment=_overall_sentiment([analysis for _, analysis in rows]),
        )
        self.db_session.add(broadcast)
        self.db_session.commit()
        self.db_session.refresh(broadcast)
        return _broadcast_to_dict(broadcast)

    def generate_breaking_for_latest_critical(self) -> dict[str, Any] | None:
        rows = self._top_news_for_broadcast("breaking")
        if not rows:
            return None
        return self.generate_briefing("breaking")

    def get_latest_broadcast(self, broadcast_type: str = "latest") -> dict[str, Any] | None:
        statement = select(NewsBroadcast).order_by(desc(NewsBroadcast.created_at)).limit(1)
        if broadcast_type != "latest":
            statement = statement.where(NewsBroadcast.broadcast_type == broadcast_type)
        broadcast = self.db_session.scalar(statement)
        if broadcast is None:
            return None
        return _broadcast_to_dict(broadcast)

    def _top_news_for_broadcast(self, broadcast_type: str) -> list[tuple[NewsItem, NewsAnalysis]]:
        cutoff_hours = 24 if broadcast_type == "morning" else 6
        cutoff = datetime.now(UTC) - timedelta(hours=cutoff_hours)
        statement = (
            select(NewsItem, NewsAnalysis)
            .join(NewsAnalysis, NewsAnalysis.news_item_id == NewsItem.id)
            .where(NewsItem.published_at >= cutoff)
            .order_by(desc(NewsAnalysis.impact_score), desc(NewsItem.published_at))
            .limit(settings.NEWS_LLM_MAX_ITEMS_PER_BATCH)
        )
        if broadcast_type == "breaking":
            statement = statement.where(NewsAnalysis.urgency_level == "critical")
        return list(self.db_session.execute(statement).all())

    def _generate_llm_broadcast(
        self,
        broadcast_type: str,
        payload_items: list[dict[str, Any]],
    ) -> dict[str, Any]:
        if not settings.NEWS_LLM_ENABLED:
            return {}
        output = self.deepseek_service.generate_json(
            system_prompt=NEWS_SYSTEM_PROMPT,
            payload={
                "instruction": (
                    "请基于以下新闻生成中文新闻播报 JSON。字段：title, content_cn, "
                    "top_symbols, overall_sentiment, watch_points, not_financial_advice。"
                ),
                "broadcast_type": broadcast_type,
                "items": payload_items,
            },
        )
        if not isinstance(output, dict) or "error" in output:
            return {}
        return output


def _broadcast_title(broadcast_type: str) -> str:
    return {
        "morning": "加密市场新闻早报",
        "intraday": "加密市场盘中快报",
        "breaking": "加密市场突发新闻播报",
    }.get(broadcast_type, "加密市场新闻播报")


def _fallback_broadcast_content(broadcast_type: str, items: list[dict[str, Any]]) -> str:
    lines = [f"{_broadcast_title(broadcast_type)}："]
    for item in items[:5]:
        symbols = ", ".join(item.get("symbols") or []) or "市场整体"
        lines.append(
            f"- {sanitize_news_summary_text(item['title'])}（{item['source']}）："
            f"影响方向 {item['impact_direction']}，"
            f"风险等级 {item['urgency_level']}，关联 {symbols}。"
        )
    lines.append("以上内容仅用于新闻影响分析，不构成投资建议。")
    return "\n".join(lines)


def _top_symbols(analyses: list[NewsAnalysis]) -> list[str]:
    symbols: list[str] = []
    for analysis in analyses:
        for symbol in analysis.symbols or []:
            if symbol not in symbols:
                symbols.append(symbol)
    return symbols[:8]


def _overall_sentiment(analyses: list[NewsAnalysis]) -> str:
    if not analyses:
        return "neutral"
    average = sum(float(analysis.sentiment_score) for analysis in analyses) / len(analyses)
    if average >= 20:
        return "bullish"
    if average <= -20:
        return "bearish"
    return "neutral"


def _broadcast_to_dict(broadcast: NewsBroadcast) -> dict[str, Any]:
    return {
        "id": broadcast.id,
        "broadcast_type": broadcast.broadcast_type,
        "title": broadcast.title,
        "content_cn": broadcast.content_cn,
        "top_symbols": broadcast.top_symbols or [],
        "top_news_ids": broadcast.top_news_ids or [],
        "overall_sentiment": broadcast.overall_sentiment,
        "created_at": broadcast.created_at.isoformat(),
    }
