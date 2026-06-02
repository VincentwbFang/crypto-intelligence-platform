import json

from app.services.ai_paper_trading_explanation_service import (
    AI_PAPER_TRADING_DISCLAIMER,
    AIPaperTradingExplanationService,
)


class FakeLLMClient:
    class Chat:
        class Completions:
            def create(self, **kwargs):  # noqa: ANN001
                return {
                    "choices": [
                        {
                            "message": {
                                "content": json.dumps(
                                    {
                                        "plain_english_summary": "The virtual account has limited simulated activity.",
                                        "performance_observations": ["Equity is close to initial balance."],
                                        "risk_observations": ["Position concentration should be monitored."],
                                        "position_notes": ["Only simulated positions are reviewed."],
                                        "what_to_monitor": ["Monitor drawdown and fees."],
                                        "limitations": ["Paper execution may differ from live execution."],
                                    }
                                )
                            }
                        }
                    ]
                }

        completions = Completions()

    chat = Chat()


def test_disabled_ai_returns_disabled_response() -> None:
    service = AIPaperTradingExplanationService(None, enabled=False, model="deepseek-v4-pro")

    assert service.explain_portfolio({}, {})["enabled"] is False


def test_mocked_llm_response_returns_structured_explanation() -> None:
    service = AIPaperTradingExplanationService(FakeLLMClient(), enabled=True, model="deepseek-v4-pro")

    result = service.explain_portfolio({"account": {}}, {"total_trades": 0})

    assert result["enabled"] is True
    assert result["disclaimer"] == AI_PAPER_TRADING_DISCLAIMER
    assert "guaranteed" not in json.dumps(result).lower()


def test_compliance_guardrail_sanitizes_unsafe_output() -> None:
    class UnsafeClient(FakeLLMClient):
        class Chat:
            class Completions:
                def create(self, **kwargs):  # noqa: ANN001
                    return {
                        "choices": [
                            {
                                "message": {
                                    "content": json.dumps(
                                        {
                                            "plain_english_summary": "This will moon.",
                                            "performance_observations": [],
                                            "risk_observations": [],
                                            "position_notes": [],
                                            "what_to_monitor": [],
                                            "limitations": [],
                                        }
                                    )
                                }
                            }
                        ]
                    }

            completions = Completions()

        chat = Chat()

    result = AIPaperTradingExplanationService(
        UnsafeClient(),
        enabled=True,
        model="deepseek-v4-pro",
    ).explain_order({"order_id": "test"})

    assert "will moon" not in json.dumps(result).lower()
    assert result["compliance_warnings"]
