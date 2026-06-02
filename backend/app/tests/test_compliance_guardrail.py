import json

from app.services.compliance_guardrail import ComplianceGuardrail


FORBIDDEN_FINAL_PHRASES = (
    "buy now",
    "sell now",
    "short here",
    "long here",
    "use leverage",
    "5x leverage",
    "guaranteed",
    "risk-free",
    "moon",
    "all in",
    "price target",
)


def test_guardrail_detects_forbidden_phrases() -> None:
    output = {
        "trend_explanation": "Buy now because this will moon.",
        "risk_notes": ["This is guaranteed."],
    }

    result = ComplianceGuardrail.validate_ai_output(output)

    assert result["safe"] is False
    assert result["warnings"]


def test_guardrail_sanitizes_unsafe_output() -> None:
    output = {
        "trend_explanation": "Short here with a price target.",
        "paper_trade_example": {
            "risk_control": "Use leverage for sure profit."
        },
    }

    result = ComplianceGuardrail.validate_ai_output(output)
    sanitized_text = json.dumps(result["sanitized_output"]).lower()

    assert result["safe"] is False
    assert "[removed unsafe wording]" in sanitized_text
    assert "compliance_warnings" in result["sanitized_output"]


def test_guardrail_safe_output_passes_unchanged() -> None:
    output = {
        "trend_explanation": "Market bias appears mixed and needs confirmation.",
        "risk_notes": ["Only OHLCV data was used."],
    }

    result = ComplianceGuardrail.validate_ai_output(output)

    assert result == {
        "safe": True,
        "warnings": [],
        "sanitized_output": output,
    }


def test_sanitized_output_does_not_contain_forbidden_phrases() -> None:
    output = {
        "trend_explanation": "Buy now, sell now, long here, short here, all in.",
        "volume_explanation": "This is guaranteed and risk-free.",
        "volatility_explanation": "It will moon with a price target.",
        "paper_trade_example": {
            "risk_control": "Use leverage or 5x leverage."
        },
    }

    result = ComplianceGuardrail.validate_ai_output(output)
    sanitized_text = json.dumps(result["sanitized_output"]).lower()

    for phrase in FORBIDDEN_FINAL_PHRASES:
        assert phrase not in sanitized_text

