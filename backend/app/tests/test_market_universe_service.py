from app.services.market_universe_service import MarketUniverseService


class FakeMarketClient:
    exchange_id = "okx"

    def __init__(self, markets: list[str]) -> None:
        self.markets = markets

    def load_markets(self) -> dict[str, dict]:
        return {symbol: {} for symbol in self.markets}


def test_market_universe_filters_excluded_and_unlisted_symbols() -> None:
    service = MarketUniverseService(
        exchange_id="okx",
        market_client=FakeMarketClient(["BTC/USDT", "ETH/USDT", "SOL/USDT"]),
    )
    service._coingecko_candidates = lambda limit: [  # type: ignore[method-assign]
        {"symbol": "btc"},
        {"symbol": "usdt"},
        {"symbol": "missing"},
        {"symbol": "eth"},
        {"symbol": "sol"},
    ]

    universe = service.get_top_market_symbols(top_n=3)

    assert universe["source"] == "coingecko"
    assert universe["symbols"] == ["BTC/USDT", "ETH/USDT", "SOL/USDT"]
    assert {"symbol": "USDT", "reason": "excluded"} in universe["skipped"]
    assert {"symbol": "MISSING/USDT", "reason": "not_listed_on_exchange"} in universe["skipped"]


def test_market_universe_uses_configured_fallback_when_coingecko_fails() -> None:
    service = MarketUniverseService(
        exchange_id="okx",
        market_client=FakeMarketClient(["BTC/USDT", "ETH/USDT", "BNB/USDT"]),
    )
    service._coingecko_candidates = lambda limit: []  # type: ignore[method-assign]

    universe = service.get_top_market_symbols(top_n=3)

    assert universe["source"] == "configured_fallback"
    assert universe["symbols"] == ["BTC/USDT", "ETH/USDT", "BNB/USDT"]
