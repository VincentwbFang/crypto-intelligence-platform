from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app.auth.dependencies import (
    optional_current_user,
    optional_current_workspace,
    require_auth_if_enabled,
)
from app.core.config import settings
from app.db.session import get_db
from app.observability.metrics import track_feature_event
from app.observability.tracing import trace_span
from app.schemas.ai import AISignalSummaryResponse
from app.services.ai_signal_service import AISignalService
from app.services.compliance_guardrail import ComplianceGuardrail
from app.services.market_service import MarketService
from app.subscriptions.usage import UsageTrackingService

router = APIRouter(tags=["ai"], dependencies=[Depends(require_auth_if_enabled)])


@router.get(
    "/signal-summary",
    response_model=AISignalSummaryResponse,
    response_model_exclude_none=True,
)
def get_ai_signal_summary(
    symbol: str = Query(...),
    timeframe: str = Query(default=settings.DEFAULT_TIMEFRAME),
    limit: int = Query(default=settings.MARKET_DATA_LIMIT, ge=2, le=1000),
    current_user: dict | None = Depends(optional_current_user),
    workspace: dict | None = Depends(optional_current_workspace),
    db: Session = Depends(get_db),
) -> AISignalSummaryResponse | JSONResponse:
    ai_service = AISignalService(
        api_key=settings.DEEPSEEK_API_KEY,
        model=settings.deepseek_model_name,
        enabled=settings.ENABLE_AI_SIGNAL_SUMMARY,
        actionable_mode=settings.ENABLE_ACTIONABLE_SIGNAL_MODE,
        paper_trade_suggestions_enabled=settings.ENABLE_PAPER_TRADE_SUGGESTIONS,
        base_url=settings.DEEPSEEK_BASE_URL,
        api_key_name="DEEPSEEK_API_KEY",
    )

    if not ai_service.enabled or not ai_service.api_key:
        return JSONResponse(
            content=ai_service.generate_signal_summary(snapshot={}, recent_candles=[])
        )

    market_service = MarketService(db)
    recent_candles = market_service.get_ohlcv(
        symbol=symbol,
        timeframe=timeframe,
        limit=limit,
    )
    try:
        snapshot = market_service.get_latest_market_snapshot(
            symbol=symbol,
            timeframe=timeframe,
            limit=limit,
        )
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    with trace_span("ai_signal_summary"):
        signal_summary = ai_service.generate_signal_summary(
            snapshot=snapshot,
            recent_candles=recent_candles,
        )
    track_feature_event("ai")
    guardrail_result = ComplianceGuardrail.validate_ai_output(signal_summary)
    if workspace:
        UsageTrackingService(db).record_event(
            workspace["workspace_id"],
            current_user["user_id"] if current_user else None,
            "ai_explanation",
            metadata={"kind": "signal_summary", "symbol": symbol, "timeframe": timeframe},
        )

    return AISignalSummaryResponse(
        **guardrail_result["sanitized_output"]
    )
