import json
import logging
from typing import Any

from openai import OpenAI

logger = logging.getLogger(__name__)

COMPLIANCE_DISCLAIMER = (
    "This is a data-driven signal summary for educational and research purposes "
    "only. It is not personalized financial advice."
)


class AISignalService:
    def __init__(
        self,
        api_key: str | None,
        model: str,
        enabled: bool,
        actionable_mode: bool,
        paper_trade_suggestions_enabled: bool,
        base_url: str | None = None,
        api_key_name: str = "DEEPSEEK_API_KEY",
        client: Any | None = None,
    ) -> None:
        self.api_key = api_key
        self.model = model
        self.enabled = enabled
        self.actionable_mode = actionable_mode
        self.paper_trade_suggestions_enabled = paper_trade_suggestions_enabled
        self.base_url = base_url
        self.api_key_name = api_key_name
        self.client = client

    def generate_signal_summary(
        self,
        snapshot: dict[str, Any],
        recent_candles: list[dict[str, Any]],
    ) -> dict[str, Any]:
        if not self.enabled:
            return {
                "enabled": False,
                "message": "AI signal summary is disabled.",
            }

        if not self.api_key:
            return {
                "enabled": True,
                "error": f"{self.api_key_name} is not configured.",
                "message": f"Set {self.api_key_name} to generate AI signal summaries.",
            }

        try:
            client = self.client or OpenAI(api_key=self.api_key, base_url=self.base_url)
            response = client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": self._system_prompt(),
                    },
                    {
                        "role": "user",
                        "content": json.dumps(
                            {
                                "snapshot": snapshot,
                                "recent_candles": recent_candles,
                                "actionable_mode": self.actionable_mode,
                                "paper_trade_suggestions_enabled": (
                                    self.paper_trade_suggestions_enabled
                                ),
                                "required_json_schema": self._signal_schema(),
                            },
                            default=str,
                        ),
                    },
                ],
                response_format={"type": "json_object"},
                temperature=0.2,
            )
            raw_summary = self._extract_response_text(response)
            summary = json.loads(raw_summary)
            return self._normalize_summary(summary=summary, snapshot=snapshot)
        except Exception:
            logger.exception("Failed to generate AI signal summary")
            return {
                "enabled": True,
                "error": "AI signal summary generation failed.",
                "message": "Market data remains available without AI signal output.",
            }

    def _system_prompt(self) -> str:
        return (
            "You generate a cautious, data-driven crypto signal framework using "
            "only the provided OHLCV snapshot and recent candles. Do not invent "
            "news, fundamentals, insider information, or external catalysts. Do "
            "not claim certainty or exact outcomes. Avoid unsafe certainty, "
            "reckless concentration, direct execution, or leverage language. "
            "If paper_trade_example is enabled, "
            "it must be clearly simulated and research-only. If data is "
            "insufficient, return low confidence. Return only JSON matching the "
            "provided schema."
        )

    def _signal_schema(self) -> dict[str, Any]:
        return {
            "type": "object",
            "additionalProperties": False,
            "required": [
                "enabled",
                "symbol",
                "timeframe",
                "market_bias",
                "setup_type",
                "confidence_score",
                "risk_level",
                "trend_explanation",
                "volume_explanation",
                "volatility_explanation",
                "invalidation_conditions",
                "watch_zones",
                "risk_notes",
                "paper_trade_example",
                "compliance_disclaimer",
            ],
            "properties": {
                "enabled": {"type": "boolean"},
                "symbol": {"type": "string"},
                "timeframe": {"type": "string"},
                "market_bias": {
                    "type": "string",
                    "enum": ["bullish", "bearish", "neutral", "mixed"],
                },
                "setup_type": {"type": "string"},
                "confidence_score": {"type": "number"},
                "risk_level": {
                    "type": "string",
                    "enum": ["low", "medium", "high", "extreme"],
                },
                "trend_explanation": {"type": "string"},
                "volume_explanation": {"type": "string"},
                "volatility_explanation": {"type": "string"},
                "invalidation_conditions": {
                    "type": "array",
                    "items": {"type": "string"},
                },
                "watch_zones": {"type": "array", "items": {"type": "string"}},
                "risk_notes": {"type": "array", "items": {"type": "string"}},
                "paper_trade_example": {
                    "type": "object",
                    "additionalProperties": False,
                    "required": [
                        "enabled",
                        "scenario",
                        "entry_condition",
                        "invalidation_condition",
                        "risk_control",
                    ],
                    "properties": {
                        "enabled": {"type": "boolean"},
                        "scenario": {"type": ["string", "null"]},
                        "entry_condition": {"type": ["string", "null"]},
                        "invalidation_condition": {"type": ["string", "null"]},
                        "risk_control": {"type": ["string", "null"]},
                    },
                },
                "compliance_disclaimer": {"type": "string"},
            },
        }

    def _extract_response_text(self, response: Any) -> str:
        choices = (
            response.get("choices")
            if isinstance(response, dict)
            else getattr(response, "choices", None)
        )
        if choices:
            choice = choices[0]
            message = (
                choice.get("message")
                if isinstance(choice, dict)
                else getattr(choice, "message", None)
            )
            content = (
                message.get("content")
                if isinstance(message, dict)
                else getattr(message, "content", None)
            )
            if content:
                return str(content)

        output_text = getattr(response, "output_text", None)
        if output_text:
            return str(output_text)

        if isinstance(response, dict):
            if response.get("output_text"):
                return str(response["output_text"])
            output = response.get("output", [])
        else:
            output = getattr(response, "output", [])

        for item in output:
            content = (
                item.get("content", [])
                if isinstance(item, dict)
                else getattr(item, "content", [])
            )
            for part in content:
                text = (
                    part.get("text")
                    if isinstance(part, dict)
                    else getattr(part, "text", None)
                )
                if text:
                    return str(text)

        raise ValueError("OpenAI response did not include output text.")

    def _normalize_summary(
        self,
        summary: dict[str, Any],
        snapshot: dict[str, Any],
    ) -> dict[str, Any]:
        normalized = {
            "enabled": True,
            "symbol": str(summary.get("symbol") or snapshot.get("symbol") or ""),
            "timeframe": str(summary.get("timeframe") or snapshot.get("timeframe") or ""),
            "market_bias": self._choice(
                summary.get("market_bias"),
                {"bullish", "bearish", "neutral", "mixed"},
                "mixed",
            ),
            "setup_type": str(summary.get("setup_type") or "observation_only"),
            "confidence_score": self._confidence_score(summary.get("confidence_score")),
            "risk_level": self._choice(
                summary.get("risk_level"),
                {"low", "medium", "high", "extreme"},
                "medium",
            ),
            "trend_explanation": str(
                summary.get("trend_explanation")
                or "Recent candles show mixed near-term movement."
            ),
            "volume_explanation": str(
                summary.get("volume_explanation")
                or "Volume should be compared with additional recent candles."
            ),
            "volatility_explanation": str(
                summary.get("volatility_explanation")
                or "Volatility cannot be fully assessed from limited data."
            ),
            "invalidation_conditions": self._string_list(
                summary.get("invalidation_conditions")
            ),
            "watch_zones": self._string_list(summary.get("watch_zones")),
            "risk_notes": self._string_list(summary.get("risk_notes")),
            "paper_trade_example": self._paper_trade_example(
                summary.get("paper_trade_example")
            ),
            "compliance_disclaimer": COMPLIANCE_DISCLAIMER,
        }

        if not self.actionable_mode:
            normalized["setup_type"] = "observation_only"

        if not normalized["invalidation_conditions"]:
            normalized["invalidation_conditions"] = [
                "The signal framework weakens if future candles reverse the latest close range."
            ]
        if not normalized["watch_zones"]:
            normalized["watch_zones"] = ["Recent high area", "Recent support range"]
        if not normalized["risk_notes"]:
            normalized["risk_notes"] = [
                "Only OHLCV data was used.",
                "No order book, funding rate, or open interest data is included yet.",
            ]

        return normalized

    def _choice(self, value: Any, allowed: set[str], fallback: str) -> str:
        normalized = str(value or "").lower()
        return normalized if normalized in allowed else fallback

    def _confidence_score(self, value: Any) -> float:
        try:
            score = float(value)
        except (TypeError, ValueError):
            return 25.0
        return max(0.0, min(100.0, score))

    def _string_list(self, value: Any) -> list[str]:
        if not isinstance(value, list):
            return []
        return [str(item) for item in value if str(item).strip()]

    def _paper_trade_example(self, value: Any) -> dict[str, Any]:
        if not self.paper_trade_suggestions_enabled:
            return {
                "enabled": False,
                "scenario": None,
                "entry_condition": None,
                "invalidation_condition": None,
                "risk_control": None,
            }

        source = value if isinstance(value, dict) else {}
        return {
            "enabled": True,
            "scenario": str(
                source.get("scenario")
                or "Research-only simulated setup monitoring example."
            ),
            "entry_condition": str(
                source.get("entry_condition")
                or "Monitor whether the market confirms the setup with future candles."
            ),
            "invalidation_condition": str(
                source.get("invalidation_condition")
                or "The simulated setup is invalidated if price closes back below the recent range."
            ),
            "risk_control": str(
                source.get("risk_control")
                or "Use predefined position sizing and maximum loss limits in paper trading only."
            ),
        }
