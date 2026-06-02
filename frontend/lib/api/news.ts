import { apiFetch } from "@/lib/api/client";
import type {
  NewsAlertsResponse,
  NewsBriefingResponse,
  NewsLatestResponse,
  NewsSourcesResponse
} from "@/lib/api/types";

export function getLatestNews(params: {
  limit?: number;
  symbol?: string;
  urgency?: string;
  source?: string;
} = {}): Promise<NewsLatestResponse> {
  return apiFetch<NewsLatestResponse>("/api/news/latest", { query: params });
}

export function getNewsBriefing(type = "latest"): Promise<NewsBriefingResponse> {
  return apiFetch<NewsBriefingResponse>("/api/news/briefing", { query: { type } });
}

export function getNewsAlerts(limit = 20): Promise<NewsAlertsResponse> {
  return apiFetch<NewsAlertsResponse>("/api/news/alerts", { query: { limit } });
}

export function refreshNews(): Promise<Record<string, unknown>> {
  return apiFetch<Record<string, unknown>>("/api/news/refresh", { method: "POST" });
}

export function analyzeNews(): Promise<Record<string, unknown>> {
  return apiFetch<Record<string, unknown>>("/api/news/analyze", { method: "POST" });
}

export function getNewsSources(): Promise<NewsSourcesResponse> {
  return apiFetch<NewsSourcesResponse>("/api/news/sources");
}
