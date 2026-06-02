import json
import logging
from typing import Any

from app.services.compliance_guardrail import ComplianceGuardrail

logger = logging.getLogger(__name__)

AI_SIGNAL_EXPLANATION_DISCLAIMER = (
    "This is a data-driven signal explanation for educational and research "
    "purposes only. It is not personalized financial advice."
)


class AISignalExplanationService:
    def __init__(
        self,
        llm_client: Any | None,
        enabled: bool,
        model: str | None = None,
    ) -> None:
        self.llm_client = llm_client
        self.enabled = enabled
        self.model = model

    def explain_signal(self, signal: dict[str, Any]) -> dict[str, Any]:
        if not self.enabled:
            return {
                "enabled": False,
                "message": "AI signal explanation is disabled.",
            }
        if self.llm_client is None or self.model is None:
            return {
                "enabled": True,
                "error": "LLM client is not configured.",
                "message": "Set DEEPSEEK_API_KEY to generate AI signal explanations.",
            }

        try:
            response = self.llm_client.chat.completions.create(
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
                                "deterministic_signal": signal,
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
            logger.exception("Failed to generate AI signal explanation")
            return {
                "enabled": True,
                "error": "AI signal explanation generation failed.",
                "message": "The deterministic signal is still available.",
            }

    def _system_prompt(self) -> str:
        return (
            "Explain only the deterministic signal JSON provided by the system. "
            "Do not invent news, fundamentals, external catalysts, or price "
            "targets. Do not recommend buying, selling, shorting, longing, or "
            "leverage. Do not override scores or change signal direction. Explain "
            "uncertainty clearly; if risk_level is high or extreme, emphasize risk. "
            "Return only JSON matching the provided schema."
        )

    def _explanation_schema(self) -> dict[str, Any]:
        return {
            "enabled": True,
            "plain_english_summary": "string",
            "why_this_signal": ["string"],
            "main_risks": ["string"],
            "what_to_monitor": ["string"],
            "confidence_commentary": "string",
            "limitations": ["string"],
            "disclaimer": AI_SIGNAL_EXPLANATION_DISCLAIMER,
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
                or "The deterministic signal was generated from stored OHLCV data."
            ),
            "why_this_signal": self._string_list(explanation.get("why_this_signal")),
            "main_risks": self._string_list(explanation.get("main_risks")),
            "what_to_monitor": self._string_list(explanation.get("what_to_monitor")),
            "confidence_commentary": str(
                explanation.get("confidence_commentary")
                or "Confidence should be interpreted together with risk level and data quality."
            ),
            "limitations": self._string_list(explanation.get("limitations")),
            "disclaimer": AI_SIGNAL_EXPLANATION_DISCLAIMER,
        }

    def _string_list(self, value: Any) -> list[str]:
        if not isinstance(value, list):
            return []
        return [str(item) for item in value if str(item).strip()]

