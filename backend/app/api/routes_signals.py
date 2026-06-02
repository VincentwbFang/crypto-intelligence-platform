from openai import OpenAI
from fastapi import APIRouter, Depends, HTTPException, Query
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
from app.schemas.signals import SignalRankResponse, SignalResponse
from app.services.ai_signal_explanation_service import AISignalExplanationService
from app.services.signal_service import SignalService
from app.subscriptions.usage import UsageTrackingService

router = APIRouter(tags=["signals"], dependencies=[Depends(require_auth_if_enabled)])


@router.get("/rank", response_model=SignalRankResponse)
def rank_symbols(
    symbols: str = Query(default=settings.DEFAULT_SYMBOLS),
    timeframe: str = Query(default=settings.DEFAULT_TIMEFRAME),
    limit: int = Query(default=settings.SIGNAL_DEFAULT_LIMIT, ge=2, le=1000),
    db: Session = Depends(get_db),
) -> SignalRankResponse:
    symbol_list = [symbol.strip() for symbol in symbols.split(",") if symbol.strip()]
    signal_service = SignalService(db)
    with trace_span("signal_generation"):
        ranked = signal_service.rank_symbols(
            symbols=symbol_list,
            timeframe=timeframe,
            limit=limit,
        )
    track_feature_event("signal_generation")
    return SignalRankResponse(symbols=symbol_list, timeframe=timeframe, data=ranked)


@router.post("/{symbol:path}/generate", response_model=SignalResponse)
def generate_and_store_signal(
    symbol: str,
    timeframe: str = Query(default=settings.DEFAULT_TIMEFRAME),
    limit: int = Query(default=settings.SIGNAL_DEFAULT_LIMIT, ge=2, le=1000),
    db: Session = Depends(get_db),
) -> SignalResponse:
    signal_service = SignalService(db)
    with trace_span("signal_generation"):
        signal = signal_service.generate_and_store_latest_signal(
            symbol=symbol,
            timeframe=timeframe,
            limit=limit,
        )
    track_feature_event("signal_generation")
    return SignalResponse(**signal)


@router.get("/{symbol:path}/latest", response_model=SignalResponse)
def get_latest_signal(
    symbol: str,
    timeframe: str = Query(default=settings.DEFAULT_TIMEFRAME),
    db: Session = Depends(get_db),
) -> SignalResponse:
    signal_service = SignalService(db)
    signal = signal_service.get_latest_signal(symbol=symbol, timeframe=timeframe)
    if signal is None:
        raise HTTPException(status_code=404, detail="No stored signal found.")
    return SignalResponse(**signal)


@router.get("/{symbol:path}", response_model=SignalResponse)
def generate_signal(
    symbol: str,
    timeframe: str = Query(default=settings.DEFAULT_TIMEFRAME),
    limit: int = Query(default=settings.SIGNAL_DEFAULT_LIMIT, ge=2, le=1000),
    include_ai_explanation: bool = Query(default=False),
    current_user: dict | None = Depends(optional_current_user),
    workspace: dict | None = Depends(optional_current_workspace),
    db: Session = Depends(get_db),
) -> SignalResponse:
    signal_service = SignalService(db)
    with trace_span("signal_generation"):
        signal = signal_service.generate_latest_signal(
            symbol=symbol,
            timeframe=timeframe,
            limit=limit,
        )
    track_feature_event("signal_generation")
    signal["ai_explanation"] = None
    if include_ai_explanation and settings.ENABLE_AI_SIGNAL_EXPLANATION:
        llm_client = None
        if settings.DEEPSEEK_API_KEY:
            llm_client = OpenAI(
                api_key=settings.DEEPSEEK_API_KEY,
                base_url=settings.DEEPSEEK_BASE_URL,
            )
        ai_service = AISignalExplanationService(
            llm_client=llm_client,
            enabled=settings.ENABLE_AI_SIGNAL_EXPLANATION,
            model=settings.deepseek_model_name,
        )
        with trace_span("ai_signal_explanation"):
            signal["ai_explanation"] = ai_service.explain_signal(signal)
        track_feature_event("ai")
        if workspace:
            UsageTrackingService(db).record_event(
                workspace["workspace_id"],
                current_user["user_id"] if current_user else None,
                "ai_explanation",
                metadata={"kind": "signal", "symbol": symbol, "timeframe": timeframe},
            )
    return SignalResponse(**signal)
