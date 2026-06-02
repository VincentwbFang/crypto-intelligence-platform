from __future__ import annotations

import json
import logging
from typing import Any

from app.services.compliance_guardrail import ComplianceGuardrail

logger = logging.getLogger(__name__)

AI_BACKTEST_EXPLANATION_DISCLAIMER = (
    "This is a research-only explanation of historical backtest results. "
    "It is not personalized financial advice and does not guarantee future performance."
)


class AIBacktestExplanationService:
    def __init__(
        self,
        llm_client: Any | None,
        enabled: bool,
        model: str | None = None,
    ) -> None:
        self.llm_client = llm_client
        self.enabled = enabled
        self.model = model

    def explain_backtest(self, backtest_result: dict[str, Any]) -> dict[str, Any]:
        if not self.enabled:
            return {
                "enabled": False,
                "message": "AI backtest explanation is disabled.",
            }
        if self.llm_client is None or self.model is None:
            return {
                "enabled": True,
                "error": "LLM client is not configured.",
                "message": "Set DEEPSEEK_API_KEY to generate AI backtest explanations.",
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
                                "backtest_result": backtest_result,
                                "required_json_schema": self._explanation_schema(),
                            },
                            default=str,
                        ),
                    },
                ],
                response_format={"type": "json_object"},
                temperature=0.2,
            )
            explanation = json.loads(self._extract_response_text(response))
            normalized = self._normalize_explanation(explanation)
            guardrail = ComplianceGuardrail.validate_ai_output(normalized)
            return guardrail["sanitized_output"]
        except Exception:
            logger.exception("Failed to generate AI backtest explanation")
            return {
                "enabled": True,
                "error": "AI backtest explanation generation failed.",
                "message": "The deterministic backtest result is still available.",
            }

    def _system_prompt(self) -> str:
        return (
            "Explain only the provided historical backtest JSON. Do not invent "
            "trades, news, external catalysts, or specific future levels. Do not recommend "
            "buying, selling, shorting, longing, or leverage. Do not claim future "
            "profitability. Emphasize that backtests are hypothetical and mention "
            "fees, slippage, and sample-period limitations. Return only JSON."
        )

    def _explanation_schema(self) -> dict[str, Any]:
        return {
            "enabled": True,
            "plain_english_summary": "string",
            "performance_interpretation": ["string"],
            "risk_interpretation": ["string"],
            "strategy_behavior": ["string"],
            "main_weaknesses": ["string"],
            "what_to_validate_next": ["string"],
            "limitations": ["string"],
            "disclaimer": AI_BACKTEST_EXPLANATION_DISCLAIMER,
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
        raise ValueError("LLM response did not include output text.")

    def _normalize_explanation(self, explanation: dict[str, Any]) -> dict[str, Any]:
        return {
            "enabled": True,
            "plain_english_summary": str(
                explanation.get("plain_english_summary")
                or "The backtest was evaluated from stored OHLCV data."
            ),
            "performance_interpretation": self._string_list(
                explanation.get("performance_interpretation")
            ),
            "risk_interpretation": self._string_list(explanation.get("risk_interpretation")),
            "strategy_behavior": self._string_list(explanation.get("strategy_behavior")),
            "main_weaknesses": self._string_list(explanation.get("main_weaknesses")),
            "what_to_validate_next": self._string_list(explanation.get("what_to_validate_next")),
            "limitations": self._string_list(explanation.get("limitations")),
            "disclaimer": AI_BACKTEST_EXPLANATION_DISCLAIMER,
        }

    def _string_list(self, value: Any) -> list[str]:
        if not isinstance(value, list):
            return []
        return [str(item) for item in value if str(item).strip()]
