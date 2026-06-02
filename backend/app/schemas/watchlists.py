from __future__ import annotations

from pydantic import BaseModel


class WatchlistCreateRequest(BaseModel):
    name: str


class WatchlistSymbolAddRequest(BaseModel):
    symbol: str


class WatchlistReorderRequest(BaseModel):
    symbols: list[str]


class WatchlistSymbolResponse(BaseModel):
    id: int | None = None
    symbol: str
    display_order: int
    created_at: str | None = None


class WatchlistResponse(BaseModel):
    watchlist_id: str
    workspace_id: str
    name: str
    created_by_user_id: str
    created_at: str | None = None
    updated_at: str | None = None
    symbols: list[WatchlistSymbolResponse] = []


class WatchlistListResponse(BaseModel):
    data: list[WatchlistResponse]


class WatchlistDeleteResponse(BaseModel):
    watchlist_id: str
    deleted: bool
