export class ApiError extends Error {
  status: number;
  details: unknown;

  constructor(message: string, status: number, details: unknown = null) {
    super(message);
    this.name = "ApiError";
    this.status = status;
    this.details = details;
  }
}

export type QueryValue = string | number | boolean | null | undefined;
export type QueryParams = Record<string, QueryValue>;

const ACCESS_TOKEN_KEY = "cip_access_token";
const REFRESH_TOKEN_KEY = "cip_refresh_token";

export function buildQuery(params: QueryParams = {}) {
  const searchParams = new URLSearchParams();
  Object.entries(params).forEach(([key, value]) => {
    if (value !== undefined && value !== null && value !== "") {
      searchParams.set(key, String(value));
    }
  });
  const query = searchParams.toString();
  return query ? `?${query}` : "";
}

function getBaseUrl() {
  if (typeof window === "undefined") {
    return (
      process.env.BACKEND_INTERNAL_URL ||
      process.env.NEXT_PUBLIC_API_BASE_URL ||
      "http://localhost:8000"
    ).replace(/\/$/, "");
  }
  return (process.env.NEXT_PUBLIC_API_BASE_URL || "/api/backend").replace(/\/$/, "");
}

type ApiFetchOptions = {
  method?: "GET" | "POST" | "PATCH" | "DELETE";
  query?: QueryParams;
  body?: unknown;
  timeoutMs?: number;
  cache?: RequestCache;
};

export async function apiFetch<T>(
  path: string,
  options: ApiFetchOptions = {}
): Promise<T> {
  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), options.timeoutMs ?? 12000);
  const baseUrl = getBaseUrl();
  const url = `${baseUrl}${path.startsWith("/") ? path : `/${path}`}${buildQuery(
    options.query
  )}`;

  try {
    const response = await fetch(url, {
      method: options.method ?? "GET",
      headers: buildHeaders(url),
      body: options.body === undefined ? undefined : JSON.stringify(options.body),
      cache: options.cache ?? "no-store",
      signal: controller.signal
    });

    const text = await response.text();
    const data = parseResponseBody(text, response.headers.get("Content-Type"));
    if (response.status === 401 && !path.includes("/auth/refresh") && canAttemptRefresh(baseUrl)) {
      const refreshed = await refreshAccessToken(baseUrl);
      if (refreshed) {
        return apiFetch<T>(path, { ...options, timeoutMs: options.timeoutMs ?? 12000 });
      }
    }
    if (!response.ok) {
      const message = getErrorMessage(data, response.status);
      throw new ApiError(message, response.status, data);
    }
    return data as T;
  } finally {
    clearTimeout(timeout);
  }
}

function buildHeaders(url: string) {
  const headers: Record<string, string> = {
    "Content-Type": "application/json"
  };
  const token = getBrowserToken(ACCESS_TOKEN_KEY);
  if (token && shouldAttachAuthHeader(url)) {
    headers.Authorization = `Bearer ${token}`;
  }
  return headers;
}

function shouldAttachAuthHeader(url: string) {
  if (typeof window === "undefined") {
    return false;
  }
  const resolved = new URL(url, window.location.origin);
  return resolved.origin === window.location.origin;
}

function canAttemptRefresh(baseUrl: string) {
  return (
    typeof window !== "undefined" &&
    shouldAttachAuthHeader(baseUrl) &&
    Boolean(getBrowserToken(REFRESH_TOKEN_KEY))
  );
}

async function refreshAccessToken(baseUrl: string) {
  const refreshToken = getBrowserToken(REFRESH_TOKEN_KEY);
  if (!refreshToken) {
    return false;
  }
  try {
    const response = await fetch(`${baseUrl}/auth/refresh`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ refresh_token: refreshToken })
    });
    if (!response.ok) {
      clearBrowserTokens();
      return false;
    }
    const data = (await response.json()) as {
      access_token?: string;
      refresh_token?: string;
    };
    if (!data.access_token || !data.refresh_token) {
      clearBrowserTokens();
      return false;
    }
    window.localStorage.setItem(ACCESS_TOKEN_KEY, data.access_token);
    window.localStorage.setItem(REFRESH_TOKEN_KEY, data.refresh_token);
    return true;
  } catch {
    clearBrowserTokens();
    return false;
  }
}

function getBrowserToken(key: string) {
  if (typeof window === "undefined") {
    return null;
  }
  return window.localStorage.getItem(key);
}

function clearBrowserTokens() {
  if (typeof window === "undefined") {
    return;
  }
  window.localStorage.removeItem(ACCESS_TOKEN_KEY);
  window.localStorage.removeItem(REFRESH_TOKEN_KEY);
}

function parseResponseBody(text: string, contentType: string | null): unknown {
  if (!text) {
    return null;
  }
  if (contentType?.toLowerCase().includes("application/json")) {
    try {
      return JSON.parse(text);
    } catch {
      throw new ApiError("API returned invalid JSON.", 0, text);
    }
  }
  try {
    return JSON.parse(text);
  } catch {
    return text;
  }
}

function getErrorMessage(data: unknown, status: number): string {
  if (isRecord(data) && typeof data.detail === "string") {
    return data.detail;
  }
  if (isRecord(data) && isRecord(data.error) && typeof data.error.message === "string") {
    return data.error.message;
  }
  if (typeof data === "string" && data.trim()) {
    return data.trim();
  }
  return `API request failed with status ${status}`;
}

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null && !Array.isArray(value);
}
