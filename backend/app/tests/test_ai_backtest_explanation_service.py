import json

from app.services.ai_backtest_explanation_service import (
    AI_BACKTEST_EXPLANATION_DISCLAIMER,
    AIBacktestExplanationService,
)


class FakeLLMClient:
    class chat:
        class completions:
            @staticmethod
            def create(**_: object) -> dict:
                return {
                    "choices": [
                        {
                            "message": {
                                "content": json.dumps(
                                    {
                                        "plain_english_summary": "The historical sample was mixed.",
                                        "performance_interpretation": ["Return was positive."],
                                        "risk_interpretation": ["Drawdown should be reviewed."],
                                        "strategy_behavior": ["The strategy was long-only."],
                                        "main_weaknesses": ["This will moon is unsafe wording."],
                                        "what_to_validate_next": ["Test another period."],
                                        "limitations": ["Stored OHLCV only."],
                                    }
                                )
                            }
                        }
                    ]
                }


def test_disabled_ai_returns_disabled_response() -> None:
    result = AIBacktestExplanationService(None, enabled=False).explain_backtest({})
    assert result["enabled"] is False


def test_mocked_deepseek_response_returns_structured_explanation() -> None:
    result = AIBacktestExplanationService(
        FakeLLMClient(),
        enabled=True,
        model="deepseek-v4-pro",
    ).explain_backtest({"metrics": {"total_return_pct": 1}})

    assert result["enabled"] is True
    assert result["disclaimer"] == AI_BACKTEST_EXPLANATION_DISCLAIMER
    text = json.dumps(result).lower()
    assert "will moon" not in text
    assert "compliance_warnings" in result
