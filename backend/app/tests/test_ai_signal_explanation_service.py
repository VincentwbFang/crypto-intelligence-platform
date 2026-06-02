import json
from types import SimpleNamespace

from app.services.ai_signal_explanation_service import (
    AI_SIGNAL_EXPLANATION_DISCLAIMER,
    AISignalExplanationService,
)


SIGNAL = {
    "symbol": "SOL/USDT",
    "timeframe": "1h",
    "signal_direction": "bullish",
    "setup_type": "trend_continuation",
    "risk_level": "medium",
    "scores": {"overall_signal_score": 68.0},
    "risk_notes": ["Only OHLCV data was used."],
}


class FakeCompletions:
    def __init__(self, unsafe: bool = False) -> None:
        self.unsafe = unsafe

    def create(self, **kwargs: object) -> SimpleNamespace:
        explanation = {
            "enabled": True,
            "plain_english_summary": (
                "The deterministic signal shows positive trend conditions."
            ),
            "why_this_signal": ["Trend and momentum scores support the signal."],
            "main_risks": ["Risk can rise if volatility expands."],
            "what_to_monitor": ["Monitor follow-through volume."],
            "confidence_commentary": "Confidence is moderate, not certain.",
            "limitations": ["Only OHLCV-derived data is included."],
            "disclaimer": AI_SIGNAL_EXPLANATION_DISCLAIMER,
        }
        if self.unsafe:
            explanation["plain_english_summary"] = "Buy now, this is guaranteed."
        return SimpleNamespace(
            choices=[
                SimpleNamespace(
                    message=SimpleNamespace(content=json.dumps(explanation))
                )
            ]
        )


class FakeChat:
    def __init__(self, unsafe: bool = False) -> None:
        self.completions = FakeCompletions(unsafe=unsafe)


class FakeLLMClient:
    def __init__(self, unsafe: bool = False) -> None:
        self.chat = FakeChat(unsafe=unsafe)


def test_disabled_ai_returns_disabled_response() -> None:
    service = AISignalExplanationService(llm_client=None, enabled=False)

    result = service.explain_signal(SIGNAL)

    assert result == {
        "enabled": False,
        "message": "AI signal explanation is disabled.",
    }


def test_mocked_deepseek_response_returns_structured_explanation() -> None:
    service = AISignalExplanationService(
        llm_client=FakeLLMClient(),
        enabled=True,
        model="deepseek-v4-pro",
    )

    result = service.explain_signal(SIGNAL)

    assert result["enabled"] is True
    assert result["plain_english_summary"]
    assert result["disclaimer"] == AI_SIGNAL_EXPLANATION_DISCLAIMER


def test_ai_explanation_does_not_change_deterministic_signal_direction() -> None:
    signal = dict(SIGNAL)
    service = AISignalExplanationService(
        llm_client=FakeLLMClient(),
        enabled=True,
        model="deepseek-v4-pro",
    )

    service.explain_signal(signal)

    assert signal["signal_direction"] == "bullish"


def test_compliance_guardrail_removes_unsafe_language() -> None:
    service = AISignalExplanationService(
        llm_client=FakeLLMClient(unsafe=True),
        enabled=True,
        model="deepseek-v4-pro",
    )

    result = service.explain_signal(SIGNAL)
    output_text = json.dumps(result).lower()

    assert "buy now" not in output_text
    assert "guaranteed" not in output_text
    assert result["compliance_warnings"]


def test_final_ai_output_includes_disclaimer() -> None:
    service = AISignalExplanationService(
        llm_client=FakeLLMClient(),
        enabled=True,
        model="deepseek-v4-pro",
    )

    result = service.explain_signal(SIGNAL)

    assert result["disclaimer"] == AI_SIGNAL_EXPLANATION_DISCLAIMER
