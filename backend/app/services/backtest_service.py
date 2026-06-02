from __future__ import annotations

from datetime import UTC, datetime
from decimal import Decimal
from typing import Any
from uuid import uuid4

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.backtesting.data_loader import BacktestDataLoader
from app.backtesting.engine import BacktestEngine
from app.backtesting.models import BACKTEST_DISCLAIMER
from app.backtesting.serialization import sanitize_json, to_decimal, to_iso
from app.backtesting.strategies import list_strategies
from app.core.config import settings
from app.db.models import BacktestRun, BacktestTrade
from app.schemas.backtesting import BacktestRunRequest


class BacktestService:
    def __init__(
        self,
        db_session: Session,
        workspace_id: str | None = None,
        user_id: str | None = None,
    ) -> None:
        self.db_session = db_session
        self.workspace_id = workspace_id
        self.user_id = user_id
        self.data_loader = BacktestDataLoader(db_session)
        self.engine = BacktestEngine(settings.BACKTEST_MIN_CANDLES)

    def run_backtest(self, request: BacktestRunRequest) -> dict[str, Any]:
        run_id = str(uuid4())
        now = datetime.now(UTC)
        run = BacktestRun(
            workspace_id=self.workspace_id,
            created_by_user_id=self.user_id,
            run_id=run_id,
            symbol=request.symbol,
            timeframe=request.timeframe,
            strategy_name=request.strategy_name,
            parameters=sanitize_json(request.parameters),
            initial_capital=Decimal(str(request.initial_capital)),
            status="running",
            started_at=now,
        )
        self.db_session.add(run)
        self.db_session.commit()

        try:
            df = self.data_loader.load_dataframe(
                request.symbol,
                request.timeframe,
                request.start_date,
                request.end_date,
            )
            reference_df = None
            if request.strategy_name == "relative_strength":
                reference_symbol = str(
                    request.parameters.get("reference_symbol", settings.SIGNAL_REFERENCE_SYMBOL)
                )
                reference_df = self.data_loader.load_dataframe(
                    reference_symbol,
                    request.timeframe,
                    request.start_date,
                    request.end_date,
                )

            result = self.engine.run_backtest(
                symbol=request.symbol,
                timeframe=request.timeframe,
                df=df,
                strategy_name=request.strategy_name,
                parameters=request.parameters,
                initial_capital=request.initial_capital,
                fee_bps=request.fee_bps,
                slippage_bps=request.slippage_bps,
                max_position_pct=request.max_position_pct,
                reference_df=reference_df,
            )
            metrics = dict(result["metrics"])
            stored_metrics = {
                **metrics,
                "data_quality": result["data_quality"],
                "disclaimer": result["disclaimer"],
            }
            run.status = "completed"
            run.completed_at = datetime.now(UTC)
            run.final_equity = to_decimal(metrics.get("final_equity"))
            run.total_return_pct = to_decimal(metrics.get("total_return_pct"))
            run.max_drawdown_pct = to_decimal(metrics.get("max_drawdown_pct"))
            run.sharpe_ratio = to_decimal(metrics.get("sharpe_ratio"))
            run.win_rate = to_decimal(metrics.get("win_rate"))
            run.profit_factor = to_decimal(metrics.get("profit_factor"))
            run.total_trades = int(metrics.get("total_trades", 0))
            run.metrics = sanitize_json(stored_metrics)
            run.equity_curve = sanitize_json(result["equity_curve"])
            for trade in result["trades"]:
                self.db_session.add(self._trade_from_result(run_id, request.symbol, trade))
            self.db_session.commit()
            return self.get_backtest(run_id) or {}
        except Exception as exc:
            self.db_session.rollback()
            run = self._get_run_row(run_id)
            if run is None:
                run = BacktestRun(
                    workspace_id=self.workspace_id,
                    created_by_user_id=self.user_id,
                    run_id=run_id,
                    symbol=request.symbol,
                    timeframe=request.timeframe,
                    strategy_name=request.strategy_name,
                    parameters=sanitize_json(request.parameters),
                    initial_capital=Decimal(str(request.initial_capital)),
                    status="running",
                    started_at=now,
                )
                self.db_session.add(run)
            run.status = "failed"
            run.completed_at = datetime.now(UTC)
            run.error_message = str(exc)
            run.metrics = {}
            run.equity_curve = []
            self.db_session.commit()
            return self.get_backtest(run_id) or {}

    def get_backtest(self, run_id: str) -> dict[str, Any] | None:
        run = self._get_run_row(run_id)
        if run is None:
            return None
        trades = self._get_trade_rows(run_id)
        return self._run_to_detail(run, trades)

    def list_backtests(
        self,
        symbol: str | None = None,
        strategy_name: str | None = None,
        status: str | None = None,
        limit: int = 50,
    ) -> list[dict[str, Any]]:
        statement = select(BacktestRun).order_by(BacktestRun.created_at.desc()).limit(limit)
        if self.workspace_id:
            statement = statement.where(BacktestRun.workspace_id == self.workspace_id)
        if symbol:
            statement = statement.where(BacktestRun.symbol == symbol)
        if strategy_name:
            statement = statement.where(BacktestRun.strategy_name == strategy_name)
        if status:
            statement = statement.where(BacktestRun.status == status)
        return [self._run_to_summary(row) for row in self.db_session.scalars(statement).all()]

    def delete_backtest(self, run_id: str) -> bool:
        run = self._get_run_row(run_id)
        if run is None:
            return False
        self.db_session.execute(delete(BacktestTrade).where(BacktestTrade.run_id == run_id))
        self.db_session.delete(run)
        self.db_session.commit()
        return True

    def list_strategies(self) -> list[dict[str, Any]]:
        return list_strategies()

    def get_trades(self, run_id: str) -> list[dict[str, Any]]:
        return [self._trade_to_dict(row) for row in self._get_trade_rows(run_id)]

    def get_equity_curve(self, run_id: str) -> list[dict[str, Any]] | None:
        run = self._get_run_row(run_id)
        if run is None:
            return None
        return run.equity_curve or []

    def _get_run_row(self, run_id: str) -> BacktestRun | None:
        statement = select(BacktestRun).where(BacktestRun.run_id == run_id)
        if self.workspace_id:
            statement = statement.where(BacktestRun.workspace_id == self.workspace_id)
        return self.db_session.scalar(statement)

    def _get_trade_rows(self, run_id: str) -> list[BacktestTrade]:
        return list(
            self.db_session.scalars(
                select(BacktestTrade)
                .where(BacktestTrade.run_id == run_id)
                .order_by(BacktestTrade.entry_time.asc())
            ).all()
        )

    def _trade_from_result(
        self,
        run_id: str,
        symbol: str,
        trade: dict[str, Any],
    ) -> BacktestTrade:
        return BacktestTrade(
            workspace_id=self.workspace_id,
            run_id=run_id,
            symbol=symbol,
            side=trade["side"],
            entry_time=self._parse_datetime(trade["entry_time"]),
            entry_price=Decimal(str(trade["entry_price"])),
            exit_time=self._parse_datetime(trade["exit_time"]),
            exit_price=Decimal(str(trade["exit_price"])),
            quantity=Decimal(str(trade["quantity"])),
            notional=Decimal(str(trade["notional"])),
            fee=Decimal(str(trade["fee"])),
            slippage=Decimal(str(trade["slippage"])),
            pnl=Decimal(str(trade["pnl"])),
            pnl_pct=Decimal(str(trade["pnl_pct"])),
            holding_period_bars=int(trade["holding_period_bars"]),
            exit_reason=trade["exit_reason"],
        )

    def _run_to_summary(self, run: BacktestRun) -> dict[str, Any]:
        return {
            "run_id": run.run_id,
            "workspace_id": run.workspace_id,
            "created_by_user_id": run.created_by_user_id,
            "symbol": run.symbol,
            "timeframe": run.timeframe,
            "strategy_name": run.strategy_name,
            "parameters": run.parameters or {},
            "initial_capital": float(run.initial_capital),
            "final_equity": float(run.final_equity) if run.final_equity is not None else None,
            "total_return_pct": float(run.total_return_pct) if run.total_return_pct is not None else None,
            "max_drawdown_pct": float(run.max_drawdown_pct) if run.max_drawdown_pct is not None else None,
            "sharpe_ratio": float(run.sharpe_ratio) if run.sharpe_ratio is not None else None,
            "win_rate": float(run.win_rate) if run.win_rate is not None else None,
            "profit_factor": float(run.profit_factor) if run.profit_factor is not None else None,
            "total_trades": run.total_trades,
            "status": run.status,
            "started_at": to_iso(run.started_at),
            "completed_at": to_iso(run.completed_at),
            "error_message": run.error_message,
            "created_at": to_iso(run.created_at),
        }

    def _run_to_detail(
        self,
        run: BacktestRun,
        trades: list[BacktestTrade],
    ) -> dict[str, Any]:
        metrics = dict(run.metrics or {})
        data_quality = metrics.pop("data_quality", None)
        disclaimer = metrics.pop("disclaimer", BACKTEST_DISCLAIMER)
        return {
            **self._run_to_summary(run),
            "metrics": metrics or None,
            "trades": [self._trade_to_dict(trade) for trade in trades],
            "equity_curve": run.equity_curve or [],
            "data_quality": data_quality,
            "disclaimer": disclaimer,
        }

    def _trade_to_dict(self, trade: BacktestTrade) -> dict[str, Any]:
        return {
            "id": trade.id,
            "run_id": trade.run_id,
            "workspace_id": trade.workspace_id,
            "symbol": trade.symbol,
            "side": trade.side,
            "entry_time": to_iso(trade.entry_time),
            "entry_price": float(trade.entry_price),
            "exit_time": to_iso(trade.exit_time),
            "exit_price": float(trade.exit_price),
            "quantity": float(trade.quantity),
            "notional": float(trade.notional),
            "fee": float(trade.fee),
            "slippage": float(trade.slippage),
            "pnl": float(trade.pnl),
            "pnl_pct": float(trade.pnl_pct),
            "holding_period_bars": trade.holding_period_bars,
            "exit_reason": trade.exit_reason,
            "created_at": to_iso(trade.created_at),
        }

    def _parse_datetime(self, value: str) -> datetime:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
