import json
from types import SimpleNamespace

from app.services.ai_signal_service import AISignalService, COMPLIANCE_DISCLAIMER


SNAPSHOT = {
    "symbol": "BTC/USDT",
    "timeframe": "1h",
    "latest_close": 68000.0,
    "previous_close": 67500.0,
    "return_pct": 0.7407,
    "high": 68100.0,
    "low": 67000.0,
    "volume": 12345.67,
    "candle_count": 200,
    "timestamp": "2026-05-27T12:00:00Z",
}
RECENT_CANDLES = [
    {
        "symbol": "BTC/USDT",
        "timeframe": "1h",
        "timestamp": "2026-05-27T11:00:00Z",
        "open": 67500.0,
        "high": 67900.0,
        "low": 67400.0,
        "close": 67500.0,
        "volume": 12000.0,
    }
]


class FakeResponses:
    def create(self, **kwargs: object) -> SimpleNamespace:
        summary = {
            "enabled": True,
            "symbol": "BTC/USDT",
            "timeframe": "1h",
            "market_bias": "bullish",
            "setup_type": "breakout_watch",
            "confidence_score": 67,
            "risk_level": "medium",
            "trend_explanation": (
                "BTC is above the prior close, suggesting short-term positive momentum."
            ),
            "volume_explanation": "Volume confirmation remains moderate.",
            "volatility_explanation": "The latest candle range is wider than recent candles.",
            "invalidation_conditions": [
                "The framework weakens if price falls back below the recent range."
            ],
            "watch_zones": ["Recent high area", "Recent support range"],
            "risk_notes": [
                "Only OHLCV data was used.",
                "No order book, funding rate, or open interest data is included yet.",
            ],
            "paper_trade_example": {
                "enabled": True,
                "scenario": "Research-only breakout monitoring example.",
                "entry_condition": (
                    "Monitor whether price closes above the recent high with stronger volume."
                ),
                "invalidation_condition": (
                    "The research setup is invalidated if price closes back below the recent range."
                ),
                "risk_control": (
                    "Use predefined position sizing and maximum loss limits in paper trading only."
                ),
            },
            "compliance_disclaimer": COMPLIANCE_DISCLAIMER,
        }
        return SimpleNamespace(output_text=json.dumps(summary))


class FakeCompletions:
    def create(self, **kwargs: object) -> SimpleNamespace:
        summary = {
            "enabled": True,
            "symbol": "BTC/USDT",
            "timeframe": "1h",
            "market_bias": "bullish",
            "setup_type": "breakout_watch",
            "confidence_score": 67,
            "risk_level": "medium",
            "trend_explanation": (
                "BTC is above the prior close, suggesting short-term positive momentum."
            ),
            "volume_explanation": "Volume confirmation remains moderate.",
            "volatility_explanation": "The latest candle range is wider than recent candles.",
            "invalidation_conditions": [
                "The framework weakens if price falls back below the recent range."
            ],
            "watch_zones": ["Recent high area", "Recent support range"],
            "risk_notes": [
                "Only OHLCV data was used.",
                "No order book, funding rate, or open interest data is included yet.",
            ],
            "paper_trade_example": {
                "enabled": True,
                "scenario": "Research-only breakout monitoring example.",
                "entry_condition": (
                    "Monitor whether price closes above the recent high with stronger volume."
                ),
                "invalidation_condition": (
                    "The research setup is invalidated if price closes back below the recent range."
                ),
                "risk_control": (
                    "Use predefined position sizing and maximum loss limits in paper trading only."
                ),
            },
            "compliance_disclaimer": COMPLIANCE_DISCLAIMER,
        }
        return SimpleNamespace(
            choices=[
                SimpleNamespace(
                    message=SimpleNamespace(content=json.dumps(summary))
                )
            ]
        )


class FakeChat:
    completions = FakeCompletions()


class FakeOpenAIClient:
    chat = FakeChat()
    responses = FakeResponses()


def make_service(
    enabled: bool = True,
    paper_trade_suggestions_enabled: bool = False,
) -> AISignalService:
    return AISignalService(
        api_key="test-key",
        model="test-model",
        enabled=enabled,
        actionable_mode=True,
        paper_trade_suggestions_enabled=paper_trade_suggestions_enabled,
        client=FakeOpenAIClient(),
    )


def test_ai_signal_summary_disabled_returns_safe_response() -> None:
    service = AISignalService(
        api_key=None,
        model="test-model",
        enabled=False,
        actionable_mode=False,
        paper_trade_suggestions_enabled=False,
    )

    result = service.generate_signal_summary(SNAPSHOT, RECENT_CANDLES)

    assert result == {
        "enabled": False,
        "message": "AI signal summary is disabled.",
    }


def test_ai_signal_summary_missing_api_key_returns_safe_error() -> None:
    service = AISignalService(
        api_key=None,
        model="test-model",
        enabled=True,
        actionable_mode=False,
        paper_trade_suggestions_enabled=False,
        api_key_name="DEEPSEEK_API_KEY",
    )

    result = service.generate_signal_summary(SNAPSHOT, RECENT_CANDLES)

    assert result["enabled"] is True
    assert result["error"] == "DEEPSEEK_API_KEY is not configured."


def test_ai_signal_summary_returns_mocked_structured_response() -> None:
    service = make_service(paper_trade_suggestions_enabled=True)

    result = service.generate_signal_summary(SNAPSHOT, RECENT_CANDLES)

    assert result["enabled"] is True
    assert result["symbol"] == "BTC/USDT"
    assert result["timeframe"] == "1h"
    assert result["market_bias"] == "bullish"
    assert result["setup_type"] == "breakout_watch"
    assert result["confidence_score"] == 67
    assert result["risk_level"] == "medium"


def test_paper_trade_example_is_disabled_when_setting_is_false() -> None:
    service = make_service(paper_trade_suggestions_enabled=False)

    result = service.generate_signal_summary(SNAPSHOT, RECENT_CANDLES)

    assert result["paper_trade_example"] == {
        "enabled": False,
        "scenario": None,
        "entry_condition": None,
        "invalidation_condition": None,
        "risk_control": None,
    }


def test_paper_trade_example_is_enabled_only_when_setting_is_true() -> None:
    service = make_service(paper_trade_suggestions_enabled=True)

    result = service.generate_signal_summary(SNAPSHOT, RECENT_CANDLES)

    assert result["paper_trade_example"]["enabled"] is True
    assert "Research-only" in result["paper_trade_example"]["scenario"]


def test_output_includes_compliance_disclaimer() -> None:
    service = make_service(paper_trade_suggestions_enabled=True)

    result = service.generate_signal_summary(SNAPSHOT, RECENT_CANDLES)

    assert result["compliance_disclaimer"] == COMPLIANCE_DISCLAIMER
