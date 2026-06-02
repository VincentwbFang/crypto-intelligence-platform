from __future__ import annotations

from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.models import PaperTrade
from app.paper_trading.account import PaperAccountManager
from app.paper_trading.broker import PaperBroker
from app.paper_trading.execution import SimulatedExecutionEngine
from app.paper_trading.performance import PaperPerformanceCalculator
from app.paper_trading.portfolio import PaperPortfolioManager
from app.paper_trading.positions import PaperPositionManager
from app.paper_trading.risk import PaperRiskManager
from app.paper_trading.serialization import to_float, to_iso
from app.paper_trading.signal_executor import SignalPaperExecutor
from app.services.signal_service import SignalService


class PaperTradingService:
    def __init__(
        self,
        db_session: Session,
        workspace_id: str | None = None,
        user_id: str | None = None,
    ) -> None:
        self.db_session = db_session
        self.workspace_id = workspace_id
        self.user_id = user_id
        self.account_manager = PaperAccountManager(db_session, workspace_id, user_id)
        self.position_manager = PaperPositionManager(db_session, workspace_id)
        self.broker = PaperBroker(
            db_session=db_session,
            risk_manager=PaperRiskManager(settings),
            execution_engine=SimulatedExecutionEngine(db_session, settings),
            position_manager=self.position_manager,
            workspace_id=workspace_id,
            user_id=user_id,
        )
        self.portfolio_manager = PaperPortfolioManager(db_session, workspace_id)
        self.performance_calculator = PaperPerformanceCalculator(db_session, workspace_id)

    def create_account(self, request: Any) -> dict[str, Any]:
        return self.account_manager.create_account(request.name, request.initial_balance)

    def list_accounts(self, status: str | None = None) -> list[dict[str, Any]]:
        return self.account_manager.list_accounts(status)

    def get_account(self, account_id: str) -> dict[str, Any]:
        account = self.account_manager.get_account(account_id)
        if account is None:
            raise ValueError("Paper account not found.")
        return account

    def pause_account(self, account_id: str) -> dict[str, Any]:
        return self.account_manager.pause_account(account_id)

    def activate_account(self, account_id: str) -> dict[str, Any]:
        return self.account_manager.activate_account(account_id)

    def close_account(self, account_id: str) -> dict[str, Any]:
        return self.account_manager.close_account(account_id)

    def submit_order(self, request: Any) -> dict[str, Any]:
        data = request.model_dump()
        data["workspace_id"] = self.workspace_id
        data["created_by_user_id"] = self.user_id
        return self.broker.submit_order(data)

    def cancel_order(self, order_id: str) -> dict[str, Any]:
        return self.broker.cancel_order(order_id)

    def get_order(self, order_id: str) -> dict[str, Any]:
        order = self.broker.get_order(order_id)
        if order is None:
            raise ValueError("Paper order not found.")
        return order

    def list_orders(
        self,
        account_id: str,
        status: str | None = None,
        limit: int = 100,
    ) -> list[dict[str, Any]]:
        return self.broker.list_orders(account_id, status, limit)

    def list_positions(self, account_id: str, status: str | None = "open") -> list[dict[str, Any]]:
        return self.position_manager.list_positions(account_id, status)

    def list_trades(
        self,
        account_id: str,
        symbol: str | None = None,
        limit: int = 100,
    ) -> list[dict[str, Any]]:
        statement = (
            select(PaperTrade)
            .where(PaperTrade.account_id == account_id)
            .order_by(PaperTrade.created_at.desc())
            .limit(limit)
        )
        if self.workspace_id:
            statement = statement.where(PaperTrade.workspace_id == self.workspace_id)
        if symbol:
            statement = statement.where(PaperTrade.symbol == symbol)
        return [self._trade_to_dict(row) for row in self.db_session.scalars(statement).all()]

    def get_portfolio(self, account_id: str) -> dict[str, Any]:
        return self.portfolio_manager.get_portfolio(account_id)

    def refresh_portfolio(self, account_id: str) -> dict[str, Any]:
        return self.portfolio_manager.refresh_portfolio(account_id)

    def get_performance(self, account_id: str) -> dict[str, Any]:
        return self.performance_calculator.calculate_performance(account_id)

    def run_signal_paper_execution(
        self,
        account_id: str,
        symbol: str,
        timeframe: str,
        limit: int,
    ) -> dict[str, Any]:
        executor = SignalPaperExecutor(SignalService(self.db_session), self.broker, settings)
        return executor.evaluate_signal_for_paper_trade(account_id, symbol, timeframe, limit)

    @staticmethod
    def _trade_to_dict(trade: PaperTrade) -> dict[str, Any]:
        return {
            "id": trade.id,
            "workspace_id": trade.workspace_id,
            "created_by_user_id": trade.created_by_user_id,
            "trade_id": trade.trade_id,
            "account_id": trade.account_id,
            "symbol": trade.symbol,
            "side": trade.side,
            "entry_time": to_iso(trade.entry_time),
            "entry_price": to_float(trade.entry_price),
            "exit_time": to_iso(trade.exit_time),
            "exit_price": to_float(trade.exit_price),
            "quantity": to_float(trade.quantity),
            "notional": to_float(trade.notional),
            "fee": to_float(trade.fee),
            "slippage": to_float(trade.slippage),
            "realized_pnl": to_float(trade.realized_pnl),
            "realized_pnl_pct": to_float(trade.realized_pnl_pct),
            "source": trade.source,
            "strategy_name": trade.strategy_name,
            "exit_reason": trade.exit_reason,
            "created_at": to_iso(trade.created_at),
        }
