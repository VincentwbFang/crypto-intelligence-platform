from __future__ import annotations

from decimal import Decimal
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import PaperAccount, PaperEquitySnapshot, PaperPosition, PaperTrade


class PaperPerformanceCalculator:
    def __init__(self, db_session: Session, workspace_id: str | None = None) -> None:
        self.db_session = db_session
        self.workspace_id = workspace_id

    def calculate_performance(self, account_id: str) -> dict[str, Any]:
        account_statement = select(PaperAccount).where(PaperAccount.account_id == account_id)
        if self.workspace_id:
            account_statement = account_statement.where(PaperAccount.workspace_id == self.workspace_id)
        account = self.db_session.scalar(account_statement)
        if account is None:
            raise ValueError("Paper account not found.")
        trade_statement = select(PaperTrade).where(PaperTrade.account_id == account_id)
        snapshot_statement = (
            select(PaperEquitySnapshot)
            .where(PaperEquitySnapshot.account_id == account_id)
            .order_by(PaperEquitySnapshot.timestamp.asc())
        )
        position_statement = select(PaperPosition).where(
            PaperPosition.account_id == account_id,
            PaperPosition.status == "open",
        )
        if self.workspace_id:
            trade_statement = trade_statement.where(PaperTrade.workspace_id == self.workspace_id)
            snapshot_statement = snapshot_statement.where(
                PaperEquitySnapshot.workspace_id == self.workspace_id
            )
            position_statement = position_statement.where(
                PaperPosition.workspace_id == self.workspace_id
            )
        trades = list(
            self.db_session.scalars(trade_statement).all()
        )
        snapshots = list(
            self.db_session.scalars(snapshot_statement).all()
        )
        open_positions = list(
            self.db_session.scalars(position_statement).all()
        )
        initial = float(account.initial_balance)
        equity = float(account.equity)
        wins = [trade for trade in trades if float(trade.realized_pnl or 0) > 0]
        losses = [trade for trade in trades if float(trade.realized_pnl or 0) < 0]
        gross_profit = sum(float(trade.realized_pnl or 0) for trade in wins)
        gross_loss = abs(sum(float(trade.realized_pnl or 0) for trade in losses))
        market_value = sum(float(position.market_value) for position in open_positions)
        return {
            "initial_balance": initial,
            "current_equity": equity,
            "total_return_pct": ((equity - initial) / initial) * 100 if initial else 0.0,
            "realized_pnl": float(account.realized_pnl),
            "unrealized_pnl": float(account.unrealized_pnl),
            "total_fees": float(account.total_fees),
            "total_trades": len(trades),
            "win_rate": len(wins) / len(trades) if trades else 0.0,
            "profit_factor": gross_profit / gross_loss if gross_loss else None,
            "max_drawdown_pct": self._max_drawdown(snapshots, equity),
            "open_positions_count": len(open_positions),
            "exposure_pct": (market_value / equity) * 100 if equity else 0.0,
        }

    @staticmethod
    def _max_drawdown(snapshots: list[PaperEquitySnapshot], current_equity: float) -> float:
        values = [float(snapshot.equity) for snapshot in snapshots] or [current_equity]
        peak = values[0] if values else current_equity
        max_drawdown = 0.0
        for value in values:
            peak = max(peak, value)
            drawdown = ((value - peak) / peak) * 100 if peak else 0.0
            max_drawdown = min(max_drawdown, drawdown)
        return max_drawdown
