import json
from types import SimpleNamespace

from app.services.ai_alert_explanation_service import (
    AI_ALERT_EXPLANATION_DISCLAIMER,
    AIAlertExplanationService,
)


ALERT = {
    "id": 1,
    "symbol": "SOL/USDT",
    "timeframe": "1h",
    "alert_type": "high_risk",
    "severity": "high",
    "title": "Elevated risk detected",
    "message": "Volatility risk increased for research monitoring.",
    "risk_level": "high",
    "signal_score": 64.0,
}


class FakeCompletions:
    def __init__(self, unsafe: bool = False) -> None:
        self.unsafe = unsafe

    def create(self, **kwargs: object) -> SimpleNamespace:
        explanation = {
            "enabled": True,
            "plain_english_summary": "The alert was triggered by elevated risk inputs.",
            "why_triggered": ["The deterministic alert rule detected high risk."],
            "risk_context": ["Volatility conditions require careful monitoring."],
            "what_to_monitor": ["Monitor whether risk scores cool down."],
            "limitations": ["Only the stored alert payload was used."],
            "disclaimer": AI_ALERT_EXPLANATION_DISCLAIMER,
        }
        if self.unsafe:
            explanation["plain_english_summary"] = "Buy now; this is guaranteed."
            explanation["what_to_monitor"] = ["Use leverage if momentum continues."]
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
    service = AIAlertExplanationService(llm_client=None, enabled=False)

    result = service.explain_alert(ALERT)

    assert result == {
        "enabled": False,
        "message": "AI alert explanation is disabled.",
    }


def test_mocked_deepseek_response_returns_structured_explanation() -> None:
    service = AIAlertExplanationService(
        llm_client=FakeLLMClient(),
        enabled=True,
        model="deepseek-v4-pro",
    )

    result = service.explain_alert(ALERT)

    assert result["enabled"] is True
    assert result["plain_english_summary"]
    assert result["disclaimer"] == AI_ALERT_EXPLANATION_DISCLAIMER


def test_ai_explanation_does_not_change_alert_severity() -> None:
    alert = dict(ALERT)
    service = AIAlertExplanationService(
        llm_client=FakeLLMClient(),
        enabled=True,
        model="deepseek-v4-pro",
    )

    service.explain_alert(alert)

    assert alert["severity"] == "high"


def test_ai_explanation_does_not_contain_forbidden_phrases() -> None:
    service = AIAlertExplanationService(
        llm_client=FakeLLMClient(unsafe=True),
        enabled=True,
        model="deepseek-v4-pro",
    )

    result = service.explain_alert(ALERT)
    output_text = json.dumps(result).lower()

    for phrase in ("buy now", "guaranteed", "use leverage"):
        assert phrase not in output_text


def test_compliance_guardrail_sanitizes_unsafe_output() -> None:
    service = AIAlertExplanationService(
        llm_client=FakeLLMClient(unsafe=True),
        enabled=True,
        model="deepseek-v4-pro",
    )

    result = service.explain_alert(ALERT)

    assert result["compliance_warnings"]


def test_disclaimer_is_included() -> None:
    service = AIAlertExplanationService(
        llm_client=FakeLLMClient(),
        enabled=True,
        model="deepseek-v4-pro",
    )

    result = service.explain_alert(ALERT)

    assert result["disclaimer"] == AI_ALERT_EXPLANATION_DISCLAIMER
