from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.auth.dependencies import require_auth_if_enabled
from app.db.session import get_db
from app.services.news.news_alert_service import NewsAlertService
from app.services.news.news_broadcast_service import NewsBroadcastService
from app.services.news.news_service import NewsService

router = APIRouter(tags=["news"], dependencies=[Depends(require_auth_if_enabled)])


@router.get("/latest")
def get_latest_news(
    limit: int = Query(default=50, ge=1, le=200),
    symbol: str | None = Query(default=None),
    urgency: str | None = Query(default=None),
    source: str | None = Query(default=None),
    db: Session = Depends(get_db),
) -> dict:
    return {
        "data": NewsService(db).list_latest_news(
            limit=limit,
            symbol=symbol,
            urgency=urgency,
            source=source,
        )
    }


@router.get("/briefing")
def get_news_briefing(
    briefing_type: str = Query(default="latest", alias="type"),
    db: Session = Depends(get_db),
) -> dict:
    broadcast = NewsBroadcastService(db).get_latest_broadcast(briefing_type)
    if broadcast is None:
        broadcast = {
            "id": None,
            "broadcast_type": briefing_type,
            "title": "加密市场新闻播报",
            "content_cn": "暂无已生成的新闻播报。可以等待定时任务运行，或手动触发新闻分析和播报生成。",
            "top_symbols": [],
            "top_news_ids": [],
            "overall_sentiment": "neutral",
            "created_at": None,
        }
    return {"data": broadcast}


@router.get("/alerts")
def get_news_alerts(
    limit: int = Query(default=50, ge=1, le=200),
    db: Session = Depends(get_db),
) -> dict:
    return {"data": NewsAlertService(db).list_alerts(limit=limit)}


@router.post("/refresh")
def refresh_news(db: Session = Depends(get_db)) -> dict:
    return NewsService(db).fetch_news()


@router.post("/analyze")
def analyze_news(db: Session = Depends(get_db)) -> dict:
    result = NewsService(db).analyze_unprocessed_news()
    alerts = NewsAlertService(db).create_alerts_for_recent_news()
    result["alerts_created"] = len(alerts)
    return result


@router.get("/sources")
def get_news_sources(db: Session = Depends(get_db)) -> dict:
    return NewsService(db).get_sources_status()
