import { apiFetch } from "@/lib/api/client";
import type {
  MarketIngestRequest,
  MarketIngestResponse,
  MarketSnapshot,
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
