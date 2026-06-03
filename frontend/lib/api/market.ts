import { apiFetch } from "@/lib/api/client";
import type {
  MarketBackfillRequest,
  MarketBackfillResponse,
  MarketIngestRequest,
  MarketIngestResponse,
  MarketSnapshot,
  MarketUniverseResponse,
  OHLCVResponse
} from "@/lib/api/types";

export function getMarketSnapshot(symbol: string, timeframe = "1h") {
  return apiFetch<MarketSnapshot>("/market/snapshot", {
    query: { symbol, timeframe }
  });
}

export function getOHLCV(symbol: string, timeframe = "1h", limit = 200) {
  return apiFetch<OHLCVResponse>("/market/ohlcv", {
    query: { symbol, timeframe, limit }
  });
}

export function ingestMarketData(request: MarketIngestRequest) {
  return apiFetch<MarketIngestResponse>("/market/ingest", {
    method: "POST",
    body: request
  });
}

export function getMarketUniverse(exchange = "okx", topN = 30) {
  return apiFetch<MarketUniverseResponse>("/market/universe", {
    query: { exchange, top_n: topN }
  });
}

export function backfillMarketData(request: MarketBackfillRequest) {
  return apiFetch<MarketBackfillResponse>("/market/backfill", {
    method: "POST",
    body: request
  });
}
