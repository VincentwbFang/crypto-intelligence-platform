from datetime import datetime

from pydantic import BaseModel, Field

from app.core.config import settings


class MarketIngestRequest(BaseModel):
    exchange: str = settings.DEFAULT_EXCHANGE
    symbols: list[str] = Field(default_factory=lambda: settings.default_symbols_list)
    timeframe: str = settings.DEFAULT_TIMEFRAME
    limit: int = Field(default=settings.MARKET_DATA_LIMIT, ge=1, le=1000)


class MarketIngestResponse(BaseModel):
    exchange: str
    timeframe: str
    results: dict[str, int]


class OHLCVCandle(BaseModel):
    exchange: str
    symbol: str
    timeframe: str
    timestamp: datetime
    open: float
    high: float
    low: float
    close: float
    volume: float


class OHLCVResponse(BaseModel):
    symbol: str
    timeframe: str
    data: list[OHLCVCandle]


class MarketSnapshotResponse(BaseModel):
    symbol: str
    timeframe: str
    latest_close: float
    previous_close: float
    return_pct: float
    high: float
    low: float
    volume: float
    candle_count: int
    timestamp: datetime
