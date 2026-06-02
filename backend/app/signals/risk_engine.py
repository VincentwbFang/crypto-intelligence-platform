from typing import Any


def _float(value: Any) -> float | None:
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def calculate_drawdown_from_recent_high(
    rows: list[dict[str, Any]],
    lookback: int = 168,
) -> float:
    if not rows:
        return 0.0
    recent_rows = rows[-lookback:]
    highs = [_float(row.get("high")) for row in recent_rows]
    highs = [high for high in highs if high is not None]
    close = _float(rows[-1].get("close"))
    if not highs or close is None:
        return 0.0
    recent_high = max(highs)
    if recent_high == 0:
        return 0.0
    return round(((close - recent_high) / recent_high) * 100, 4)


def detect_overbought_risk(latest_row: dict[str, Any]) -> bool:
    rsi = _float(latest_row.get("rsi_14"))
    return rsi is not None and rsi > 75


def detect_weak_breakout(latest_row: dict[str, Any], previous_row: dict[str, Any]) -> bool:
    latest_close = _float(latest_row.get("close"))
    previous_close = _float(previous_row.get("close"))
    volume_zscore = _float(latest_row.get("volume_zscore_20"))
    if latest_close is None or previous_close is None:
        return False
    return latest_close > previous_close and (volume_zscore is None or volume_zscore < 0.5)


def detect_volatility_expansion(
    latest_row: dict[str, Any],
    recent_rows: list[dict[str, Any]],
) -> bool:
    high = _float(latest_row.get("high"))
    low = _float(latest_row.get("low"))
    if high is None or low is None:
        return False
    latest_range = high - low
    ranges = []
    for row in recent_rows[-20:]:
        row_high = _float(row.get("high"))
        row_low = _float(row.get("low"))
        if row_high is not None and row_low is not None:
            ranges.append(row_high - row_low)
    if not ranges:
        return False
    avg_range = sum(ranges) / len(ranges)
    return avg_range > 0 and latest_range > avg_range * 1.5


def calculate_risk_level(
    volatility_risk_score: float,
    latest_row: dict[str, Any],
    recent_rows: list[dict[str, Any]],
) -> str:
    risk_score = volatility_risk_score
    if detect_overbought_risk(latest_row):
        risk_score += 10
    if detect_volatility_expansion(latest_row, recent_rows):
        risk_score += 10

    if risk_score >= 85:
        return "extreme"
    if risk_score >= 65:
        return "high"
    if risk_score >= 40:
        return "medium"
    return "low"


def generate_risk_notes(
    latest_row: dict[str, Any],
    previous_row: dict[str, Any],
    recent_rows: list[dict[str, Any]],
    volatility_risk_score: float,
) -> list[str]:
    notes: list[str] = []
    if len(recent_rows) < 60:
        notes.append("Insufficient candle history may reduce signal reliability.")
    if detect_overbought_risk(latest_row):
        notes.append("RSI is above 75, which can indicate overbought mean-reversion risk.")
    if detect_weak_breakout(latest_row, previous_row):
        notes.append("Price rose but volume confirmation is limited.")
    if detect_volatility_expansion(latest_row, recent_rows):
        notes.append("Latest candle range is elevated versus recent candles.")
    drawdown = calculate_drawdown_from_recent_high(recent_rows)
    if drawdown <= -15:
        notes.append("Price remains materially below the recent high, showing drawdown damage.")
    if volatility_risk_score >= 65:
        notes.append("Volatility risk score is elevated.")
    if not notes:
        notes.append("No major deterministic risk warning was detected from OHLCV data.")
    return notes

