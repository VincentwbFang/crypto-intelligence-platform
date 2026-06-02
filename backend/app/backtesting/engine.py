from __future__ import annotations

from typing import Any

import pandas as pd

from app.backtesting.metrics import calculate_metrics
from app.backtesting.models import BACKTEST_DISCLAIMER
from app.backtesting.portfolio import PortfolioSimulator
from app.backtesting.serialization import sanitize_json, to_iso
from app.backtesting.strategies import get_strategy


class BacktestEngine:
    def __init__(self, min_candles: int = 100) -> None:
        self.min_candles = min_candles

    def run_backtest(
        self,
        symbol: str,
        timeframe: str,
        df: pd.DataFrame,
        strategy_name: str,
        parameters: dict[str, Any],
        initial_capital: float,
        fee_bps: float,
        slippage_bps: float,
        max_position_pct: float,
        reference_df: pd.DataFrame | None = None,
    ) -> dict[str, Any]:
        clean_df = self._prepare_dataframe(df, symbol)
        candle_count = len(clean_df)
        if candle_count < self.min_candles:
            raise ValueError(
                f"Insufficient OHLCV data for backtest: {candle_count} candles, "
                f"minimum required is {self.min_candles}."
            )

        strategy = get_strategy(strategy_name)
        strategy_parameters = dict(parameters or {})
        if reference_df is not None:
            strategy_parameters["reference_df"] = self._prepare_dataframe(
                reference_df,
                str(strategy_parameters.get("reference_symbol", "BTC/USDT")),
            )

        signal_df = strategy.generate_signals(clean_df, strategy_parameters)
        signal_df["symbol"] = symbol
        signal_df["signal"] = signal_df["signal"].clip(lower=0, upper=1).fillna(0).astype(int)

        simulation = PortfolioSimulator(
            initial_capital=initial_capital,
            fee_bps=fee_bps,
            slippage_bps=slippage_bps,
            max_position_pct=max_position_pct,
        ).run(signal_df)
        metrics = calculate_metrics(
            initial_capital=initial_capital,
            final_equity=simulation["final_equity"],
            equity_curve=simulation["equity_curve"],
            trades=simulation["trades"],
            timeframe=timeframe,
        )
        result = {
            "symbol": symbol,
            "timeframe": timeframe,
            "strategy_name": strategy_name,
            "parameters": parameters or {},
            "metrics": metrics,
            "trades": simulation["trades"],
            "equity_curve": simulation["equity_curve"],
            "data_quality": {
                "candle_count": candle_count,
                "start_date": to_iso(clean_df.iloc[0]["timestamp"]),
                "end_date": to_iso(clean_df.iloc[-1]["timestamp"]),
                "has_sufficient_data": True,
            },
            "disclaimer": BACKTEST_DISCLAIMER,
        }
        return sanitize_json(result)

    def _prepare_dataframe(self, df: pd.DataFrame, symbol: str) -> pd.DataFrame:
        required = ("timestamp", "open", "high", "low", "close", "volume")
        missing = [column for column in required if column not in df.columns]
        if missing:
            raise ValueError(f"Missing required OHLCV columns: {', '.join(missing)}")
        clean = df.copy()
        clean["timestamp"] = pd.to_datetime(clean["timestamp"], utc=True)
        for column in ("open", "high", "low", "close", "volume"):
            clean[column] = pd.to_numeric(clean[column], errors="coerce").astype(float)
        clean = clean.dropna(subset=list(required))
        clean = clean.sort_values("timestamp").drop_duplicates("timestamp", keep="last")
        clean["symbol"] = symbol
        return clean.reset_index(drop=True)
