from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from app.alerts.severity import classify_alert_severity
from app.core.config import settings


class AlertRuleEngine:
    def evaluate_signal(
        self,
        signal: dict[str, Any],
        previous_signal: dict[str, Any] | None = None,
        config: dict[str, Any] | None = None,
    ) -> list[dict[str, Any]]:
        thresholds = {
            "signal_score_threshold": settings.ALERT_SIGNAL_SCORE_THRESHOLD,
            "high_risk_threshold": settings.ALERT_HIGH_RISK_THRESHOLD,
        }
        if config:
            thresholds.update(config)

        candidates: list[dict[str, Any]] = []
        scores = signal.get("scores", {})
        data_quality = signal.get("data_quality", {})
        risk_notes = [str(note).lower() for note in signal.get("risk_notes", [])]
        overall_score = _to_float(scores.get("overall_signal_score"))
        volatility_risk_score = _to_float(scores.get("volatility_risk_score"))
        relative_strength_score = _to_float(scores.get("relative_strength_score"))
        volume_score = _to_float(scores.get("volume_score"))
        trend_score = _to_float(scores.get("trend_score"))
        risk_level = str(signal.get("risk_level") or "medium").lower()
        direction = str(signal.get("signal_direction") or "neutral").lower()
        setup_type = str(signal.get("setup_type") or "unknown")
        has_sufficient_data = bool(data_quality.get("has_sufficient_data"))

        if overall_score >= thresholds["signal_score_threshold"] and has_sufficient_data:
            candidates.append(
                self._candidate(
                    alert_type="high_signal_score",
                    title="High signal score detected",
                    message=(
                        f"{signal['symbol']} {signal['timeframe']} has a high signal "
                        f"score of {overall_score:.1f}. Direction: {direction}; "
                        f"setup: {setup_type}; risk: {risk_level}. "
                        "This is for educational and research purposes only."
                    ),
                    signal=signal,
                )
            )

        if risk_level in {"high", "extreme"} or (
            volatility_risk_score >= thresholds["high_risk_threshold"]
        ):
            candidates.append(
                self._candidate(
                    alert_type="high_risk",
                    title="Elevated risk detected",
                    message=(
                        f"{signal['symbol']} {signal['timeframe']} risk is {risk_level}; "
                        f"volatility risk score is {volatility_risk_score:.1f}. "
                        "Monitor market conditions with caution."
                    ),
                    signal=signal,
                )
            )

        if relative_strength_score >= 70 and direction in {"bullish", "mixed"}:
            candidates.append(
                self._candidate(
                    alert_type="relative_strength",
                    title="Relative strength improved",
                    message=(
                        f"{signal['symbol']} {signal['timeframe']} relative strength "
                        f"score is {relative_strength_score:.1f} versus the reference "
                        "symbol. The signal remains research-only."
                    ),
                    signal=signal,
                )
            )

        if self._has_weak_breakout_note(risk_notes) or (
            setup_type == "breakout_watch" and volume_score < 50
        ):
            candidates.append(
                self._candidate(
                    alert_type="weak_breakout",
                    title="Breakout confirmation risk detected",
                    message=(
                        f"{signal['symbol']} {signal['timeframe']} shows breakout-watch "
                        "conditions with limited volume confirmation. Treat the setup "
                        "as uncertain until data improves."
                    ),
                    signal=signal,
                )
            )

        if direction == "bearish" and trend_score < 40 and risk_level in {"high", "extreme"}:
            candidates.append(
                self._candidate(
                    alert_type="trend_damage",
                    title="Trend damage warning",
                    message=(
                        f"{signal['symbol']} {signal['timeframe']} has bearish direction, "
                        f"trend score {trend_score:.1f}, and {risk_level} risk. "
                        "This warning describes market structure, not a trade instruction."
                    ),
                    signal=signal,
                )
            )

        if not has_sufficient_data:
            candidates.append(
                self._candidate(
                    alert_type="insufficient_data",
                    title="Insufficient market data",
                    message=(
                        f"{signal['symbol']} {signal['timeframe']} does not have enough "
                        "stored candles for a reliable deterministic signal."
                    ),
                    signal=signal,
                )
            )

        if previous_signal is not None and self._signal_changed(previous_signal, signal):
            previous_score = _to_float(
                previous_signal.get("scores", {}).get("overall_signal_score")
            )
            candidates.append(
                self._candidate(
                    alert_type="signal_change",
                    title="Signal state changed",
                    message=(
                        f"{signal['symbol']} {signal['timeframe']} signal state changed. "
                        f"Previous direction/risk/score: "
                        f"{previous_signal.get('signal_direction')}/"
                        f"{previous_signal.get('risk_level')}/{previous_score:.1f}. "
                        f"Current direction/risk/score: {direction}/{risk_level}/"
                        f"{overall_score:.1f}."
                    ),
                    signal=signal,
                    previous_signal=previous_signal,
                )
            )

        return candidates

    def _candidate(
        self,
        alert_type: str,
        title: str,
        message: str,
        signal: dict[str, Any],
        previous_signal: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        scores = signal.get("scores", {})
        setup_type = str(signal.get("setup_type") or "unknown")
        risk_level = str(signal.get("risk_level") or "medium").lower()
        severity = classify_alert_severity(alert_type, signal)
        symbol = str(signal.get("symbol") or "")
        timeframe = str(signal.get("timeframe") or settings.DEFAULT_TIMEFRAME)
        return {
            "symbol": symbol,
            "timeframe": timeframe,
            "timestamp": signal.get("timestamp") or datetime.now(UTC).isoformat(),
            "alert_type": alert_type,
            "severity": severity,
            "title": title,
            "message": message,
            "source": "signal_engine",
            "signal_score": _to_float(scores.get("overall_signal_score")),
            "risk_level": risk_level,
            "setup_type": setup_type,
            "dedup_key": f"{symbol}:{timeframe}:{alert_type}:{setup_type}:{risk_level}",
            "raw_payload": {
                "signal": signal,
                "previous_signal": previous_signal,
                "rule": alert_type,
            },
        }

    def _has_weak_breakout_note(self, risk_notes: list[str]) -> bool:
        return any(
            "weak breakout" in note
            or ("breakout" in note and "volume" in note and "confirm" in note)
            for note in risk_notes
        )

    def _signal_changed(
        self,
        previous_signal: dict[str, Any],
        current_signal: dict[str, Any],
    ) -> bool:
        previous_direction = previous_signal.get("signal_direction")
        current_direction = current_signal.get("signal_direction")
        if previous_direction != current_direction:
            return True

        previous_risk = str(previous_signal.get("risk_level") or "").lower()
        current_risk = str(current_signal.get("risk_level") or "").lower()
        if previous_risk in {"low", "medium"} and current_risk in {"high", "extreme"}:
            return True

        previous_score = _to_float(
            previous_signal.get("scores", {}).get("overall_signal_score")
        )
        current_score = _to_float(current_signal.get("scores", {}).get("overall_signal_score"))
        return abs(current_score - previous_score) >= 15


def _to_float(value: Any) -> float:
    try:
        if value is None:
            return 0.0
        return float(value)
    except (TypeError, ValueError):
        return 0.0
