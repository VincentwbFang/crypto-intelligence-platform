from __future__ import annotations

import json
import logging
from typing import Any

from openai import OpenAI

from app.core.config import settings
from app.services.compliance_guardrail import ComplianceGuardrail

logger = logging.getLogger(__name__)


class DeepSeekService:
    """Small OpenAI-compatible DeepSeek wrapper for on-demand JSON explanations."""

    def __init__(
        self,
        api_key: str | None = None,
        base_url: str | None = None,
        model: str | None = None,
        enabled: bool = True,
        client: Any | None = None,
    ) -> None:
        self.api_key = api_key if api_key is not None else settings.DEEPSEEK_API_KEY
        self.base_url = base_url or settings.DEEPSEEK_BASE_URL
        self.model = model or settings.deepseek_model_name
        self.enabled = enabled
        self.client = client

    def generate_json(
        self,
        *,
        system_prompt: str,
        payload: dict[str, Any],
        temperature: float = 0.2,
        apply_guardrail: bool = True,
    ) -> dict[str, Any]:
        if not self.enabled:
            return {"enabled": False, "message": "DeepSeek generation is disabled."}
        if not self.api_key and self.client is None:
            return {
                "enabled": True,
                "error": "DEEPSEEK_API_KEY is not configured.",
                "message": "Set DEEPSEEK_API_KEY to generate on-demand explanations.",
            }

        try:
            client = self.client or OpenAI(api_key=self.api_key, base_url=self.base_url)
            response = client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": json.dumps(payload, default=str)},
                ],
                response_format={"type": "json_object"},
                temperature=temperature,
            )
            output = json.loads(self._extract_response_text(response))
            if apply_guardrail:
                return ComplianceGuardrail.validate_ai_output(output)["sanitized_output"]
            return output
        except Exception:
            logger.exception("DeepSeek JSON generation failed")
            return {
                "enabled": True,
                "error": "DeepSeek generation failed.",
                "message": "The deterministic platform output remains available.",
            }

    @staticmethod
    def _extract_response_text(response: Any) -> str:
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
        if isinstance(response, dict) and response.get("output_text"):
            return str(response["output_text"])

        raise ValueError("DeepSeek response did not include output text.")
