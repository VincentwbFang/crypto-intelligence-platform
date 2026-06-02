from typing import Any

ALERT_SEVERITIES = ("info", "low", "medium", "high", "critical")


def classify_alert_severity(alert_type: str, signal: dict[str, Any]) -> str:
    risk_level = str(signal.get("risk_level") or "").lower()

    if risk_level == "extreme":
        return "critical"

    if alert_type == "insufficient_data":
        return "low"

    if alert_type == "trend_damage":
        return "high"

    if alert_type == "high_risk":
        return "high" if risk_level == "high" else "medium"

    if alert_type == "volatility_expansion":
        return "high" if risk_level in {"high", "extreme"} else "medium"

    if alert_type == "weak_breakout":
        return "high" if risk_level in {"high", "extreme"} else "medium"

    if alert_type == "relative_strength":
        return "medium"

    if alert_type == "signal_change":
        return "high" if risk_level in {"high", "extreme"} else "medium"

    if alert_type == "high_signal_score":
        return "high" if risk_level == "high" else "medium"

    return "info"
