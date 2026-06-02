import math
from typing import Any

import pandas as pd

from app.core.config import settings
from app.indicators.technicals import add_all_indicators
from app.signals.relative_strength import calculate_relative_strength_score
from app.signals.risk_engine import calculate_risk_level, generate_risk_notes
from app.signals.scoring import (
    calculate_momentum_score,
    calculate_overall_signal_score,
    calculate_trend_score,
    calculate_volume_score,
    calculate_volatility_risk_score,
    classify_setup_type,
    classify_signal_direction,
)

INDICATOR_COLUMNS = (
    "ema_20",
    "ema_50",
    "ema_200",
    "rsi_14",
    "macd",
    "macd_signal",
    "macd_histogram",
    "atr_14",
    "volume_zscore_20",
    "realized_volatility_20",
)


class SignalEngine:
    def __init__(self, min_required_candles: int | None = None) -> None:
        self.min_required_candles = min_required_candles or settings.SIGNAL_MIN_CANDLES

    def generate_signal(
        self,
        symbol: str,
        timeframe: str,
        rows: list[dict[str, Any]],
        reference_rows: list[dict[str, Any]] | None = None,
    ) -> dict[str, Any]:
        if not rows:
            return self._insufficient_signal(symbol, timeframe, 0)

        indicator_rows = self._indicator_rows(rows)
        latest_row = indicator_rows[-1]
        previous_row = indicator_rows[-2] if len(indicator_rows) > 1 else latest_row

        relative_strength = calculate_relative_strength_score(
            indicator_rows,
            reference_rows or [],
            reference_symbol=settings.SIGNAL_REFERENCE_SYMBOL,
        )
        scores = {
            "trend_score": calculate_trend_score(latest_row),
            "momentum_score": calculate_momentum_score(latest_row),
            "volume_score": calculate_volume_score(latest_row),
            "volatility_risk_score": calculate_volatility_risk_score(
                latest_row,
                indicator_rows,
            ),
            "relative_strength_score": relative_strength["relative_strength_score"],
        }
        scores["overall_signal_score"] = calculate_overall_signal_score(scores)

        has_sufficient_data = len(rows) >= self.min_required_candles
        missing_indicator_warning = any(
            self._is_missing(latest_row.get(column)) for column in INDICATOR_COLUMNS
        )
        if not has_sufficient_data:
            setup_type = "insufficient_data"
            signal_direction = "neutral"
        else:
            setup_type = classify_setup_type(scores, latest_row)
            signal_direction = classify_signal_direction(scores, latest_row)

        risk_level = calculate_risk_level(
            scores["volatility_risk_score"],
            latest_row,
            indicator_rows,
        )
        risk_notes = generate_risk_notes(
            latest_row,
            previous_row,
            indicator_rows,
            scores["volatility_risk_score"],
        )
        signal = {
            "symbol": symbol,
            "timeframe": timeframe,
            "timestamp": self._json_value(latest_row.get("timestamp")),
            "latest_close": self._json_value(latest_row.get("close")),
            "scores": {key: self._json_value(value) for key, value in scores.items()},
            "signal_direction": signal_direction,
            "setup_type": setup_type,
            "risk_level": risk_level,
            "indicators": {
                column: self._json_value(latest_row.get(column))
                for column in INDICATOR_COLUMNS
            },
            "relative_strength": self._json_value(relative_strength),
            "risk_notes": risk_notes,
            "data_quality": {
                "candle_count": len(rows),
                "min_required_candles": self.min_required_candles,
                "has_sufficient_data": has_sufficient_data,
                "missing_indicator_warning": missing_indicator_warning,
            },
            "explanation": self._deterministic_explanation(
                signal_direction,
                setup_type,
                risk_level,
                scores,
            ),
        }
        return self._json_value(signal)

    def _indicator_rows(self, rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
        df = pd.DataFrame(rows)
        with_indicators = add_all_indicators(df)
        return with_indicators.to_dict(orient="records")

    def _insufficient_signal(
        self,
        symbol: str,
        timeframe: str,
        candle_count: int,
    ) -> dict[str, Any]:
        return {
            "symbol": symbol,
            "timeframe": timeframe,
            "timestamp": None,
            "latest_close": None,
            "scores": {
                "trend_score": 0.0,
                "momentum_score": 0.0,
                "volume_score": 0.0,
                "volatility_risk_score": 0.0,
                "relative_strength_score": 50.0,
                "overall_signal_score": 0.0,
            },
            "signal_direction": "neutral",
            "setup_type": "insufficient_data",
            "risk_level": "medium",
            "indicators": {column: None for column in INDICATOR_COLUMNS},
            "relative_strength": {
                "reference_symbol": settings.SIGNAL_REFERENCE_SYMBOL,
                "return_24h": None,
                "reference_return_24h": None,
                "relative_return_24h": None,
                "return_7d": None,
                "reference_return_7d": None,
                "relative_return_7d": None,
                "relative_strength_score": 50.0,
                "explanation": "Insufficient data to calculate relative strength.",
            },
            "risk_notes": ["Insufficient candle history may reduce signal reliability."],
            "data_quality": {
                "candle_count": candle_count,
                "min_required_candles": self.min_required_candles,
                "has_sufficient_data": False,
                "missing_indicator_warning": True,
            },
            "explanation": "Insufficient candle history for a reliable deterministic signal.",
        }

    def _deterministic_explanation(
        self,
        direction: str,
        setup_type: str,
        risk_level: str,
        scores: dict[str, float],
    ) -> str:
        return (
            f"Deterministic signal is {direction} with setup {setup_type}. "
            f"Overall score is {scores['overall_signal_score']:.2f}; "
            f"risk level is {risk_level}."
        )

    def _is_missing(self, value: Any) -> bool:
        try:
            return value is None or not math.isfinite(float(value))
        except (TypeError, ValueError):
            return True

    def _json_value(self, value: Any) -> Any:
        if isinstance(value, dict):
            return {key: self._json_value(child) for key, child in value.items()}
        if isinstance(value, list):
            return [self._json_value(child) for child in value]
        if isinstance(value, pd.Timestamp):
            return value.isoformat()
        if hasattr(value, "isoformat") and not isinstance(value, (int, float, str)):
            return value.isoformat()
        if isinstance(value, float):
            if not math.isfinite(value):
                return None
            return round(value, 6)
        return value
