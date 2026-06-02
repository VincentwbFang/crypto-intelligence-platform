from __future__ import annotations

from datetime import UTC, datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from openai import OpenAI
from sqlalchemy.orm import Session

from app.alerts.deduplication import AlertDeduplicator
from app.alerts.evaluator import AlertEvaluator
from app.alerts.notification import NotificationService
from app.alerts.rules import AlertRuleEngine
from app.auth.dependencies import (
    optional_current_user,
    optional_current_workspace,
    require_auth_if_enabled,
)
from app.core.config import settings
from app.db.session import get_db
from app.observability.metrics import track_feature_event
from app.observability.tracing import trace_span
from app.schemas.alerts import (
    AIAlertExplanationResponse,
    AlertEvaluateRequest,
    AlertEvaluateResponse,
    AlertListResponse,
    AlertResponse,
    AlertStatusUpdateRequest,
    NotificationResult,
    NotificationTestRequest,
)
from app.services.ai_alert_explanation_service import AIAlertExplanationService
from app.services.alert_service import AlertService
from app.services.signal_service import SignalService
from app.subscriptions.usage import UsageTrackingService

router = APIRouter(tags=["alerts"], dependencies=[Depends(require_auth_if_enabled)])


@router.post("/evaluate", response_model=AlertEvaluateResponse)
def evaluate_alerts(
    request: AlertEvaluateRequest,
    current_user: dict | None = Depends(optional_current_user),
    workspace: dict | None = Depends(optional_current_workspace),
    db: Session = Depends(get_db),
) -> AlertEvaluateResponse:
    symbols = request.symbols or settings.alert_default_symbols_list
    evaluator = _build_evaluator(db, workspace, current_user)
    with trace_span("alert_evaluation"):
        result = evaluator.evaluate_many(
            symbols=symbols,
            timeframe=request.timeframe,
            limit=request.limit,
        )
    track_feature_event("alert_evaluation")
    if request.send_notifications:
        notification_service = NotificationService(settings)
        result["notifications"] = notification_service.notify_many(result["alerts"])
    if workspace:
        UsageTrackingService(db).record_event(
            workspace["workspace_id"],
            current_user["user_id"] if current_user else None,
            "alert_evaluation",
            metadata={"symbols": symbols, "timeframe": request.timeframe},
        )
    return AlertEvaluateResponse(**result)


@router.get("", response_model=AlertListResponse)
def list_alerts(
    symbol: str | None = Query(default=None),
    timeframe: str | None = Query(default=None),
    severity: str | None = Query(default=None),
    alert_type: str | None = Query(default=None),
    status: str | None = Query(default=None),
    limit: int = Query(default=100, ge=1, le=1000),
    workspace: dict | None = Depends(optional_current_workspace),
    db: Session = Depends(get_db),
) -> AlertListResponse:
    alert_service = AlertService(db, workspace["workspace_id"] if workspace else None)
    alerts = alert_service.list_alerts(
        symbol=symbol,
        timeframe=timeframe,
        severity=severity,
        alert_type=alert_type,
        status=status,
        limit=limit,
    )
    return AlertListResponse(data=alerts)


@router.post("/test-notification", response_model=NotificationResult)
def test_notification(
    request: NotificationTestRequest,
) -> NotificationResult:
    alert = {
        "id": None,
        "symbol": "TEST/USDT",
        "timeframe": settings.ALERT_DEFAULT_TIMEFRAME,
        "timestamp": datetime.now(UTC).isoformat(),
        "alert_type": "test_notification",
        "severity": "info",
        "title": "Test alert notification",
        "message": f"Test notification requested for channel {request.channel}.",
        "status": "open",
        "source": "test",
        "signal_score": None,
        "risk_level": None,
        "setup_type": None,
        "dedup_key": "test-notification",
        "raw_payload": {},
    }
    result = NotificationService(settings).notify_alert(alert)
    return NotificationResult(**result)


@router.get("/{alert_id}", response_model=AlertResponse)
def get_alert(
    alert_id: int,
    workspace: dict | None = Depends(optional_current_workspace),
    db: Session = Depends(get_db),
) -> AlertResponse:
    alert = AlertService(db, workspace["workspace_id"] if workspace else None).get_alert(alert_id)
    if alert is None:
        raise HTTPException(status_code=404, detail="Alert not found.")
    return AlertResponse(**alert)


@router.patch("/{alert_id}/status", response_model=AlertResponse)
def update_alert_status(
    alert_id: int,
    request: AlertStatusUpdateRequest,
    workspace: dict | None = Depends(optional_current_workspace),
    db: Session = Depends(get_db),
) -> AlertResponse:
    try:
        alert = AlertService(db, workspace["workspace_id"] if workspace else None).update_alert_status(alert_id, request.status)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return AlertResponse(**alert)


@router.post("/{alert_id}/resolve", response_model=AlertResponse)
def resolve_alert(
    alert_id: int,
    workspace: dict | None = Depends(optional_current_workspace),
    db: Session = Depends(get_db),
) -> AlertResponse:
    try:
        alert = AlertService(db, workspace["workspace_id"] if workspace else None).mark_alert_resolved(alert_id)
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return AlertResponse(**alert)


@router.get("/{alert_id}/explain", response_model=AIAlertExplanationResponse)
def explain_alert(
    alert_id: int,
    current_user: dict | None = Depends(optional_current_user),
    workspace: dict | None = Depends(optional_current_workspace),
    db: Session = Depends(get_db),
) -> AIAlertExplanationResponse:
    alert = AlertService(db, workspace["workspace_id"] if workspace else None).get_alert(alert_id)
    if alert is None:
        raise HTTPException(status_code=404, detail="Alert not found.")

    llm_client = None
    if settings.ENABLE_AI_ALERT_EXPLANATION and settings.DEEPSEEK_API_KEY:
        llm_client = OpenAI(
            api_key=settings.DEEPSEEK_API_KEY,
            base_url=settings.DEEPSEEK_BASE_URL,
        )
    ai_service = AIAlertExplanationService(
        llm_client=llm_client,
        enabled=settings.ENABLE_AI_ALERT_EXPLANATION,
        model=settings.deepseek_model_name,
    )
    with trace_span("ai_alert_explanation"):
        explanation = ai_service.explain_alert(alert)
    if explanation.get("enabled") is True:
        track_feature_event("ai")
    if workspace and explanation.get("enabled") is True:
        UsageTrackingService(db).record_event(
            workspace["workspace_id"],
            current_user["user_id"] if current_user else None,
            "ai_explanation",
            metadata={"kind": "alert", "alert_id": alert_id},
        )
    return AIAlertExplanationResponse(**explanation)


def _build_evaluator(
    db: Session,
    workspace: dict | None = None,
    current_user: dict | None = None,
) -> AlertEvaluator:
    return AlertEvaluator(
        signal_service=SignalService(db),
        alert_rule_engine=AlertRuleEngine(),
        alert_deduplicator=AlertDeduplicator(db),
        workspace_id=workspace["workspace_id"] if workspace else None,
        user_id=current_user["user_id"] if current_user else None,
    )
