import { apiFetch } from "@/lib/api/client";
import type {
  AIPaperTradingExplanation,
  PaperAccount,
  PaperOrder,
  PaperPerformance,
  PaperPortfolio,
  PaperPosition,
  PaperTrade,
  SignalPaperExecutionResult
} from "@/lib/api/types";

export type PaperAccountCreateRequest = {
  name: string;
  initial_balance: number;
};

export type PaperOrderCreateRequest = {
  account_id: string;
  symbol: string;
  timeframe: string;
  side: "buy" | "sell";
  order_type: "market";
  notional: number;
  reason?: string | null;
};

export function createPaperAccount(request: PaperAccountCreateRequest) {
  return apiFetch<PaperAccount>("/paper/accounts", { method: "POST", body: request });
}

export function listPaperAccounts(filters: { status?: string } = {}) {
  return apiFetch<{ data: PaperAccount[] }>("/paper/accounts", { query: filters });
}

export function getPaperAccount(accountId: string) {
  return apiFetch<PaperAccount>(`/paper/accounts/${accountId}`);
}

export function pausePaperAccount(accountId: string) {
  return apiFetch<PaperAccount>(`/paper/accounts/${accountId}/pause`, { method: "PATCH" });
}

export function activatePaperAccount(accountId: string) {
  return apiFetch<PaperAccount>(`/paper/accounts/${accountId}/activate`, {
    method: "PATCH"
  });
}

export function closePaperAccount(accountId: string) {
  return apiFetch<PaperAccount>(`/paper/accounts/${accountId}/close`, { method: "PATCH" });
}

export function submitPaperOrder(request: PaperOrderCreateRequest) {
  return apiFetch<PaperOrder>("/paper/orders", { method: "POST", body: request });
}

export function listPaperOrders(accountId: string, status?: string, limit = 100) {
  return apiFetch<{ data: PaperOrder[] }>("/paper/orders", {
    query: { account_id: accountId, status, limit }
  });
}

export function getPaperOrder(orderId: string) {
  return apiFetch<PaperOrder>(`/paper/orders/${orderId}`);
}

export function cancelPaperOrder(orderId: string) {
  return apiFetch<PaperOrder>(`/paper/orders/${orderId}/cancel`, { method: "POST" });
}

export function listPaperPositions(accountId: string, status = "open") {
  return apiFetch<{ data: PaperPosition[] }>(`/paper/accounts/${accountId}/positions`, {
    query: { status }
  });
}

export function listPaperTrades(accountId: string, symbol?: string, limit = 100) {
  return apiFetch<{ data: PaperTrade[] }>(`/paper/accounts/${accountId}/trades`, {
    query: { symbol, limit }
  });
}

export function getPaperPortfolio(accountId: string) {
  return apiFetch<PaperPortfolio>(`/paper/accounts/${accountId}/portfolio`);
}

export function refreshPaperPortfolio(accountId: string) {
  return apiFetch<PaperPortfolio>(`/paper/accounts/${accountId}/refresh`, {
    method: "POST"
  });
}

export function getPaperPerformance(accountId: string) {
  return apiFetch<PaperPerformance>(`/paper/accounts/${accountId}/performance`);
}

export function runSignalPaperExecution(
  accountId: string,
  request: { symbol: string; timeframe: string; limit: number }
) {
  return apiFetch<SignalPaperExecutionResult>(`/paper/accounts/${accountId}/signal-execution`, {
    method: "POST",
    body: request
  });
}

export function explainPaperPortfolio(accountId: string) {
  return apiFetch<AIPaperTradingExplanation>(`/paper/accounts/${accountId}/explain`);
}

export function explainPaperOrder(orderId: string) {
  return apiFetch<AIPaperTradingExplanation>(`/paper/orders/${orderId}/explain`);
}
