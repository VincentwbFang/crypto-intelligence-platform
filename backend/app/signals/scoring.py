import math
from typing import Any


def _finite(value: Any) -> float | None:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    if not math.isfinite(number):
        return None
    return number


def _clamp(score: float) -> float:
    return round(max(0.0, min(100.0, score)), 4)


def calculate_trend_score(latest_row: dict[str, Any]) -> float:
    close = _finite(latest_row.get("close"))
    ema_20 = _finite(latest_row.get("ema_20"))
    ema_50 = _finite(latest_row.get("ema_50"))
    ema_200 = _finite(latest_row.get("ema_200"))
    if close is None or ema_20 is None or ema_50 is None:
        return 35.0

    score = 50.0
    if close > ema_20 > ema_50:
        score = 70.0
    if ema_200 is not None and close > ema_20 > ema_50 > ema_200:
        score = 90.0
    if close < ema_20:
        score -= 25.0
    if ema_20 < ema_50:
        score -= 20.0
    if ema_200 is None:
        score -= 10.0
    elif close < ema_200:
        score -= 15.0
    return _clamp(score)


def calculate_momentum_score(latest_row: dict[str, Any]) -> float:
    rsi = _finite(latest_row.get("rsi_14"))
    macd_histogram = _finite(latest_row.get("macd_histogram"))
    score = 50.0

    if rsi is not None:
        if 50 <= rsi <= 70:
            score += 22.0
        elif 40 <= rsi < 50:
            score += 5.0
        elif 70 < rsi <= 75:
            score += 10.0
        elif rsi > 75:
            score -= 8.0
        elif rsi < 35:
            score -= 18.0
    if macd_histogram is not None:
        if macd_histogram > 0:
            score += min(18.0, abs(macd_histogram) * 4)
        elif macd_histogram < 0:
            score -= min(18.0, abs(macd_histogram) * 4)
    return _clamp(score)


def calculate_volume_score(latest_row: dict[str, Any]) -> float:
    volume_zscore = _finite(latest_row.get("volume_zscore_20"))
    open_ = _finite(latest_row.get("open"))
    close = _finite(latest_row.get("close"))
    if volume_zscore is None:
        return 50.0

    price_return = 0.0
    if open_ not in (None, 0.0) and close is not None:
        price_return = (close - open_) / open_

    score = 50.0
    if volume_zscore > 1 and price_return > 0:
        score += 28.0
    elif volume_zscore > 1 and price_return < 0:
        score -= 12.0
    elif volume_zscore < 0 and price_return > 0:
        score -= 15.0
    elif volume_zscore < -1:
        score -= 8.0
    else:
        score += 5.0
    return _clamp(score)


def calculate_volatility_risk_score(
    latest_row: dict[str, Any],
    recent_rows: list[dict[str, Any]],
) -> float:
    realized_volatility = _finite(latest_row.get("realized_volatility_20"))
    high = _finite(latest_row.get("high"))
    low = _finite(latest_row.get("low"))
    atr = _finite(latest_row.get("atr_14"))
    score = 25.0

    if realized_volatility is not None:
        score += min(35.0, realized_volatility * 500)

    latest_range = None
    if high is not None and low is not None:
        latest_range = max(0.0, high - low)

    ranges = []
    atr_values = []
    for row in recent_rows[-20:]:
        row_high = _finite(row.get("high"))
        row_low = _finite(row.get("low"))
        row_atr = _finite(row.get("atr_14"))
        if row_high is not None and row_low is not None:
            ranges.append(max(0.0, row_high - row_low))
        if row_atr is not None:
            atr_values.append(row_atr)

    if latest_range is not None and ranges:
        avg_range = sum(ranges) / len(ranges)
        if avg_range > 0 and latest_range > avg_range * 1.8:
            score += 25.0
        elif avg_range > 0 and latest_range > avg_range * 1.3:
            score += 12.0

    if atr is not None and len(atr_values) >= 5:
        avg_atr = sum(atr_values[:-1] or atr_values) / len(atr_values[:-1] or atr_values)
        if avg_atr > 0 and atr > avg_atr * 1.5:
            score += 18.0

    return _clamp(score)


def calculate_overall_signal_score(scores: dict[str, Any]) -> float:
    trend = _finite(scores.get("trend_score")) or 0.0
    momentum = _finite(scores.get("momentum_score")) or 0.0
    volume = _finite(scores.get("volume_score")) or 0.0
    relative_strength = _finite(scores.get("relative_strength_score"))
    if relative_strength is None:
        relative_strength = 50.0
    return _clamp(
        trend * 0.35
        + momentum * 0.25
        + volume * 0.20
        + relative_strength * 0.20
    )


def classify_signal_direction(scores: dict[str, Any], latest_row: dict[str, Any]) -> str:
    overall = _finite(scores.get("overall_signal_score")) or 50.0
    trend = _finite(scores.get("trend_score")) or 50.0
    momentum = _finite(scores.get("momentum_score")) or 50.0
    macd_histogram = _finite(latest_row.get("macd_histogram"))

    if overall >= 65 and trend >= 60 and momentum >= 55:
        return "bullish"
    if overall <= 38 and trend <= 45 and momentum <= 45:
        return "bearish"
    if macd_histogram is not None and trend >= 58 and macd_histogram < 0:
        return "mixed"
    if 45 <= overall <= 58:
        return "neutral"
    return "mixed"


def classify_setup_type(scores: dict[str, Any], latest_row: dict[str, Any]) -> str:
    trend = _finite(scores.get("trend_score")) or 50.0
    momentum = _finite(scores.get("momentum_score")) or 50.0
    volume = _finite(scores.get("volume_score")) or 50.0
    risk = _finite(scores.get("volatility_risk_score")) or 50.0
    close = _finite(latest_row.get("close"))
    rolling_high = _finite(latest_row.get("rolling_high_20"))
    rolling_low = _finite(latest_row.get("rolling_low_20"))
    rsi = _finite(latest_row.get("rsi_14"))

    if close is None:
        return "insufficient_data"
    if trend >= 72 and momentum >= 58 and risk < 75:
        return "trend_continuation"
    if rolling_high is not None and close >= rolling_high * 0.995 and volume >= 58:
        return "breakout_watch"
    if rsi is not None and rsi > 75:
        return "mean_reversion_risk"
    if rolling_low is not None and close <= rolling_low * 1.005 and trend < 45:
        return "breakdown_risk"
    if 42 <= trend <= 62 and 42 <= momentum <= 62:
        return "range_bound"
    return "range_bound"

