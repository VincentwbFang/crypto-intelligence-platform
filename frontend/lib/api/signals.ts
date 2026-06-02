import { apiFetch } from "@/lib/api/client";
import type { SignalRankResponse, SignalResponse } from "@/lib/api/types";

function encodeSymbol(symbol: string) {
  return encodeURIComponent(symbol);
}

export function getSignal(
  symbol: string,
  timeframe = "1h",
  limit = 200,
  includeAIExplanation = false
) {
  return apiFetch<SignalResponse>(`/signals/${encodeSymbol(symbol)}`, {
    query: {
      timeframe,
      limit,
      include_ai_explanation: includeAIExplanation
    }
  });
}

export function generateSignal(symbol: string, timeframe = "1h", limit = 200) {
  return apiFetch<SignalResponse>(`/signals/${encodeSymbol(symbol)}/generate`, {
    method: "POST",
    query: { timeframe, limit }
  });
}

export function getLatestSignal(symbol: string, timeframe = "1h") {
  return apiFetch<SignalResponse>(`/signals/${encodeSymbol(symbol)}/latest`, {
    query: { timeframe }
  });
}

export function rankSignals(symbols: string[], timeframe = "1h", limit = 200) {
  return apiFetch<SignalRankResponse>("/signals/rank", {
    query: { symbols: symbols.join(","), timeframe, limit }
  });
}
