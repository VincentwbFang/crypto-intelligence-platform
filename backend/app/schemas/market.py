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


class MarketBackfillRequest(BaseModel):
    exchange: str = settings.DEFAULT_EXCHANGE
    symbols: list[str] | None = None
    use_top_market_cap: bool = True
    top_n: int = Field(default=settings.MARKET_TOP_N, ge=1, le=100)
    timeframe: str = settings.MARKET_BACKFILL_TIMEFRAME
    years: int = Field(default=settings.MARKET_BACKFILL_YEARS, ge=1, le=10)
    batch_limit: int = Field(default=settings.MARKET_BACKFILL_BATCH_LIMIT, ge=50, le=1000)
    max_batches_per_symbol: int | None = Field(default=None, ge=1)


class MarketBackfillResponse(BaseModel):
    exchange: str
    timeframe: str
    years: int
    symbols: list[str]
    skipped: list[dict[str, str]] = Field(default_factory=list)
    results: dict[str, dict]


class MarketUniverseResponse(BaseModel):
    exchange: str
    top_n: int
    quote: str
    source: str
    symbols: list[str]
    skipped: list[dict[str, str]]


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
