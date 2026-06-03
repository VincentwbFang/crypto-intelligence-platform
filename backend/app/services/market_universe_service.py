from __future__ import annotations

import logging
from typing import Any

import httpx

from app.core.config import settings
from app.data.exchanges.ccxt_client import CCXTMarketClient, MarketDataError

logger = logging.getLogger(__name__)


class MarketUniverseService:
    """Build a tradable major-coin universe from market-cap rank plus exchange support."""

    def __init__(
        self,
        exchange_id: str | None = None,
        market_client: CCXTMarketClient | None = None,
    ) -> None:
        self.exchange_id = exchange_id or settings.DEFAULT_EXCHANGE
        self.market_client = market_client or CCXTMarketClient(self.exchange_id)

    def get_top_market_symbols(self, top_n: int | None = None) -> dict[str, Any]:
        top_n = top_n or settings.MARKET_TOP_N
        markets = self.market_client.load_markets()
        candidates = self._coingecko_candidates(limit=max(top_n * 3, 60))
        source = "coingecko"
        if not candidates:
            candidates = self._fallback_candidates()
            source = "configured_fallback"

        selected: list[str] = []
        skipped: list[dict[str, str]] = []
        for candidate in candidates:
            base = candidate["symbol"].upper()
            if base in settings.market_exclude_symbols_set:
                skipped.append({"symbol": base, "reason": "excluded"})
                continue
            symbol = f"{base}/{settings.MARKET_BACKFILL_QUOTE}"
            if symbol not in markets:
                skipped.append({"symbol": symbol, "reason": "not_listed_on_exchange"})
                continue
            if symbol not in selected:
                selected.append(symbol)
            if len(selected) >= top_n:
                break

        if len(selected) < top_n:
            for symbol in settings.market_top_symbols_list:
                if symbol in selected:
                    continue
                if symbol in markets:
                    selected.append(symbol)
                else:
                    skipped.append({"symbol": symbol, "reason": "fallback_not_listed_on_exchange"})
                if len(selected) >= top_n:
                    break

        return {
            "exchange": self.exchange_id,
            "top_n": top_n,
            "quote": settings.MARKET_BACKFILL_QUOTE,
            "source": source,
            "symbols": selected,
            "skipped": skipped,
        }

    def _coingecko_candidates(self, limit: int) -> list[dict[str, Any]]:
        try:
            with httpx.Client(timeout=10.0) as client:
                response = client.get(
                    settings.COINGECKO_MARKETS_URL,
                    params={
                        "vs_currency": "usd",
                        "order": "market_cap_desc",
                        "per_page": min(max(limit, 1), 250),
                        "page": 1,
                        "sparkline": "false",
                    },
                    headers={"accept": "application/json"},
                )
                response.raise_for_status()
                payload = response.json()
            if not isinstance(payload, list):
                return []
            return [
                {
                    "id": item.get("id"),
                    "symbol": str(item.get("symbol", "")).upper(),
                    "name": item.get("name"),
                    "market_cap_rank": item.get("market_cap_rank"),
                }
                for item in payload
                if item.get("symbol")
            ]
        except Exception:
            logger.exception("Failed to load CoinGecko market-cap universe; using fallback")
            return []

    def _fallback_candidates(self) -> list[dict[str, Any]]:
        return [
            {
                "id": symbol.split("/")[0].lower(),
                "symbol": symbol.split("/")[0].upper(),
                "name": symbol,
                "market_cap_rank": index + 1,
            }
            for index, symbol in enumerate(settings.market_top_symbols_list)
        ]


def get_top_market_symbols(exchange_id: str | None = None, top_n: int | None = None) -> dict[str, Any]:
    try:
        return MarketUniverseService(exchange_id=exchange_id).get_top_market_symbols(top_n=top_n)
    except MarketDataError:
        raise
