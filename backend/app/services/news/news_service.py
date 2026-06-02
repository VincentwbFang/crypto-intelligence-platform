from __future__ import annotations

import logging
from datetime import UTC, datetime
from decimal import Decimal
from typing import Any

from sqlalchemy import desc, exists, select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.models import NewsAnalysis, NewsItem
from app.services.deepseek_service import DeepSeekService
from app.services.news.deduper import hash_title
from app.services.news.deduper import NewsDeduper
from app.services.news.entity_extractor import NewsEntityExtractor
from app.services.news.scoring import NewsScoringService
from app.services.news.sources.cryptopanic_source import CryptoPanicSource
from app.services.news.sources.gdelt_source import GDELTNewsSource
from app.services.news.sources.newsapi_source import NewsAPISource
from app.services.news.sources.rss_source import RSSNewsSource
from app.services.news.text_safety import sanitize_news_summary_payload

logger = logging.getLogger(__name__)

NEWS_SYSTEM_PROMPT = (
    "你是一个专业的加密货币新闻分析助手。你的任务是把新闻转化为简洁、客观、"
    "可执行的信息摘要。你不能给出买入、卖出、做空、加杠杆等明确交易指令。"
    "你只能分析新闻对市场情绪、流动性、监管、估值预期、风险偏好的潜在影响。"
)


class NewsService:
    def __init__(
        self,
        db_session: Session,
        deepseek_service: DeepSeekService | None = None,
    ) -> None:
        self.db_session = db_session
        self.deepseek_service = deepseek_service or DeepSeekService(enabled=settings.NEWS_LLM_ENABLED)
        self.deduper = NewsDeduper(db_session)
        self.entity_extractor = NewsEntityExtractor()
        self.scoring = NewsScoringService()

    def fetch_news(self, limit: int | None = None) -> dict[str, Any]:
        max_items = limit or settings.NEWS_MAX_ITEMS_PER_FETCH
        fetched = 0
        inserted = 0
        duplicates = 0
        errors: list[str] = []

        for source in self._enabled_sources():
            try:
                source_items = source.fetch(max_items)
            except Exception as exc:
                logger.exception("News source failed: %s", source.__class__.__name__)
                errors.append(f"{source.__class__.__name__}: {exc}")
                continue
            fetched += len(source_items)
            for item in source_items:
                try:
                    if self._insert_news_item(item):
                        inserted += 1
                    else:
                        duplicates += 1
                except Exception as exc:
                    logger.warning("Failed to persist news item %s: %s", item.get("url"), exc)
                    errors.append(str(exc))
        self.db_session.commit()
        return {"fetched": fetched, "inserted": inserted, "duplicates": duplicates, "errors": errors}

    def analyze_unprocessed_news(self, limit: int = 100) -> dict[str, Any]:
        items = self.db_session.scalars(
            select(NewsItem)
            .where(~exists().where(NewsAnalysis.news_item_id == NewsItem.id))
            .order_by(desc(NewsItem.published_at))
            .limit(limit)
        ).all()
        analyses: list[NewsAnalysis] = []
        for item in items:
            item_dict = _news_item_to_dict(item)
            entities = self.entity_extractor.extract(item_dict)
            scores = self.scoring.score(item_dict, entities)
            analysis = NewsAnalysis(
                news_item_id=item.id,
                symbols=entities["symbols"],
                sectors=entities["sectors"],
                main_symbol=entities["main_symbol"],
                relevance_score=Decimal(str(scores["relevance_score"])),
                impact_score=Decimal(str(scores["impact_score"])),
                sentiment_score=Decimal(str(scores["sentiment_score"])),
                urgency_level=scores["urgency_level"],
                time_decay_score=Decimal(str(scores["time_decay_score"])),
                impact_direction=scores["impact_direction"],
                ai_summary_json=_fallback_ai_summary(item, entities, scores),
                analyzed_at=datetime.now(UTC),
            )
            self.db_session.add(analysis)
            analyses.append(analysis)
        self.db_session.flush()

        self._generate_batch_ai_summaries(analyses)
        self.db_session.commit()
        return {"analyzed": len(analyses)}

    def list_latest_news(
        self,
        *,
        limit: int = 50,
        symbol: str | None = None,
        urgency: str | None = None,
        source: str | None = None,
    ) -> list[dict[str, Any]]:
        statement = (
            select(NewsItem, NewsAnalysis)
            .join(NewsAnalysis, NewsAnalysis.news_item_id == NewsItem.id, isouter=True)
            .order_by(desc(NewsItem.published_at))
            .limit(max(limit * 3, limit))
        )
        if source:
            statement = statement.where(NewsItem.source == source)
        rows = self.db_session.execute(statement).all()
        data = [_combine_news_analysis(item, analysis) for item, analysis in rows]
        if urgency:
            data = [item for item in data if item.get("analysis", {}).get("urgency_level") == urgency]
        if symbol and symbol.upper() != "ALL":
            normalized = symbol.upper()
            data = [
                item
                for item in data
                if normalized in (item.get("analysis", {}).get("symbols") or [])
                or normalized in (item.get("analysis", {}).get("sectors") or [])
            ]
        return data[:limit]

    def get_sources_status(self) -> dict[str, Any]:
        return {
            "rss": {"enabled": settings.RSS_NEWS_ENABLED, "feeds": settings.news_rss_feed_urls_list},
            "gdelt": {"enabled": settings.GDELT_ENABLED, "query": settings.NEWS_GDELT_QUERY},
            "newsapi": {"enabled": bool(settings.NEWSAPI_API_KEY)},
            "cryptopanic": {"enabled": bool(settings.CRYPTOPANIC_API_KEY)},
        }

    def _enabled_sources(self) -> list[Any]:
        sources: list[Any] = []
        if settings.RSS_NEWS_ENABLED:
            sources.append(RSSNewsSource(settings.news_rss_feed_urls_list))
        if settings.GDELT_ENABLED:
            sources.append(GDELTNewsSource(settings.NEWS_GDELT_QUERY))
        if settings.NEWSAPI_API_KEY:
            sources.append(NewsAPISource(settings.NEWSAPI_API_KEY, settings.NEWS_GDELT_QUERY))
        if settings.CRYPTOPANIC_API_KEY:
            sources.append(CryptoPanicSource(settings.CRYPTOPANIC_API_KEY))
        return sources

    def _insert_news_item(self, item: dict[str, Any]) -> bool:
        fetched_at = datetime.now(UTC)
        published_at = item.get("published_at") or fetched_at
        published_at_estimated = item.get("published_at") is None
        item = {**item, "published_at": published_at}
        duplicate = self.deduper.record_duplicate(item)
        if duplicate is not None:
            return False
        news_item = NewsItem(
            title=item["title"][:512],
            url=item["url"][:1024],
            source=item["source"][:128],
            source_type=item["source_type"],
            published_at=published_at,
            published_at_estimated=published_at_estimated,
            fetched_at=fetched_at,
            summary_raw=item.get("summary_raw"),
            content_raw=item.get("content_raw"),
            language=item.get("language"),
            hash_title=hash_title(item["title"]),
            duplicate_count=0,
        )
        self.db_session.add(news_item)
        self.db_session.flush()
        return True

    def _generate_batch_ai_summaries(self, analyses: list[NewsAnalysis]) -> None:
        if not settings.NEWS_LLM_ENABLED:
            return
        eligible = [
            analysis
            for analysis in analyses
            if float(analysis.impact_score) >= 70
            and analysis.urgency_level in {"high", "critical"}
        ][: settings.NEWS_LLM_MAX_ITEMS_PER_BATCH]
        if not eligible:
            return

        payload_items = []
        for analysis in eligible:
            news_item = self.db_session.get(NewsItem, analysis.news_item_id)
            if news_item is None:
                continue
            payload_items.append(
                {
                    "news_item_id": news_item.id,
                    "title": news_item.title,
                    "source": news_item.source,
                    "published_at": news_item.published_at.isoformat(),
                    "content": news_item.content_raw or news_item.summary_raw or news_item.title,
                    "symbols": analysis.symbols or [],
                    "scores": {
                        "relevance_score": float(analysis.relevance_score),
                        "impact_score": float(analysis.impact_score),
                        "sentiment_score": float(analysis.sentiment_score),
                        "urgency_level": analysis.urgency_level,
                        "impact_direction": analysis.impact_direction,
                    },
                }
            )
        if not payload_items:
            return

        output = self.deepseek_service.generate_json(
            system_prompt=NEWS_SYSTEM_PROMPT,
            payload={
                "instruction": (
                    "请批量分析以下加密货币新闻，并输出严格 JSON。返回 {items:[...]}; "
                    "每个 item 必须包含 news_item_id, headline_cn, summary_cn, why_it_matters, "
                    "affected_symbols, market_impact, risk_level, watch_points, not_financial_advice。"
                ),
                "items": payload_items,
            },
        )
        if "error" in output:
            return
        items = output.get("items") if isinstance(output, dict) else None
        if not isinstance(items, list):
            return
        by_id = {int(item["news_item_id"]): item for item in items if item.get("news_item_id")}
        for analysis in eligible:
            summary = by_id.get(analysis.news_item_id)
            if summary:
                summary["llm_generated"] = True
                analysis.ai_summary_json = sanitize_news_summary_payload(summary)


def _fallback_ai_summary(
    item: NewsItem,
    entities: dict[str, Any],
    scores: dict[str, Any],
) -> dict[str, Any]:
    symbols = entities.get("symbols") or []
    symbol_text = ", ".join(symbols or entities.get("sectors") or ["市场整体"])
    return {
        "headline_cn": f"{symbol_text} 新闻影响观察",
        "summary_cn": (
            f"该新闻来自 {item.source}，涉及 {symbol_text}。规则评分显示影响方向为"
            f"{_direction_cn(scores['impact_direction'])}，风险等级为 {scores['urgency_level']}。"
            "请结合后续确认、成交量、波动率和 BTC 联动变化观察。"
        ),
        "why_it_matters": "该新闻可能影响加密市场情绪、风险偏好或相关资产关注度。",
        "affected_symbols": symbols,
        "market_impact": _direction_cn(scores["impact_direction"]),
        "risk_level": scores["urgency_level"],
        "watch_points": [
            "观察后续官方确认和主流媒体跟进。",
            "观察相关币种成交量、波动率和 BTC 联动变化。",
        ],
        "not_financial_advice": True,
        "llm_generated": False,
    }


def _direction_cn(direction: str) -> str:
    return {
        "bullish": "利好",
        "bearish": "利空",
        "mixed": "混合",
        "neutral": "中性",
    }.get(direction, "中性")


def _news_item_to_dict(item: NewsItem) -> dict[str, Any]:
    return {
        "id": item.id,
        "title": item.title,
        "url": item.url,
        "source": item.source,
        "source_type": item.source_type,
        "published_at": item.published_at,
        "summary_raw": item.summary_raw,
        "content_raw": item.content_raw,
        "language": item.language,
        "symbols_hint": [],
    }


def _combine_news_analysis(item: NewsItem, analysis: NewsAnalysis | None) -> dict[str, Any]:
    return {
        "id": item.id,
        "title": item.title,
        "url": item.url,
        "source": item.source,
        "source_type": item.source_type,
        "published_at": item.published_at.isoformat(),
        "published_at_estimated": item.published_at_estimated,
        "summary_raw": item.summary_raw,
        "content_raw": item.content_raw,
        "language": item.language,
        "duplicate_count": item.duplicate_count,
        "analysis": _analysis_to_dict(analysis) if analysis is not None else None,
    }


def _analysis_to_dict(analysis: NewsAnalysis) -> dict[str, Any]:
    return {
        "symbols": analysis.symbols or [],
        "sectors": analysis.sectors or [],
        "main_symbol": analysis.main_symbol,
        "relevance_score": float(analysis.relevance_score),
        "impact_score": float(analysis.impact_score),
        "sentiment_score": float(analysis.sentiment_score),
        "urgency_level": analysis.urgency_level,
        "time_decay_score": float(analysis.time_decay_score),
        "impact_direction": analysis.impact_direction,
        "ai_summary_json": sanitize_news_summary_payload(analysis.ai_summary_json or {}),
        "analyzed_at": analysis.analyzed_at.isoformat(),
    }
