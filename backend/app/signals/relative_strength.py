from typing import Any


def calculate_return_pct(rows: list[dict[str, Any]], lookback: int) -> float | None:
    if len(rows) <= lookback:
        return None
    latest_close = rows[-1].get("close")
    prior_close = rows[-1 - lookback].get("close")
    try:
        latest = float(latest_close)
        prior = float(prior_close)
    except (TypeError, ValueError):
        return None
    if prior == 0:
        return None
    return round(((latest - prior) / prior) * 100, 4)


def calculate_relative_strength(
    target_rows: list[dict[str, Any]],
    reference_rows: list[dict[str, Any]],
    lookback: int,
) -> float | None:
    target_return = calculate_return_pct(target_rows, lookback)
    reference_return = calculate_return_pct(reference_rows, lookback)
    if target_return is None or reference_return is None:
        return None
    return round(target_return - reference_return, 4)


def calculate_relative_strength_score(
    target_rows: list[dict[str, Any]],
    reference_rows: list[dict[str, Any]],
    reference_symbol: str = "BTC/USDT",
) -> dict[str, Any]:
    return_24h = calculate_return_pct(target_rows, 24)
    reference_return_24h = calculate_return_pct(reference_rows, 24)
    relative_return_24h = calculate_relative_strength(target_rows, reference_rows, 24)
    return_7d = calculate_return_pct(target_rows, 168)
    reference_return_7d = calculate_return_pct(reference_rows, 168)
    relative_return_7d = calculate_relative_strength(target_rows, reference_rows, 168)

    if relative_return_24h is None and relative_return_7d is None:
        score = 50.0
        explanation = "Insufficient data to calculate relative strength."
    else:
        score = 50.0
        if relative_return_24h is not None:
            score += relative_return_24h * 2.0
        if relative_return_7d is not None:
            score += relative_return_7d * 1.0
        score = round(max(0.0, min(100.0, score)), 4)
        if score > 55:
            explanation = "Target is outperforming the reference symbol."
        elif score < 45:
            explanation = "Target is underperforming the reference symbol."
        else:
            explanation = "Target is broadly in line with the reference symbol."

    return {
        "reference_symbol": reference_symbol,
        "return_24h": return_24h,
        "reference_return_24h": reference_return_24h,
        "relative_return_24h": relative_return_24h,
        "return_7d": return_7d,
        "reference_return_7d": reference_return_7d,
        "relative_return_7d": relative_return_7d,
        "relative_strength_score": score,
        "explanation": explanation,
    }
