from __future__ import annotations

import json
import logging
from typing import Any

from app.services.compliance_guardrail import ComplianceGuardrail

logger = logging.getLogger(__name__)

AI_PAPER_TRADING_DISCLAIMER = (
    "This is a research-only explanation of simulated paper trading activity. "
    "It is not personalized financial advice and no real order was placed."
)


class AIPaperTradingExplanationService:
    def __init__(
        self,
        llm_client: Any | None,
        enabled: bool,
        model: str | None = None,
    ) -> None:
        self.llm_client = llm_client
        self.enabled = enabled
        self.model = model

    def explain_portfolio(self, portfolio: dict[str, Any], performance: dict[str, Any]) -> dict[str, Any]:
        return self._explain({"portfolio": portfolio, "performance": performance})

    def explain_order(self, order: dict[str, Any]) -> dict[str, Any]:
        return self._explain({"order": order})

    def _explain(self, payload: dict[str, Any]) -> dict[str, Any]:
        if not self.enabled:
            return {"enabled": False, "message": "AI paper trading explanation is disabled."}
        if self.llm_client is None or self.model is None:
            return {
                "enabled": True,
                "error": "LLM client is not configured.",
                "message": "Set DEEPSEEK_API_KEY to generate AI paper trading explanations.",
            }
        try:
            response = self.llm_client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self._system_prompt()},
                    {
                        "role": "user",
                        "content": json.dumps(
                            {
                                "paper_trading_payload": payload,
                                "required_json_schema": self._schema(),
                            },
                            default=str,
                        ),
                    },
                ],
                response_format={"type": "json_object"},
                temperature=0.2,
            )
            normalized = self._normalize(json.loads(self._extract_response_text(response)))
            return ComplianceGuardrail.validate_ai_output(normalized)["sanitized_output"]
        except Exception:
            logger.exception("Failed to generate AI paper trading explanation")
            return {
                "enabled": True,
                "error": "AI paper trading explanation generation failed.",
                "message": "The simulated paper trading data is still available.",
            }

    def _system_prompt(self) -> str:
        return (
            "Explain only the provided simulated paper trading JSON. Do not invent "
            "external news or specific future levels. Do not recommend real trading, "
            "shorting, longing, or leverage. Do not claim the simulated activity will "
            "work in live markets. Mention that simulated execution can differ from "
            "live execution. Return only JSON."
        )

    def _schema(self) -> dict[str, Any]:
        return {
            "enabled": True,
            "plain_english_summary": "string",
            "performance_observations": ["string"],
            "risk_observations": ["string"],
            "position_notes": ["string"],
            "what_to_monitor": ["string"],
            "limitations": ["string"],
            "disclaimer": AI_PAPER_TRADING_DISCLAIMER,
        }

    def _normalize(self, data: dict[str, Any]) -> dict[str, Any]:
        return {
            "enabled": True,
            "plain_english_summary": str(data.get("plain_english_summary") or ""),
            "performance_observations": self._string_list(data.get("performance_observations")),
            "risk_observations": self._string_list(data.get("risk_observations")),
            "position_notes": self._string_list(data.get("position_notes")),
            "what_to_monitor": self._string_list(data.get("what_to_monitor")),
            "limitations": self._string_list(data.get("limitations")),
            "disclaimer": AI_PAPER_TRADING_DISCLAIMER,
        }

    def _extract_response_text(self, response: Any) -> str:
        choices = response.get("choices") if isinstance(response, dict) else getattr(response, "choices", None)
        if choices:
            choice = choices[0]
            message = choice.get("message") if isinstance(choice, dict) else getattr(choice, "message", None)
            content = message.get("content") if isinstance(message, dict) else getattr(message, "content", None)
            if content:
                return str(content)
        raise ValueError("LLM response did not include output text.")

    def _string_list(self, value: Any) -> list[str]:
        if not isinstance(value, list):
            return []
        return [str(item) for item in value if str(item).strip()]
