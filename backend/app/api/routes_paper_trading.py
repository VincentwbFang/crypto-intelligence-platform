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
from app.schemas.paper_trading import (
    AIPaperTradingExplanationResponse,
    PaperAccountCreateRequest,
    PaperAccountListResponse,
    PaperAccountResponse,
    PaperOrderCreateRequest,
    PaperOrderListResponse,
    PaperOrderResponse,
    PaperPerformanceResponse,
    PaperPortfolioResponse,
    PaperPositionListResponse,
    PaperTradeListResponse,
    SignalPaperExecutionRequest,
    SignalPaperExecutionResponse,
)
from app.services.ai_paper_trading_explanation_service import AIPaperTradingExplanationService
from app.services.paper_trading_service import PaperTradingService
from app.subscriptions.usage import UsageTrackingService

router = APIRouter(tags=["paper"], dependencies=[Depends(require_auth_if_enabled)])


def _service(
    db: Session,
    workspace: dict | None = None,
    current_user: dict | None = None,
) -> PaperTradingService:
    return PaperTradingService(
        db,
        workspace["workspace_id"] if workspace else None,
        current_user["user_id"] if current_user else None,
    )


def _handle_error(exc: ValueError) -> None:
    message = str(exc)
    status = 404 if "not found" in message.lower() else 400
    raise HTTPException(status_code=status, detail=message)


@router.post("/accounts", response_model=PaperAccountResponse)
def create_paper_account(
    request: PaperAccountCreateRequest,
    current_user: dict | None = Depends(optional_current_user),
    workspace: dict | None = Depends(optional_current_workspace),
    db: Session = Depends(get_db),
) -> PaperAccountResponse:
    try:
        return PaperAccountResponse(**_service(db, workspace, current_user).create_account(request))
    except ValueError as exc:
        _handle_error(exc)


@router.get("/accounts", response_model=PaperAccountListResponse)
def list_paper_accounts(
    status: str | None = Query(default=None),
    workspace: dict | None = Depends(optional_current_workspace),
    db: Session = Depends(get_db),
) -> PaperAccountListResponse:
    return PaperAccountListResponse(data=_service(db, workspace).list_accounts(status))


@router.get("/accounts/{account_id}", response_model=PaperAccountResponse)
def get_paper_account(
    account_id: str,
    workspace: dict | None = Depends(optional_current_workspace),
    db: Session = Depends(get_db),
) -> PaperAccountResponse:
    try:
        return PaperAccountResponse(**_service(db, workspace).get_account(account_id))
    except ValueError as exc:
        _handle_error(exc)


@router.patch("/accounts/{account_id}/pause", response_model=PaperAccountResponse)
def pause_paper_account(
    account_id: str,
    workspace: dict | None = Depends(optional_current_workspace),
    db: Session = Depends(get_db),
) -> PaperAccountResponse:
    try:
        return PaperAccountResponse(**_service(db, workspace).pause_account(account_id))
    except ValueError as exc:
        _handle_error(exc)


@router.patch("/accounts/{account_id}/activate", response_model=PaperAccountResponse)
def activate_paper_account(
    account_id: str,
    workspace: dict | None = Depends(optional_current_workspace),
    db: Session = Depends(get_db),
) -> PaperAccountResponse:
    try:
        return PaperAccountResponse(**_service(db, workspace).activate_account(account_id))
    except ValueError as exc:
        _handle_error(exc)


@router.patch("/accounts/{account_id}/close", response_model=PaperAccountResponse)
def close_paper_account(
    account_id: str,
    workspace: dict | None = Depends(optional_current_workspace),
    db: Session = Depends(get_db),
) -> PaperAccountResponse:
    try:
        return PaperAccountResponse(**_service(db, workspace).close_account(account_id))
    except ValueError as exc:
        _handle_error(exc)


@router.post("/orders", response_model=PaperOrderResponse)
def submit_paper_order(
    request: PaperOrderCreateRequest,
    current_user: dict | None = Depends(optional_current_user),
    workspace: dict | None = Depends(optional_current_workspace),
    db: Session = Depends(get_db),
) -> PaperOrderResponse:
    try:
        with trace_span("paper_order_submission"):
            result = _service(db, workspace, current_user).submit_order(request)
        track_feature_event("paper_order")
        if workspace:
            UsageTrackingService(db).record_event(
                workspace["workspace_id"],
                current_user["user_id"] if current_user else None,
                "paper_order",
                metadata={"order_id": result.get("order_id"), "status": result.get("status")},
            )
        return PaperOrderResponse(**result)
    except ValueError as exc:
        _handle_error(exc)


@router.get("/orders", response_model=PaperOrderListResponse)
def list_paper_orders(
    account_id: str = Query(...),
    status: str | None = Query(default=None),
    limit: int = Query(default=100, ge=1, le=500),
    workspace: dict | None = Depends(optional_current_workspace),
    db: Session = Depends(get_db),
) -> PaperOrderListResponse:
    return PaperOrderListResponse(data=_service(db, workspace).list_orders(account_id, status, limit))


@router.get("/orders/{order_id}", response_model=PaperOrderResponse)
def get_paper_order(
    order_id: str,
    workspace: dict | None = Depends(optional_current_workspace),
    db: Session = Depends(get_db),
) -> PaperOrderResponse:
    try:
        return PaperOrderResponse(**_service(db, workspace).get_order(order_id))
    except ValueError as exc:
        _handle_error(exc)


@router.post("/orders/{order_id}/cancel", response_model=PaperOrderResponse)
def cancel_paper_order(
    order_id: str,
    workspace: dict | None = Depends(optional_current_workspace),
    db: Session = Depends(get_db),
) -> PaperOrderResponse:
    try:
        return PaperOrderResponse(**_service(db, workspace).cancel_order(order_id))
    except ValueError as exc:
        _handle_error(exc)


@router.get("/accounts/{account_id}/positions", response_model=PaperPositionListResponse)
def list_paper_positions(
    account_id: str,
    status: str | None = Query(default="open"),
    workspace: dict | None = Depends(optional_current_workspace),
    db: Session = Depends(get_db),
) -> PaperPositionListResponse:
    return PaperPositionListResponse(data=_service(db, workspace).list_positions(account_id, status))


@router.get("/accounts/{account_id}/trades", response_model=PaperTradeListResponse)
def list_paper_trades(
    account_id: str,
    symbol: str | None = Query(default=None),
    limit: int = Query(default=100, ge=1, le=500),
    workspace: dict | None = Depends(optional_current_workspace),
    db: Session = Depends(get_db),
) -> PaperTradeListResponse:
    return PaperTradeListResponse(data=_service(db, workspace).list_trades(account_id, symbol, limit))


@router.get("/accounts/{account_id}/portfolio", response_model=PaperPortfolioResponse)
def get_paper_portfolio(
    account_id: str,
    workspace: dict | None = Depends(optional_current_workspace),
    db: Session = Depends(get_db),
) -> PaperPortfolioResponse:
    try:
        return PaperPortfolioResponse(**_service(db, workspace).get_portfolio(account_id))
    except ValueError as exc:
        _handle_error(exc)


@router.post("/accounts/{account_id}/refresh", response_model=PaperPortfolioResponse)
def refresh_paper_portfolio(
    account_id: str,
    workspace: dict | None = Depends(optional_current_workspace),
    db: Session = Depends(get_db),
) -> PaperPortfolioResponse:
    try:
        return PaperPortfolioResponse(**_service(db, workspace).refresh_portfolio(account_id))
    except ValueError as exc:
        _handle_error(exc)


@router.get("/accounts/{account_id}/performance", response_model=PaperPerformanceResponse)
def get_paper_performance(
    account_id: str,
    workspace: dict | None = Depends(optional_current_workspace),
    db: Session = Depends(get_db),
) -> PaperPerformanceResponse:
    try:
        return PaperPerformanceResponse(**_service(db, workspace).get_performance(account_id))
    except ValueError as exc:
        _handle_error(exc)


@router.post("/accounts/{account_id}/signal-execution", response_model=SignalPaperExecutionResponse)
def run_signal_paper_execution(
    account_id: str,
    request: SignalPaperExecutionRequest,
    workspace: dict | None = Depends(optional_current_workspace),
    db: Session = Depends(get_db),
) -> SignalPaperExecutionResponse:
    try:
        return SignalPaperExecutionResponse(
            **_service(db, workspace).run_signal_paper_execution(
                account_id,
                request.symbol,
                request.timeframe,
                request.limit,
            )
        )
    except ValueError as exc:
        _handle_error(exc)


def _ai_service() -> AIPaperTradingExplanationService:
    llm_client = None
    if settings.ENABLE_AI_PAPER_TRADING_EXPLANATION and settings.DEEPSEEK_API_KEY:
        llm_client = OpenAI(
            api_key=settings.DEEPSEEK_API_KEY,
            base_url=settings.DEEPSEEK_BASE_URL,
        )
    return AIPaperTradingExplanationService(
        llm_client=llm_client,
        enabled=settings.ENABLE_AI_PAPER_TRADING_EXPLANATION,
        model=settings.deepseek_model_name,
    )


@router.get("/accounts/{account_id}/explain", response_model=AIPaperTradingExplanationResponse)
def explain_paper_portfolio(
    account_id: str,
    current_user: dict | None = Depends(optional_current_user),
    workspace: dict | None = Depends(optional_current_workspace),
    db: Session = Depends(get_db),
) -> AIPaperTradingExplanationResponse:
    try:
        service = _service(db, workspace)
        with trace_span("ai_paper_portfolio_explanation"):
            explanation = _ai_service().explain_portfolio(
                service.get_portfolio(account_id),
                service.get_performance(account_id),
            )
        if workspace and explanation.get("enabled") is True:
            track_feature_event("ai")
            UsageTrackingService(db).record_event(
                workspace["workspace_id"],
                current_user["user_id"] if current_user else None,
                "ai_explanation",
                metadata={"kind": "paper_portfolio", "account_id": account_id},
            )
        return AIPaperTradingExplanationResponse(**explanation)
    except ValueError as exc:
        _handle_error(exc)


@router.get("/orders/{order_id}/explain", response_model=AIPaperTradingExplanationResponse)
def explain_paper_order(
    order_id: str,
    current_user: dict | None = Depends(optional_current_user),
    workspace: dict | None = Depends(optional_current_workspace),
    db: Session = Depends(get_db),
) -> AIPaperTradingExplanationResponse:
    try:
        with trace_span("ai_paper_order_explanation"):
            explanation = _ai_service().explain_order(_service(db, workspace).get_order(order_id))
        if workspace and explanation.get("enabled") is True:
            track_feature_event("ai")
            UsageTrackingService(db).record_event(
                workspace["workspace_id"],
                current_user["user_id"] if current_user else None,
                "ai_explanation",
                metadata={"kind": "paper_order", "order_id": order_id},
            )
        return AIPaperTradingExplanationResponse(**explanation)
    except ValueError as exc:
        _handle_error(exc)
