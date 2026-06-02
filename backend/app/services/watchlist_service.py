from __future__ import annotations

from typing import Any
from uuid import uuid4

from sqlalchemy import delete, func, select
from sqlalchemy.orm import Session

from app.db.models import Watchlist, WatchlistSymbol
from app.subscriptions.feature_gates import FeatureGateService
from app.subscriptions.plans import get_plan_limits
from app.subscriptions.usage import UsageTrackingService


class WatchlistService:
    def __init__(self, db_session: Session) -> None:
        self.db_session = db_session
        self.feature_gates = FeatureGateService(db_session)
        self.usage = UsageTrackingService(db_session)

    def create_watchlist(self, workspace_id: str, user_id: str, name: str) -> dict[str, Any]:
        watchlist = Watchlist(
            watchlist_id=str(uuid4()),
            workspace_id=workspace_id,
            name=name.strip(),
            created_by_user_id=user_id,
        )
        self.db_session.add(watchlist)
        self.db_session.commit()
        self.db_session.refresh(watchlist)
        return self._watchlist_to_dict(watchlist)

    def create_default_watchlist(self, workspace_id: str, user_id: str) -> dict[str, Any]:
        watchlist = self.create_watchlist(workspace_id, user_id, "Default Watchlist")
        for index, symbol in enumerate(("BTC/USDT", "ETH/USDT", "SOL/USDT")):
            self.db_session.add(
                WatchlistSymbol(
                    watchlist_id=watchlist["watchlist_id"],
                    symbol=symbol,
                    display_order=index,
                )
            )
        self.db_session.commit()
        return self.get_watchlist(workspace_id, watchlist["watchlist_id"])

    def list_watchlists(self, workspace_id: str) -> list[dict[str, Any]]:
        statement = (
            select(Watchlist)
            .where(Watchlist.workspace_id == workspace_id)
            .order_by(Watchlist.created_at.asc())
        )
        return [self._watchlist_to_dict(row, include_symbols=True) for row in self.db_session.scalars(statement)]

    def get_watchlist(self, workspace_id: str, watchlist_id: str) -> dict[str, Any]:
        watchlist = self._require_watchlist(workspace_id, watchlist_id)
        return self._watchlist_to_dict(watchlist, include_symbols=True)

    def add_symbol(self, workspace_id: str, watchlist_id: str, symbol: str, user_id: str | None = None) -> dict[str, Any]:
        watchlist = self._require_watchlist(workspace_id, watchlist_id)
        normalized = symbol.upper().strip()
        existing = self.db_session.scalar(
            select(WatchlistSymbol).where(
                WatchlistSymbol.watchlist_id == watchlist_id,
                WatchlistSymbol.symbol == normalized,
            )
        )
        if existing is None:
            self._enforce_symbol_limit(workspace_id)
            next_order = self._symbol_count(watchlist_id)
            self.db_session.add(
                WatchlistSymbol(
                    watchlist_id=watchlist.watchlist_id,
                    symbol=normalized,
                    display_order=next_order,
                )
            )
            self.db_session.commit()
            self.usage.record_event(
                workspace_id,
                user_id,
                "watchlist_symbol_added",
                metadata={"symbol": normalized, "watchlist_id": watchlist_id},
            )
        return self.get_watchlist(workspace_id, watchlist_id)

    def remove_symbol(self, workspace_id: str, watchlist_id: str, symbol: str) -> dict[str, Any]:
        self._require_watchlist(workspace_id, watchlist_id)
        self.db_session.execute(
            delete(WatchlistSymbol).where(
                WatchlistSymbol.watchlist_id == watchlist_id,
                WatchlistSymbol.symbol == symbol.upper().strip(),
            )
        )
        self.db_session.commit()
        return self.get_watchlist(workspace_id, watchlist_id)

    def reorder_symbols(self, workspace_id: str, watchlist_id: str, symbols: list[str]) -> dict[str, Any]:
        self._require_watchlist(workspace_id, watchlist_id)
        normalized_order = [symbol.upper().strip() for symbol in symbols]
        rows = self.db_session.scalars(
            select(WatchlistSymbol).where(WatchlistSymbol.watchlist_id == watchlist_id)
        ).all()
        order_map = {symbol: index for index, symbol in enumerate(normalized_order)}
        for row in rows:
            if row.symbol in order_map:
                row.display_order = order_map[row.symbol]
        self.db_session.commit()
        return self.get_watchlist(workspace_id, watchlist_id)

    def delete_watchlist(self, workspace_id: str, watchlist_id: str) -> bool:
        watchlist = self._require_watchlist(workspace_id, watchlist_id)
        self.db_session.execute(delete(WatchlistSymbol).where(WatchlistSymbol.watchlist_id == watchlist_id))
        self.db_session.delete(watchlist)
        self.db_session.commit()
        return True

    def _enforce_symbol_limit(self, workspace_id: str) -> None:
        plan = self.feature_gates.get_workspace_plan(workspace_id)
        limit = int(get_plan_limits(plan)["max_watchlist_symbols"])
        if self._workspace_symbol_count(workspace_id) >= limit:
            raise PermissionError("Your current plan has reached the watchlist symbol limit.")

    def _workspace_symbol_count(self, workspace_id: str) -> int:
        watchlist_ids = select(Watchlist.watchlist_id).where(Watchlist.workspace_id == workspace_id)
        return int(
            self.db_session.scalar(
                select(func.count(WatchlistSymbol.id)).where(
                    WatchlistSymbol.watchlist_id.in_(watchlist_ids)
                )
            )
            or 0
        )

    def _symbol_count(self, watchlist_id: str) -> int:
        return int(
            self.db_session.scalar(
                select(func.count(WatchlistSymbol.id)).where(
                    WatchlistSymbol.watchlist_id == watchlist_id
                )
            )
            or 0
        )

    def _require_watchlist(self, workspace_id: str, watchlist_id: str) -> Watchlist:
        watchlist = self.db_session.scalar(
            select(Watchlist).where(
                Watchlist.workspace_id == workspace_id,
                Watchlist.watchlist_id == watchlist_id,
            )
        )
        if watchlist is None:
            raise LookupError("Watchlist not found.")
        return watchlist

    def _watchlist_to_dict(self, watchlist: Watchlist, include_symbols: bool = False) -> dict[str, Any]:
        data = {
            "watchlist_id": watchlist.watchlist_id,
            "workspace_id": watchlist.workspace_id,
            "name": watchlist.name,
            "created_by_user_id": watchlist.created_by_user_id,
            "created_at": watchlist.created_at.isoformat() if watchlist.created_at else None,
            "updated_at": watchlist.updated_at.isoformat() if watchlist.updated_at else None,
            "symbols": [],
        }
        if include_symbols:
            rows = self.db_session.scalars(
                select(WatchlistSymbol)
                .where(WatchlistSymbol.watchlist_id == watchlist.watchlist_id)
                .order_by(WatchlistSymbol.display_order.asc(), WatchlistSymbol.created_at.asc())
            ).all()
            data["symbols"] = [
                {
                    "id": row.id,
                    "symbol": row.symbol,
                    "display_order": row.display_order,
                    "created_at": row.created_at.isoformat() if row.created_at else None,
                }
                for row in rows
            ]
        return data
