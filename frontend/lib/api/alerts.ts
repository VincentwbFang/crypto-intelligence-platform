import { apiFetch } from "@/lib/api/client";
import type {
  AIExplanationResponse,
  AlertEvaluateRequest,
  AlertEvaluateResponse,
  AlertFilters,
  AlertListResponse,
  AlertResponse,
  NotificationResult
} from "@/lib/api/types";

export function listAlerts(filters: AlertFilters = {}) {
  return apiFetch<AlertListResponse>("/alerts", { query: filters });
}

export function getAlert(alertId: number | string) {
  return apiFetch<AlertResponse>(`/alerts/${alertId}`);
}

export function evaluateAlerts(request: AlertEvaluateRequest) {
  return apiFetch<AlertEvaluateResponse>("/alerts/evaluate", {
    method: "POST",
    body: request
  });
}

export function updateAlertStatus(alertId: number, status: string) {
  return apiFetch<AlertResponse>(`/alerts/${alertId}/status`, {
    method: "PATCH",
    body: { status }
  });
}

export function resolveAlert(alertId: number) {
  return apiFetch<AlertResponse>(`/alerts/${alertId}/resolve`, {
    method: "POST"
  });
}

export function explainAlert(alertId: number | string) {
  return apiFetch<AIExplanationResponse>(`/alerts/${alertId}/explain`);
}

export function testNotification(channel: string) {
  return apiFetch<NotificationResult>("/alerts/test-notification", {
    method: "POST",
    body: { channel }
  });
}
