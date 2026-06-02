import { apiFetch } from "@/lib/api/client";
import type { SystemHealth, SystemReady, SystemVersion } from "@/lib/api/types";

export function getSystemHealth() {
  return apiFetch<SystemHealth>("/system/health");
}

export function getSystemReady() {
  return apiFetch<SystemReady>("/system/ready");
}

export function getSystemVersion() {
  return apiFetch<SystemVersion>("/system/version");
}

export async function getMetricsPreview() {
  return apiFetch<string>("/metrics");
}
