from __future__ import annotations

from datetime import UTC, datetime
from decimal import Decimal
from typing import Any
from uuid import uuid4

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import OHLCV, PaperAccount, PaperPosition, PaperTrade
from app.paper_trading.serialization import to_float, to_iso


class PaperPositionManager:
    def __init__(self, db_session: Session, workspace_id: str | None = None) -> None:
        self.db_session = db_session
        self.workspace_id = workspace_id

    def get_position(self, account_id: str, symbol: str) -> dict[str, Any] | None:
        row = self.get_position_row(account_id, symbol)
        return self.to_dict(row) if row else None

    def get_position_row(self, account_id: str, symbol: str) -> PaperPosition | None:
        statement = (
            select(PaperPosition)
            .where(
                PaperPosition.account_id == account_id,
                PaperPosition.symbol == symbol,
                PaperPosition.status == "open",
            )
            .limit(1)
        )
        if self.workspace_id:
            statement = statement.where(PaperPosition.workspace_id == self.workspace_id)
        return self.db_session.scalars(statement).first()

    def list_positions(self, account_id: str, status: str | None = "open") -> list[dict[str, Any]]:
        statement = select(PaperPosition).where(PaperPosition.account_id == account_id)
        if self.workspace_id:
            statement = statement.where(PaperPosition.workspace_id == self.workspace_id)
        if status:
            statement = statement.where(PaperPosition.status == status)
        statement = statement.order_by(PaperPosition.updated_at.desc())
        return [self.to_dict(row) for row in self.db_session.scalars(statement).all()]

    def apply_filled_order(
        self,
        account: dict[str, Any],
        order: dict[str, Any],
        fill: dict[str, Any],
    ) -> dict[str, Any]:
        account_row = self._require_account(account["account_id"])
        if order["side"] == "buy":
            position = self._apply_buy(account_row, order, fill)
        else:
            position = self._apply_sell(account_row, order, fill)
        self.db_session.flush()
        self._refresh_account_equity(account_row)
        self.db_session.commit()
        return self.to_dict(position) if position else {}

    def update_position_prices(self, account_id: str) -> list[dict[str, Any]]:
        statement = select(PaperPosition).where(
            PaperPosition.account_id == account_id,
            PaperPosition.status == "open",
        )
        if self.workspace_id:
            statement = statement.where(PaperPosition.workspace_id == self.workspace_id)
        positions = self.db_session.scalars(statement).all()
        for position in positions:
            latest = self._latest_close(position.symbol)
            if latest is None:
                continue
            self._mark_position(position, latest)
        account = self._require_account(account_id)
        self._refresh_account_equity(account)
        self.db_session.commit()
        return [self.to_dict(position) for position in positions]

    def close_position(self, account_id: str, symbol: str, reason: str) -> dict[str, Any]:
        position = self.get_position_row(account_id, symbol)
        if position is None:
            raise ValueError("Open simulated position not found.")
        latest = self._latest_close(symbol)
        if latest is None:
            raise ValueError("No stored OHLCV data is available to close the simulated position.")
        fill = {
            "filled_price": latest,
            "fee": 0.0,
            "slippage": 0.0,
            "timestamp": datetime.now(UTC).isoformat(),
        }
        order = {
            "side": "sell",
            "symbol": symbol,
            "quantity": float(position.quantity),
            "notional": float(position.quantity) * latest,
            "source": "manual",
            "strategy_name": None,
            "exit_reason": reason,
        }
        account = {"account_id": account_id}
        result = self.apply_filled_order(account, order, fill)
        return result

    def _apply_buy(
        self,
        account: PaperAccount,
        order: dict[str, Any],
        fill: dict[str, Any],
    ) -> PaperPosition:
        now = self._parse_time(fill["timestamp"])
        notional = Decimal(str(order["notional"]))
        fee = Decimal(str(fill["fee"]))
        filled_price = Decimal(str(fill["filled_price"]))
        quantity = notional / filled_price
        position = self.get_position_row(account.account_id, order["symbol"])
        if position is None:
            position = PaperPosition(
                workspace_id=account.workspace_id,
                account_id=account.account_id,
                symbol=order["symbol"],
                quantity=quantity,
                average_entry_price=filled_price,
                current_price=filled_price,
                market_value=quantity * filled_price,
                unrealized_pnl=Decimal("0"),
                unrealized_pnl_pct=Decimal("0"),
                opened_at=now,
                status="open",
            )
            self.db_session.add(position)
        else:
            existing_cost = position.quantity * position.average_entry_price
            new_cost = quantity * filled_price
            position.quantity += quantity
            position.average_entry_price = (existing_cost + new_cost) / position.quantity
            self._mark_position(position, float(filled_price))
        account.cash_balance -= notional + fee
        account.total_fees += fee
        return position

    def _apply_sell(
        self,
        account: PaperAccount,
        order: dict[str, Any],
        fill: dict[str, Any],
    ) -> PaperPosition | None:
        position = self.get_position_row(account.account_id, order["symbol"])
        if position is None:
            raise ValueError("Cannot reduce a missing simulated position.")
        quantity = Decimal(str(order["quantity"]))
        tolerance = Decimal("0.00000001")
        if quantity - position.quantity > tolerance:
            raise ValueError("Cannot reduce more than the current simulated position quantity.")
        if position.quantity - quantity <= tolerance:
            quantity = position.quantity
        filled_price = Decimal(str(fill["filled_price"]))
        fee = Decimal(str(fill["fee"]))
        proceeds = quantity * filled_price
        pnl = (filled_price - position.average_entry_price) * quantity - fee
        pnl_pct = (
            ((filled_price - position.average_entry_price) / position.average_entry_price) * Decimal("100")
            if position.average_entry_price
            else Decimal("0")
        )
        account.cash_balance += proceeds - fee
        account.realized_pnl += pnl
        account.total_fees += fee
        position.quantity -= quantity
        if position.quantity <= Decimal("0.000000000001"):
            position.status = "closed"
            position.quantity = Decimal("0")
            position.market_value = Decimal("0")
            position.unrealized_pnl = Decimal("0")
            position.unrealized_pnl_pct = Decimal("0")
        else:
            self._mark_position(position, float(filled_price))
        self.db_session.add(
            PaperTrade(
                workspace_id=account.workspace_id,
                created_by_user_id=order.get("created_by_user_id"),
                trade_id=str(uuid4()),
                account_id=account.account_id,
                symbol=position.symbol,
                side="long",
                entry_time=position.opened_at,
                entry_price=position.average_entry_price,
                exit_time=self._parse_time(fill["timestamp"]),
                exit_price=filled_price,
                quantity=quantity,
                notional=proceeds,
                fee=fee,
                slippage=Decimal(str(fill["slippage"])),
                realized_pnl=pnl,
                realized_pnl_pct=pnl_pct,
                source=order.get("source") or "manual",
                strategy_name=order.get("strategy_name"),
                exit_reason=order.get("exit_reason") or "simulated_order",
            )
        )
        return position

    def _mark_position(self, position: PaperPosition, price: float) -> None:
        current_price = Decimal(str(price))
        position.current_price = current_price
        position.market_value = position.quantity * current_price
        position.unrealized_pnl = (current_price - position.average_entry_price) * position.quantity
        position.unrealized_pnl_pct = (
            ((current_price - position.average_entry_price) / position.average_entry_price) * Decimal("100")
            if position.average_entry_price
            else Decimal("0")
        )
        position.updated_at = datetime.now(UTC)

    def _refresh_account_equity(self, account: PaperAccount) -> None:
        statement = select(PaperPosition).where(
            PaperPosition.account_id == account.account_id,
            PaperPosition.status == "open",
        )
        if self.workspace_id:
            statement = statement.where(PaperPosition.workspace_id == self.workspace_id)
        positions = self.db_session.scalars(statement).all()
        unrealized = sum((position.unrealized_pnl for position in positions), Decimal("0"))
        market_value = sum((position.market_value for position in positions), Decimal("0"))
        account.unrealized_pnl = unrealized
        account.equity = account.cash_balance + market_value
        account.updated_at = datetime.now(UTC)

    def _latest_close(self, symbol: str) -> float | None:
        row = self.db_session.scalars(
            select(OHLCV).where(OHLCV.symbol == symbol).order_by(OHLCV.timestamp.desc()).limit(1)
        ).first()
        return float(row.close) if row else None

    def _require_account(self, account_id: str) -> PaperAccount:
        statement = select(PaperAccount).where(PaperAccount.account_id == account_id)
        if self.workspace_id:
            statement = statement.where(PaperAccount.workspace_id == self.workspace_id)
        account = self.db_session.scalar(statement)
        if account is None:
            raise ValueError("Paper account not found.")
        return account

    @staticmethod
    def _parse_time(value: str) -> datetime:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))

    @staticmethod
    def to_dict(position: PaperPosition) -> dict[str, Any]:
        return {
            "id": position.id,
            "workspace_id": position.workspace_id,
            "account_id": position.account_id,
            "symbol": position.symbol,
            "quantity": to_float(position.quantity),
            "average_entry_price": to_float(position.average_entry_price),
            "current_price": to_float(position.current_price),
            "market_value": to_float(position.market_value),
            "unrealized_pnl": to_float(position.unrealized_pnl),
            "unrealized_pnl_pct": to_float(position.unrealized_pnl_pct),
            "opened_at": to_iso(position.opened_at),
            "updated_at": to_iso(position.updated_at),
            "status": position.status,
        }
