from app.services.news.entity_extractor import NewsEntityExtractor


def test_entity_extractor_detects_symbols_and_sectors() -> None:
    result = NewsEntityExtractor().extract(
        {
            "title": "SEC delays spot Bitcoin ETF decision while Ethereum staking debate grows",
            "summary_raw": "Coinbase and Binance are watching regulation closely.",
            "content_raw": None,
            "symbols_hint": [],
        }
    )

    assert "BTC" in result["symbols"]
    assert "ETH" in result["symbols"]
    assert "ETF" in result["sectors"]
    assert "REGULATION" in result["sectors"]
    assert "EXCHANGE" in result["sectors"]
    assert result["confidence"] > 0
