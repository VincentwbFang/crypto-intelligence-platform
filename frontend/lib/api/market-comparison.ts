import { apiFetch } from "@/lib/api/client";
import type {
  RelativeStrengthAlert,
  RelativeStrengthAlertListResponse,
  RelativeStrengthHistoryResponse,
  RelativeStrengthRankingResponse,
  RelativeStrengthSnapshot
} from "@/lib/api/types";

export function getRelativeStrengthRanking(limit = 100): Promise<RelativeStrengthRankingResponse> {
  return apiFetch<RelativeStrengthRankingResponse>("/api/market-comparison/ranking", {
    query: { limit }
  });
}

export function getRelativeStrengthHistory(
  symbol: string,
  limit = 500
): Promise<RelativeStrengthHistoryResponse> {
  return apiFetch<RelativeStrengthHistoryResponse>(
    `/api/market-comparison/${encodeURIComponent(symbol)}`,
    {
      query: { limit }
    }
  );
}

export function listRelativeStrengthAlerts(
  limit = 20,
  unreadOnly = false
): Promise<RelativeStrengthAlertListResponse> {
  return apiFetch<RelativeStrengthAlertListResponse>("/api/alerts/relative-strength", {
    query: { limit, unread_only: unreadOnly }
  });
}

export function markRelativeStrengthAlertRead(alertId: number): Promise<RelativeStrengthAlert> {
  return apiFetch<RelativeStrengthAlert>(`/api/alerts/relative-strength/${alertId}/read`, {
    method: "POST"
  });
}

export type { RelativeStrengthAlert, RelativeStrengthSnapshot };
