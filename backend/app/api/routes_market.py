from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.auth.dependencies import require_auth_if_enabled
from app.core.config import settings
from app.data.exchanges.ccxt_client import MarketDataError, CCXTMarketClient
from app.data.ingestion.ohlcv_ingestor import OHLCVIngestor
from app.db.session import get_db
from app.observability.metrics import track_feature_event
from app.observability.tracing import trace_span
from app.schemas.market import (
    MarketIngestRequest,
    MarketIngestResponse,
    MarketSnapshotResponse,
    OHLCVResponse,
)
from app.services.market_service import MarketService

router = APIRouter(tags=["market"], dependencies=[Depends(require_auth_if_enabled)])


@router.post("/ingest", response_model=MarketIngestResponse)
def ingest_market_data(
    request: MarketIngestRequest,
    db: Session = Depends(get_db),
) -> MarketIngestResponse:
    try:
        with trace_span("market_ingestion"):
            market_client = CCXTMarketClient(request.exchange)
            ingestor = OHLCVIngestor(db_session=db, market_client=market_client)
            results = ingestor.ingest_many(
                symbols=request.symbols,
                timeframe=request.timeframe,
                limit=request.limit,
            )
        track_feature_event("market_ingestion")
    except MarketDataError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc

    return MarketIngestResponse(
        exchange=request.exchange,
        timeframe=request.timeframe,
        results=results,
    )


@router.get("/ohlcv", response_model=OHLCVResponse)
def get_ohlcv(
    symbol: str = Query(...),
    timeframe: str = Query(default=settings.DEFAULT_TIMEFRAME),
    limit: int = Query(default=settings.MARKET_DATA_LIMIT, ge=1, le=1000),
    db: Session = Depends(get_db),
) -> OHLCVResponse:
    market_service = MarketService(db)
    data = market_service.get_ohlcv(symbol=symbol, timeframe=timeframe, limit=limit)
    return OHLCVResponse(symbol=symbol, timeframe=timeframe, data=data)


@router.get("/snapshot", response_model=MarketSnapshotResponse)
def get_market_snapshot(
    symbol: str = Query(...),
    timeframe: str = Query(default=settings.DEFAULT_TIMEFRAME),
    db: Session = Depends(get_db),
) -> MarketSnapshotResponse:
    market_service = MarketService(db)
    try:
        snapshot = market_service.get_latest_market_snapshot(
            symbol=symbol,
            timeframe=timeframe,
            limit=settings.MARKET_DATA_LIMIT,
        )
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    return MarketSnapshotResponse(**snapshot)
