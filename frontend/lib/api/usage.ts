import { apiFetch } from "@/lib/api/client";
import type { PlanLimits, UsageSummary } from "@/lib/api/types";

export function getUsageSummary() {
  return apiFetch<UsageSummary>("/usage/summary");
}

export function getUsageLimits() {
  return apiFetch<PlanLimits>("/usage/limits");
}
