from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_workspace
from app.db.session import get_db
from app.schemas.usage import PlanLimitsResponse, UsageSummaryResponse
from app.subscriptions.plans import get_plan_limits
from app.subscriptions.usage import UsageTrackingService

router = APIRouter(tags=["usage"])


@router.get("/summary", response_model=UsageSummaryResponse)
def get_usage_summary(
    workspace: dict = Depends(get_current_workspace),
    db: Session = Depends(get_db),
) -> UsageSummaryResponse:
    summary = UsageTrackingService(db).get_usage_summary(workspace["workspace_id"])
    return UsageSummaryResponse(
        **summary,
        plan=workspace["plan"],
        limits=get_plan_limits(workspace["plan"]),
    )


@router.get("/limits", response_model=PlanLimitsResponse)
def get_usage_limits(workspace: dict = Depends(get_current_workspace)) -> PlanLimitsResponse:
    return PlanLimitsResponse(
        workspace_id=workspace["workspace_id"],
        plan=workspace["plan"],
        limits=get_plan_limits(workspace["plan"]),
    )
