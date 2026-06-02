from __future__ import annotations

from typing import Any

import pandas as pd

from app.backtesting.risk import (
    BacktestRiskConfig,
    apply_fee,
    apply_slippage,
    calculate_position_size,
    validate_risk_config,
)
from app.backtesting.serialization import to_iso


class PortfolioSimulator:
    def __init__(
        self,
        initial_capital: float,
        fee_bps: float,
        slippage_bps: float,
        max_position_pct: float,
    ) -> None:
        self.initial_capital = float(initial_capital)
        self.fee_bps = float(fee_bps)
        self.slippage_bps = float(slippage_bps)
        self.max_position_pct = float(max_position_pct)
        validate_risk_config(
            BacktestRiskConfig(
                initial_capital=self.initial_capital,
                fee_bps=self.fee_bps,
                slippage_bps=self.slippage_bps,
                max_position_pct=self.max_position_pct,
            )
        )

    def run(self, signal_df: pd.DataFrame) -> dict[str, Any]:
        if signal_df.empty:
            return {
                "final_equity": self.initial_capital,
                "trades": [],
                "equity_curve": [],
            }

        df = signal_df.copy().sort_values("timestamp").reset_index(drop=True)
        cash = self.initial_capital
        quantity = 0.0
        entry_price = 0.0
        entry_time: Any = None
        entry_fee = 0.0
        entry_notional = 0.0
        entry_slippage = 0.0
        entry_index = 0
        peak_equity = self.initial_capital
        trades: list[dict[str, Any]] = []
        equity_curve: list[dict[str, Any]] = []

        def mark_equity(row: pd.Series) -> None:
            nonlocal peak_equity
            close = float(row["close"])
            position_value = quantity * close
            equity = cash + position_value
            peak_equity = max(peak_equity, equity)
            drawdown = ((equity - peak_equity) / peak_equity) * 100 if peak_equity else 0.0
            equity_curve.append(
                {
                    "timestamp": to_iso(row["timestamp"]),
                    "equity": round(equity, 6),
                    "cash": round(cash, 6),
                    "position_value": round(position_value, 6),
                    "drawdown_pct": round(drawdown, 6),
                }
            )

        def enter(row: pd.Series, index: int) -> None:
            nonlocal cash, quantity, entry_price, entry_time, entry_fee
            nonlocal entry_notional, entry_slippage, entry_index
            close = float(row["close"])
            execution_price = apply_slippage(close, "buy", self.slippage_bps)
            equity = cash
            desired_quantity = calculate_position_size(equity, execution_price, self.max_position_pct)
            notional = desired_quantity * execution_price
            fee = apply_fee(notional, self.fee_bps)
            if notional + fee > cash and execution_price > 0:
                notional = cash / (1 + self.fee_bps / 10_000)
                desired_quantity = notional / execution_price
                fee = apply_fee(notional, self.fee_bps)
            if desired_quantity <= 0 or notional + fee > cash:
                return
            cash -= notional + fee
            quantity = desired_quantity
            entry_price = execution_price
            entry_time = row["timestamp"]
            entry_fee = fee
            entry_notional = notional
            entry_slippage = abs(execution_price - close) * quantity
            entry_index = index

        def exit_position(row: pd.Series, index: int, reason: str) -> None:
            nonlocal cash, quantity, entry_price, entry_time, entry_fee
            nonlocal entry_notional, entry_slippage
            if quantity <= 0:
                return
            close = float(row["close"])
            execution_price = apply_slippage(close, "sell", self.slippage_bps)
            gross_exit = quantity * execution_price
            exit_fee = apply_fee(gross_exit, self.fee_bps)
            cash += gross_exit - exit_fee
            total_fee = entry_fee + exit_fee
            exit_slippage = abs(close - execution_price) * quantity
            pnl = gross_exit - exit_fee - entry_notional - entry_fee
            pnl_pct = (pnl / (entry_notional + entry_fee)) * 100 if entry_notional + entry_fee else 0.0
            trades.append(
                {
                    "symbol": str(row.get("symbol", "")),
                    "side": "long",
                    "entry_time": to_iso(entry_time),
                    "entry_price": round(entry_price, 10),
                    "exit_time": to_iso(row["timestamp"]),
                    "exit_price": round(execution_price, 10),
                    "quantity": round(quantity, 12),
                    "notional": round(entry_notional, 10),
                    "fee": round(total_fee, 10),
                    "slippage": round(entry_slippage + exit_slippage, 10),
                    "pnl": round(pnl, 10),
                    "pnl_pct": round(pnl_pct, 6),
                    "holding_period_bars": max(index - entry_index, 0),
                    "exit_reason": reason,
                }
            )
            quantity = 0.0
            entry_price = 0.0
            entry_time = None
            entry_fee = 0.0
            entry_notional = 0.0
            entry_slippage = 0.0

        mark_equity(df.iloc[0])
        for index in range(1, len(df)):
            previous_signal = int(df.iloc[index - 1].get("signal", 0))
            current = df.iloc[index]
            if quantity <= 0 and previous_signal == 1 and index < len(df) - 1:
                enter(current, index)
            elif quantity > 0 and previous_signal == 0:
                exit_position(current, index, "signal_exit")
            mark_equity(current)

        if quantity > 0:
            final_index = len(df) - 1
            final_row = df.iloc[final_index]
            exit_position(final_row, final_index, "end_of_backtest")
            if equity_curve:
                peak_equity = max(peak_equity, cash)
                drawdown = ((cash - peak_equity) / peak_equity) * 100 if peak_equity else 0.0
                equity_curve[-1] = {
                    "timestamp": to_iso(final_row["timestamp"]),
                    "equity": round(cash, 6),
                    "cash": round(cash, 6),
                    "position_value": 0.0,
                    "drawdown_pct": round(drawdown, 6),
                }

        final_equity = equity_curve[-1]["equity"] if equity_curve else self.initial_capital
        return {
            "final_equity": float(final_equity),
            "trades": trades,
            "equity_curve": equity_curve,
        }
