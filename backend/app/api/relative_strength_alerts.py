from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.auth.dependencies import require_auth_if_enabled
from app.db.session import get_db
from app.services.relative_strength_alert_service import RelativeStrengthAlertService

router = APIRouter(tags=["relative-strength-alerts"], dependencies=[Depends(require_auth_if_enabled)])


@router.get("")
def list_relative_strength_alerts(
    limit: int = Query(default=50, ge=1, le=500),
    unread_only: bool = Query(default=False),
    db: Session = Depends(get_db),
) -> dict:
    alerts = RelativeStrengthAlertService(db).list_alerts(limit=limit, unread_only=unread_only)
    return {"data": alerts}


@router.post("/{alert_id}/read")
def mark_relative_strength_alert_read(
    alert_id: int,
    db: Session = Depends(get_db),
) -> dict:
    alert = RelativeStrengthAlertService(db).mark_read(alert_id)
    if alert is None:
        raise HTTPException(status_code=404, detail="Relative strength alert not found.")
    return alert
