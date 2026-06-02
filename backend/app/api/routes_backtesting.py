from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query
from openai import OpenAI
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
from app.schemas.backtesting import (
    AIBacktestExplanationResponse,
    BacktestDeleteResponse,
    BacktestDetailResponse,
    BacktestEquityCurveResponse,
    BacktestListResponse,
    BacktestRunRequest,
    BacktestStrategiesResponse,
    BacktestTradesResponse,
)
from app.services.ai_backtest_explanation_service import AIBacktestExplanationService
from app.services.backtest_service import BacktestService
from app.subscriptions.usage import UsageTrackingService

router = APIRouter(tags=["backtests"], dependencies=[Depends(require_auth_if_enabled)])


@router.get("/strategies", response_model=BacktestStrategiesResponse)
def list_backtest_strategies(db: Session = Depends(get_db)) -> BacktestStrategiesResponse:
    return BacktestStrategiesResponse(data=BacktestService(db).list_strategies())


@router.post("/run", response_model=BacktestDetailResponse)
def run_backtest(
    request: BacktestRunRequest,
    current_user: dict | None = Depends(optional_current_user),
    workspace: dict | None = Depends(optional_current_workspace),
    db: Session = Depends(get_db),
) -> BacktestDetailResponse:
    with trace_span("backtest_run"):
        result = BacktestService(
            db,
            workspace["workspace_id"] if workspace else None,
            current_user["user_id"] if current_user else None,
        ).run_backtest(request)
    track_feature_event("backtest")
    if workspace:
        UsageTrackingService(db).record_event(
            workspace["workspace_id"],
            current_user["user_id"] if current_user else None,
            "backtest_run",
            metadata={"run_id": result.get("run_id"), "strategy_name": request.strategy_name},
        )
    return BacktestDetailResponse(**result)


@router.get("", response_model=BacktestListResponse)
def list_backtests(
    symbol: str | None = Query(default=None),
    strategy_name: str | None = Query(default=None),
    status: str | None = Query(default=None),
    limit: int = Query(default=50, ge=1, le=500),
    workspace: dict | None = Depends(optional_current_workspace),
    db: Session = Depends(get_db),
) -> BacktestListResponse:
    return BacktestListResponse(
        data=BacktestService(db, workspace["workspace_id"] if workspace else None).list_backtests(
            symbol=symbol,
            strategy_name=strategy_name,
            status=status,
            limit=limit,
        )
    )


@router.get("/{run_id}", response_model=BacktestDetailResponse)
def get_backtest(
    run_id: str,
    workspace: dict | None = Depends(optional_current_workspace),
    db: Session = Depends(get_db),
) -> BacktestDetailResponse:
    result = BacktestService(db, workspace["workspace_id"] if workspace else None).get_backtest(run_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Backtest run not found.")
    return BacktestDetailResponse(**result)


@router.get("/{run_id}/trades", response_model=BacktestTradesResponse)
def get_backtest_trades(
    run_id: str,
    workspace: dict | None = Depends(optional_current_workspace),
    db: Session = Depends(get_db),
) -> BacktestTradesResponse:
    service = BacktestService(db, workspace["workspace_id"] if workspace else None)
    if service.get_backtest(run_id) is None:
        raise HTTPException(status_code=404, detail="Backtest run not found.")
    return BacktestTradesResponse(run_id=run_id, data=service.get_trades(run_id))


@router.get("/{run_id}/equity-curve", response_model=BacktestEquityCurveResponse)
def get_backtest_equity_curve(
    run_id: str,
    workspace: dict | None = Depends(optional_current_workspace),
    db: Session = Depends(get_db),
) -> BacktestEquityCurveResponse:
    curve = BacktestService(db, workspace["workspace_id"] if workspace else None).get_equity_curve(run_id)
    if curve is None:
        raise HTTPException(status_code=404, detail="Backtest run not found.")
    return BacktestEquityCurveResponse(run_id=run_id, data=curve)


@router.get("/{run_id}/explain", response_model=AIBacktestExplanationResponse)
def explain_backtest(
    run_id: str,
    current_user: dict | None = Depends(optional_current_user),
    workspace: dict | None = Depends(optional_current_workspace),
    db: Session = Depends(get_db),
) -> AIBacktestExplanationResponse:
    result = BacktestService(db, workspace["workspace_id"] if workspace else None).get_backtest(run_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Backtest run not found.")

    llm_client = None
    if settings.ENABLE_AI_BACKTEST_EXPLANATION and settings.DEEPSEEK_API_KEY:
        llm_client = OpenAI(
            api_key=settings.DEEPSEEK_API_KEY,
            base_url=settings.DEEPSEEK_BASE_URL,
        )
    ai_service = AIBacktestExplanationService(
        llm_client=llm_client,
        enabled=settings.ENABLE_AI_BACKTEST_EXPLANATION,
        model=settings.deepseek_model_name,
    )
    with trace_span("ai_backtest_explanation"):
        explanation = ai_service.explain_backtest(result)
    if explanation.get("enabled") is True:
        track_feature_event("ai")
    if workspace and explanation.get("enabled") is True:
        UsageTrackingService(db).record_event(
            workspace["workspace_id"],
            current_user["user_id"] if current_user else None,
            "ai_explanation",
            metadata={"kind": "backtest", "run_id": run_id},
        )
    return AIBacktestExplanationResponse(**explanation)


@router.delete("/{run_id}", response_model=BacktestDeleteResponse)
def delete_backtest(
    run_id: str,
    workspace: dict | None = Depends(optional_current_workspace),
    db: Session = Depends(get_db),
) -> BacktestDeleteResponse:
    deleted = BacktestService(db, workspace["workspace_id"] if workspace else None).delete_backtest(run_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Backtest run not found.")
    return BacktestDeleteResponse(run_id=run_id, deleted=True)
