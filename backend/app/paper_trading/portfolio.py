from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import PaperAccount, PaperEquitySnapshot, PaperOrder, PaperPosition
from app.paper_trading.account import PaperAccountManager
from app.paper_trading.positions import PaperPositionManager
from app.paper_trading.serialization import to_float, to_iso


class PaperPortfolioManager:
    def __init__(self, db_session: Session, workspace_id: str | None = None) -> None:
        self.db_session = db_session
        self.workspace_id = workspace_id
        self.account_manager = PaperAccountManager(db_session, workspace_id)
        self.position_manager = PaperPositionManager(db_session, workspace_id)

    def get_portfolio(self, account_id: str) -> dict[str, Any]:
        account = self.account_manager.get_account(account_id)
        if account is None:
            raise ValueError("Paper account not found.")
        return {
            "account": account,
            "positions": self.position_manager.list_positions(account_id, "open"),
            "open_orders": [self._order_to_dict(order) for order in self._open_orders(account_id)],
            "equity_snapshot": self._latest_snapshot(account_id),
        }

    def refresh_portfolio(self, account_id: str) -> dict[str, Any]:
        self.position_manager.update_position_prices(account_id)
        self.create_equity_snapshot(account_id)
        return self.get_portfolio(account_id)

    def create_equity_snapshot(self, account_id: str) -> dict[str, Any]:
        statement = select(PaperAccount).where(PaperAccount.account_id == account_id)
        if self.workspace_id:
            statement = statement.where(PaperAccount.workspace_id == self.workspace_id)
        account = self.db_session.scalar(statement)
        if account is None:
            raise ValueError("Paper account not found.")
        open_positions = self.db_session.scalars(
            select(PaperPosition).where(
                PaperPosition.account_id == account_id,
                PaperPosition.status == "open",
            )
        ).all()
        snapshot = PaperEquitySnapshot(
            workspace_id=account.workspace_id,
            account_id=account_id,
            timestamp=datetime.now(UTC),
            cash_balance=account.cash_balance,
            equity=account.equity,
            realized_pnl=account.realized_pnl,
            unrealized_pnl=account.unrealized_pnl,
            total_fees=account.total_fees,
            open_positions_count=len(open_positions),
        )
        self.db_session.add(snapshot)
        self.db_session.commit()
        return self._snapshot_to_dict(snapshot)

    def _latest_snapshot(self, account_id: str) -> dict[str, Any] | None:
        statement = (
            select(PaperEquitySnapshot)
            .where(PaperEquitySnapshot.account_id == account_id)
            .order_by(PaperEquitySnapshot.timestamp.desc())
            .limit(1)
        )
        if self.workspace_id:
            statement = statement.where(PaperEquitySnapshot.workspace_id == self.workspace_id)
        snapshot = self.db_session.scalars(statement).first()
        return self._snapshot_to_dict(snapshot) if snapshot else None

    def _open_orders(self, account_id: str) -> list[PaperOrder]:
        statement = select(PaperOrder).where(
            PaperOrder.account_id == account_id,
            PaperOrder.status == "pending",
        )
        if self.workspace_id:
            statement = statement.where(PaperOrder.workspace_id == self.workspace_id)
        return list(self.db_session.scalars(statement).all())

    @staticmethod
    def _snapshot_to_dict(snapshot: PaperEquitySnapshot) -> dict[str, Any]:
        return {
            "id": snapshot.id,
            "workspace_id": snapshot.workspace_id,
            "account_id": snapshot.account_id,
            "timestamp": to_iso(snapshot.timestamp),
            "cash_balance": to_float(snapshot.cash_balance),
            "equity": to_float(snapshot.equity),
            "realized_pnl": to_float(snapshot.realized_pnl),
            "unrealized_pnl": to_float(snapshot.unrealized_pnl),
            "total_fees": to_float(snapshot.total_fees),
            "open_positions_count": snapshot.open_positions_count,
            "created_at": to_iso(snapshot.created_at),
        }

    @staticmethod
    def _order_to_dict(order: PaperOrder) -> dict[str, Any]:
        return {
            "id": order.id,
            "workspace_id": order.workspace_id,
            "created_by_user_id": order.created_by_user_id,
            "order_id": order.order_id,
            "account_id": order.account_id,
            "symbol": order.symbol,
            "timeframe": order.timeframe,
            "side": order.side,
            "order_type": order.order_type,
            "quantity": to_float(order.quantity),
            "notional": to_float(order.notional),
            "requested_price": to_float(order.requested_price),
            "filled_price": to_float(order.filled_price),
            "status": order.status,
            "source": order.source,
            "signal_id": order.signal_id,
            "reason": order.reason,
            "fee": to_float(order.fee),
            "slippage": to_float(order.slippage),
            "created_at": to_iso(order.created_at),
            "filled_at": to_iso(order.filled_at),
            "cancelled_at": to_iso(order.cancelled_at),
        }
