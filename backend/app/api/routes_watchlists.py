from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_active_user, get_current_workspace
from app.auth.permissions import can_write_workspace
from app.db.session import get_db
from app.schemas.watchlists import (
    WatchlistCreateRequest,
    WatchlistDeleteResponse,
    WatchlistListResponse,
    WatchlistReorderRequest,
    WatchlistResponse,
    WatchlistSymbolAddRequest,
)
from app.services.watchlist_service import WatchlistService

router = APIRouter(tags=["watchlists"])


@router.get("", response_model=WatchlistListResponse)
def list_watchlists(
    workspace: dict = Depends(get_current_workspace),
    db: Session = Depends(get_db),
) -> WatchlistListResponse:
    return WatchlistListResponse(
        data=WatchlistService(db).list_watchlists(workspace["workspace_id"])
    )


@router.post("", response_model=WatchlistResponse)
def create_watchlist(
    request: WatchlistCreateRequest,
    current_user: dict = Depends(get_current_active_user),
    workspace: dict = Depends(get_current_workspace),
    db: Session = Depends(get_db),
) -> WatchlistResponse:
    _require_write(workspace)
    return WatchlistResponse(
        **WatchlistService(db).create_watchlist(
            workspace["workspace_id"],
            current_user["user_id"],
            request.name,
        )
    )


@router.get("/{watchlist_id}", response_model=WatchlistResponse)
def get_watchlist(
    watchlist_id: str,
    workspace: dict = Depends(get_current_workspace),
    db: Session = Depends(get_db),
) -> WatchlistResponse:
    try:
        return WatchlistResponse(
            **WatchlistService(db).get_watchlist(workspace["workspace_id"], watchlist_id)
        )
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.post("/{watchlist_id}/symbols", response_model=WatchlistResponse)
def add_symbol(
    watchlist_id: str,
    request: WatchlistSymbolAddRequest,
    current_user: dict = Depends(get_current_active_user),
    workspace: dict = Depends(get_current_workspace),
    db: Session = Depends(get_db),
) -> WatchlistResponse:
    _require_write(workspace)
    try:
        return WatchlistResponse(
            **WatchlistService(db).add_symbol(
                workspace["workspace_id"],
                watchlist_id,
                request.symbol,
                current_user["user_id"],
            )
        )
    except PermissionError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.delete("/{watchlist_id}/symbols/{symbol}", response_model=WatchlistResponse)
def remove_symbol(
    watchlist_id: str,
    symbol: str,
    workspace: dict = Depends(get_current_workspace),
    db: Session = Depends(get_db),
) -> WatchlistResponse:
    _require_write(workspace)
    return WatchlistResponse(
        **WatchlistService(db).remove_symbol(workspace["workspace_id"], watchlist_id, symbol)
    )


@router.patch("/{watchlist_id}/reorder", response_model=WatchlistResponse)
def reorder_symbols(
    watchlist_id: str,
    request: WatchlistReorderRequest,
    workspace: dict = Depends(get_current_workspace),
    db: Session = Depends(get_db),
) -> WatchlistResponse:
    _require_write(workspace)
    return WatchlistResponse(
        **WatchlistService(db).reorder_symbols(
            workspace["workspace_id"],
            watchlist_id,
            request.symbols,
        )
    )


@router.delete("/{watchlist_id}", response_model=WatchlistDeleteResponse)
def delete_watchlist(
    watchlist_id: str,
    workspace: dict = Depends(get_current_workspace),
    db: Session = Depends(get_db),
) -> WatchlistDeleteResponse:
    _require_write(workspace)
    WatchlistService(db).delete_watchlist(workspace["workspace_id"], watchlist_id)
    return WatchlistDeleteResponse(watchlist_id=watchlist_id, deleted=True)


def _require_write(workspace: dict) -> None:
    if not can_write_workspace(workspace.get("role")):
        raise HTTPException(status_code=403, detail="Insufficient workspace permissions.")
