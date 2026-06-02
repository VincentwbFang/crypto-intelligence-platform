from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Protocol

import numpy as np
import pandas as pd


class BacktestStrategy(Protocol):
    name: str
    description: str
    default_parameters: dict[str, Any]

    def generate_signals(
        self,
        df: pd.DataFrame,
        parameters: dict[str, Any],
    ) -> pd.DataFrame:
        ...


@dataclass(frozen=True)
class StrategyInfo:
    name: str
    description: str
    default_parameters: dict[str, Any]
    supported_positioning: str = "long_only"


def _base_signal_frame(df: pd.DataFrame) -> pd.DataFrame:
    result = df.copy()
    result["timestamp"] = pd.to_datetime(result["timestamp"], utc=True)
    result = result.sort_values("timestamp").reset_index(drop=True)
    result["close"] = pd.to_numeric(result["close"], errors="coerce").astype(float)
    result["signal"] = 0
    return result


def _rsi(close: pd.Series, period: int) -> pd.Series:
    delta = close.diff()
    gain = delta.clip(lower=0).rolling(period, min_periods=period).mean()
    loss = (-delta.clip(upper=0)).rolling(period, min_periods=period).mean()
    rs = gain / loss.replace(0, np.nan)
    rsi = 100 - (100 / (1 + rs))
    return rsi.fillna(50.0)


class EMACrossoverStrategy:
    name = "ema_crossover"
    description = "Long-only exposure when a fast EMA is above a slow EMA."
    default_parameters = {"fast_ema": 20, "slow_ema": 50}

    def generate_signals(self, df: pd.DataFrame, parameters: dict[str, Any]) -> pd.DataFrame:
        result = _base_signal_frame(df)
        fast = int(parameters.get("fast_ema", self.default_parameters["fast_ema"]))
        slow = int(parameters.get("slow_ema", self.default_parameters["slow_ema"]))
        if fast <= 0 or slow <= 0 or fast >= slow:
            raise ValueError("fast_ema must be greater than 0 and less than slow_ema.")
        result["fast_ema"] = result["close"].ewm(span=fast, adjust=False, min_periods=fast).mean()
        result["slow_ema"] = result["close"].ewm(span=slow, adjust=False, min_periods=slow).mean()
        result["signal"] = ((result["fast_ema"] > result["slow_ema"]) & result["slow_ema"].notna()).astype(int)
        return result


class RSIMeanReversionStrategy:
    name = "rsi_mean_reversion"
    description = "Long-only research setup that enters after oversold RSI and exits on RSI recovery."
    default_parameters = {"rsi_period": 14, "oversold": 30, "exit_rsi": 50}

    def generate_signals(self, df: pd.DataFrame, parameters: dict[str, Any]) -> pd.DataFrame:
        result = _base_signal_frame(df)
        period = int(parameters.get("rsi_period", self.default_parameters["rsi_period"]))
        oversold = float(parameters.get("oversold", self.default_parameters["oversold"]))
        exit_rsi = float(parameters.get("exit_rsi", self.default_parameters["exit_rsi"]))
        result["rsi"] = _rsi(result["close"], period)

        in_position = False
        signals: list[int] = []
        for value in result["rsi"]:
            if not in_position and value < oversold:
                in_position = True
            elif in_position and value > exit_rsi:
                in_position = False
            signals.append(1 if in_position else 0)
        result["signal"] = signals
        return result


class BreakoutStrategy:
    name = "breakout"
    description = "Long-only breakout watch using prior rolling highs and volume confirmation."
    default_parameters = {"lookback": 20, "volume_zscore_threshold": 1.0}

    def generate_signals(self, df: pd.DataFrame, parameters: dict[str, Any]) -> pd.DataFrame:
        result = _base_signal_frame(df)
        lookback = int(parameters.get("lookback", self.default_parameters["lookback"]))
        threshold = float(parameters.get("volume_zscore_threshold", self.default_parameters["volume_zscore_threshold"]))
        volume = pd.to_numeric(df["volume"], errors="coerce").astype(float)
        result["rolling_high"] = result["close"].rolling(lookback, min_periods=lookback).max().shift(1)
        result["rolling_low"] = result["close"].rolling(lookback, min_periods=lookback).min().shift(1)
        volume_mean = volume.rolling(lookback, min_periods=lookback).mean()
        volume_std = volume.rolling(lookback, min_periods=lookback).std(ddof=0)
        result["volume_zscore"] = (volume - volume_mean) / volume_std.replace(0, np.nan)

        in_position = False
        signals: list[int] = []
        for _, row in result.iterrows():
            if not in_position:
                if row["close"] > row["rolling_high"] and row["volume_zscore"] > threshold:
                    in_position = True
            elif row["close"] < row["rolling_low"]:
                in_position = False
            signals.append(1 if in_position else 0)
        result["signal"] = signals
        return result


class RelativeStrengthStrategy:
    name = "relative_strength"
    description = "Long-only exposure when the target outperforms a reference symbol over a lookback window."
    default_parameters = {
        "reference_symbol": "BTC/USDT",
        "lookback": 24,
        "threshold": 2.0,
    }

    def generate_signals(self, df: pd.DataFrame, parameters: dict[str, Any]) -> pd.DataFrame:
        result = _base_signal_frame(df)
        reference_df = parameters.get("reference_df")
        if reference_df is None or not isinstance(reference_df, pd.DataFrame) or reference_df.empty:
            result["relative_return"] = np.nan
            result["signal"] = 0
            return result

        lookback = int(parameters.get("lookback", self.default_parameters["lookback"]))
        threshold = float(parameters.get("threshold", self.default_parameters["threshold"]))
        reference = _base_signal_frame(reference_df)[["timestamp", "close"]].rename(
            columns={"close": "reference_close"}
        )
        merged = result.merge(reference, on="timestamp", how="left")
        merged["reference_close"] = merged["reference_close"].ffill()
        target_return = merged["close"].pct_change(lookback) * 100
        reference_return = merged["reference_close"].pct_change(lookback) * 100
        merged["relative_return"] = target_return - reference_return

        in_position = False
        signals: list[int] = []
        for value in merged["relative_return"]:
            if not in_position and value > threshold:
                in_position = True
            elif in_position and value < 0:
                in_position = False
            signals.append(1 if in_position else 0)
        merged["signal"] = signals
        return merged


STRATEGIES: dict[str, BacktestStrategy] = {
    "ema_crossover": EMACrossoverStrategy(),
    "rsi_mean_reversion": RSIMeanReversionStrategy(),
    "breakout": BreakoutStrategy(),
    "relative_strength": RelativeStrengthStrategy(),
}


def get_strategy(strategy_name: str) -> BacktestStrategy:
    strategy = STRATEGIES.get(strategy_name)
    if strategy is None:
        raise ValueError(f"Unsupported backtest strategy: {strategy_name}")
    return strategy


def list_strategies() -> list[dict[str, Any]]:
    return [
        {
            "name": strategy.name,
            "description": strategy.description,
            "default_parameters": dict(strategy.default_parameters),
            "supported_positioning": "long_only",
        }
        for strategy in STRATEGIES.values()
    ]
