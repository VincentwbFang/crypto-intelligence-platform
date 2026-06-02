from __future__ import annotations

from datetime import UTC, datetime
from decimal import Decimal
from typing import Any
from uuid import uuid4

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import PaperAccount, PaperOrder, PaperPosition
from app.paper_trading.account import PaperAccountManager
from app.paper_trading.execution import SimulatedExecutionEngine
from app.paper_trading.portfolio import PaperPortfolioManager
from app.paper_trading.positions import PaperPositionManager
from app.paper_trading.risk import PaperRiskManager
from app.paper_trading.serialization import to_float, to_iso


class PaperBroker:
    def __init__(
        self,
        db_session: Session,
        risk_manager: PaperRiskManager,
        execution_engine: SimulatedExecutionEngine,
        position_manager: PaperPositionManager,
        workspace_id: str | None = None,
        user_id: str | None = None,
    ) -> None:
        self.db_session = db_session
        self.workspace_id = workspace_id
        self.user_id = user_id
        self.risk_manager = risk_manager
        self.execution_engine = execution_engine
        self.position_manager = position_manager
        self.account_manager = PaperAccountManager(db_session, workspace_id, user_id)
        self.portfolio_manager = PaperPortfolioManager(db_session, workspace_id)

    def submit_order(self, order_request: dict[str, Any]) -> dict[str, Any]:
        account = self.account_manager.get_account(order_request["account_id"])
        if account is None:
            raise ValueError("Paper account not found.")
        if account["status"] != "active":
            raise ValueError("Paper account is not active.")
        order_input = dict(order_request)
        order_input.setdefault("source", "manual")
        if order_input["side"] == "sell":
            position = self.position_manager.get_position(order_input["account_id"], order_input["symbol"])
            if position is None:
                order_input["quantity"] = 0
            else:
                latest = self.execution_engine.get_latest_price(
                    order_input["symbol"],
                    order_input["timeframe"],
                )["latest_close"]
                reference_price = float(position.get("current_price") or latest)
                order_input["quantity"] = float(order_input["notional"]) / reference_price
        positions = self.position_manager.list_positions(order_input["account_id"], "open")
        risk = self.risk_manager.validate_order(account, order_input, positions)
        if not risk["approved"]:
            rejected = self._create_order(order_input, "rejected")
            self.db_session.commit()
            response = self.to_dict(rejected)
            response["risk"] = risk
            return response

        order = self._create_order(order_input, "pending")
        fill = self.execution_engine.simulate_market_fill(order_input)
        quantity = Decimal(str(order_input.get("quantity") or Decimal(str(order.notional)) / Decimal(str(fill["filled_price"]))))
        order.quantity = quantity
        order.requested_price = Decimal(str(fill["requested_price"]))
        order.filled_price = Decimal(str(fill["filled_price"]))
        order.fee = Decimal(str(fill["fee"]))
        order.slippage = Decimal(str(fill["slippage"]))
        order.status = "filled"
        order.filled_at = self._parse_time(fill["timestamp"])
        self.db_session.flush()
        self.position_manager.apply_filled_order(account, self.to_dict(order), fill)
        self.portfolio_manager.create_equity_snapshot(order.account_id)
        result = self.get_order(order.order_id) or {}
        result["risk"] = risk
        return result

    def cancel_order(self, order_id: str) -> dict[str, Any]:
        order = self._require_order(order_id)
        if order.status != "pending":
            raise ValueError("Only pending simulated orders can be cancelled.")
        order.status = "cancelled"
        order.cancelled_at = datetime.now(UTC)
        self.db_session.commit()
        return self.to_dict(order)

    def get_order(self, order_id: str) -> dict[str, Any] | None:
        statement = select(PaperOrder).where(PaperOrder.order_id == order_id)
        if self.workspace_id:
            statement = statement.where(PaperOrder.workspace_id == self.workspace_id)
        row = self.db_session.scalar(statement)
        return self.to_dict(row) if row else None

    def list_orders(
        self,
        account_id: str,
        status: str | None = None,
        limit: int = 100,
    ) -> list[dict[str, Any]]:
        statement = (
            select(PaperOrder)
            .where(PaperOrder.account_id == account_id)
            .order_by(PaperOrder.created_at.desc())
            .limit(limit)
        )
        if self.workspace_id:
            statement = statement.where(PaperOrder.workspace_id == self.workspace_id)
        if status:
            statement = statement.where(PaperOrder.status == status)
        return [self.to_dict(row) for row in self.db_session.scalars(statement).all()]

    def _create_order(self, data: dict[str, Any], status: str) -> PaperOrder:
        order = PaperOrder(
            workspace_id=data.get("workspace_id") or self.workspace_id,
            created_by_user_id=data.get("created_by_user_id") or self.user_id,
            order_id=str(uuid4()),
            account_id=data["account_id"],
            symbol=data["symbol"],
            timeframe=data["timeframe"],
            side=data["side"],
            order_type=data["order_type"],
            quantity=Decimal(str(data["quantity"])) if data.get("quantity") else None,
            notional=Decimal(str(data["notional"])),
            status=status,
            source=data.get("source") or "manual",
            signal_id=data.get("signal_id"),
            reason=data.get("reason"),
        )
        self.db_session.add(order)
        self.db_session.flush()
        return order

    def _require_order(self, order_id: str) -> PaperOrder:
        statement = select(PaperOrder).where(PaperOrder.order_id == order_id)
        if self.workspace_id:
            statement = statement.where(PaperOrder.workspace_id == self.workspace_id)
        order = self.db_session.scalar(statement)
        if order is None:
            raise ValueError("Paper order not found.")
        return order

    @staticmethod
    def _parse_time(value: str) -> datetime:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))

    @staticmethod
    def to_dict(order: PaperOrder) -> dict[str, Any]:
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
