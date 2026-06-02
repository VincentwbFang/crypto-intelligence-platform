import { apiFetch } from "@/lib/api/client";
import type {
  AIBacktestExplanation,
  BacktestDetail,
  BacktestRun,
  BacktestRunRequest,
  BacktestStrategyInfo,
  BacktestTrade,
  EquityCurvePoint
} from "@/lib/api/types";

export function listStrategies() {
  return apiFetch<{ data: BacktestStrategyInfo[] }>("/backtests/strategies");
}

export function runBacktest(request: BacktestRunRequest) {
  return apiFetch<BacktestDetail>("/backtests/run", {
    method: "POST",
    body: request,
    timeoutMs: 30000
  });
}

export function listBacktests(
  filters: {
    symbol?: string;
    strategy_name?: string;
    status?: string;
    limit?: number;
  } = {}
) {
  return apiFetch<{ data: BacktestRun[] }>("/backtests", { query: filters });
}

export function getBacktest(runId: string) {
  return apiFetch<BacktestDetail>(`/backtests/${runId}`);
}

export function getBacktestTrades(runId: string) {
  return apiFetch<{ run_id: string; data: BacktestTrade[] }>(
    `/backtests/${runId}/trades`
  );
}

export function getBacktestEquityCurve(runId: string) {
  return apiFetch<{ run_id: string; data: EquityCurvePoint[] }>(
    `/backtests/${runId}/equity-curve`
  );
}

export function explainBacktest(runId: string) {
  return apiFetch<AIBacktestExplanation>(`/backtests/${runId}/explain`);
}

export function deleteBacktest(runId: string) {
  return apiFetch<{ run_id: string; deleted: boolean }>(`/backtests/${runId}`, {
    method: "DELETE"
  });
}
