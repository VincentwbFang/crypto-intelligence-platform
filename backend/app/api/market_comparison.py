from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.auth.dependencies import require_auth_if_enabled
from app.db.session import get_db
from app.services.relative_strength_service import RelativeStrengthService

router = APIRouter(tags=["market-comparison"], dependencies=[Depends(require_auth_if_enabled)])


@router.get("/ranking")
def get_relative_strength_ranking(
    limit: int = Query(default=100, ge=1, le=500),
    db: Session = Depends(get_db),
) -> dict:
    return {"data": RelativeStrengthService(db).get_latest_ranking(limit=limit)}


@router.get("/{symbol:path}")
def get_relative_strength_history(
    symbol: str,
    limit: int = Query(default=500, ge=1, le=2000),
    db: Session = Depends(get_db),
) -> dict:
    return {
        "symbol": symbol,
        "data": RelativeStrengthService(db).get_symbol_history(symbol=symbol, limit=limit),
    }
