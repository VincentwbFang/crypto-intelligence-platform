from __future__ import annotations

import re
from collections import Counter
from typing import Any

SYMBOL_KEYWORDS: dict[str, tuple[str, ...]] = {
    "BTC": ("bitcoin", "btc", "spot bitcoin etf", "microstrategy", "mining", "hashrate"),
    "ETH": ("ethereum", "eth", "staking", "layer 2", "l2", "vitalik"),
    "SOL": ("solana", "sol", "pump.fun", "pump fun"),
    "XRP": ("ripple", "xrp"),
    "BNB": ("bnb", "binance"),
    "DOGE": ("dogecoin", "doge"),
    "ADA": ("cardano", "ada"),
    "AVAX": ("avalanche", "avax"),
    "LINK": ("chainlink", "link"),
    "TON": ("toncoin", "ton"),
    "TRX": ("tron", "trx", "justin sun"),
    "SUI": ("sui",),
    "HYPE": ("hyperliquid", "hype"),
    "DOT": ("polkadot", "dot"),
    "LTC": ("litecoin", "ltc"),
    "BCH": ("bitcoin cash", "bch"),
    "UNI": ("uniswap", "uni"),
    "APT": ("aptos", "apt"),
    "ARB": ("arbitrum", "arb"),
    "OP": ("optimism", "op mainnet"),
    "NEAR": ("near protocol", "near"),
    "ATOM": ("cosmos", "atom"),
    "FIL": ("filecoin", "fil"),
    "INJ": ("injective", "inj"),
    "SEI": ("sei",),
}

SECTOR_KEYWORDS: dict[str, tuple[str, ...]] = {
    "ETF": ("etf", "exchange traded fund", "spot bitcoin etf", "spot ether etf", "flows"),
    "REGULATION": ("sec", "cftc", "regulation", "lawsuit", "settlement", "court", "policy"),
    "EXCHANGE": ("binance", "coinbase", "kraken", "okx", "bybit", "exchange outage"),
    "STABLECOIN": ("stablecoin", "usdt", "tether", "usdc", "circle", "depeg", "reserve"),
    "DEFI": ("defi", "dex", "lending protocol", "yield", "liquidity pool"),
    "LAYER2": ("layer 2", "l2", "rollup", "arbitrum", "optimism", "base"),
    "MEME": ("meme", "dogecoin", "shib", "pump.fun", "pepe"),
    "AI_CRYPTO": ("ai token", "depin", "artificial intelligence", "ai crypto"),
}


class NewsEntityExtractor:
    def extract(self, item: dict[str, Any]) -> dict[str, Any]:
        text = _normalize(
            " ".join(
                str(value or "")
                for value in (
                    item.get("title"),
                    item.get("summary_raw"),
                    item.get("content_raw"),
                    " ".join(item.get("symbols_hint") or []),
                )
            )
        )
        symbol_hits = _keyword_hits(text, SYMBOL_KEYWORDS)
        sector_hits = _keyword_hits(text, SECTOR_KEYWORDS)

        symbols = sorted(symbol_hits.keys(), key=lambda symbol: (-symbol_hits[symbol], symbol))
        sectors = sorted(sector_hits.keys(), key=lambda sector: (-sector_hits[sector], sector))
        main_symbol = symbols[0] if symbols else None
        total_hits = sum(symbol_hits.values()) + sum(sector_hits.values())
        confidence = min(1.0, 0.25 + total_hits * 0.12) if total_hits else 0.0

        return {
            "symbols": symbols,
            "sectors": sectors,
            "main_symbol": main_symbol,
            "confidence": round(confidence, 3),
        }


def _keyword_hits(text: str, mapping: dict[str, tuple[str, ...]]) -> Counter[str]:
    hits: Counter[str] = Counter()
    for key, keywords in mapping.items():
        for keyword in keywords:
            if _contains_keyword(text, keyword):
                hits[key] += 1
    return hits


def _contains_keyword(text: str, keyword: str) -> bool:
    normalized = _normalize(keyword)
    if len(normalized) <= 4 and normalized.isalpha():
        return re.search(rf"\b{re.escape(normalized)}\b", text) is not None
    return normalized in text


def _normalize(value: str) -> str:
    return re.sub(r"\s+", " ", value.lower()).strip()
