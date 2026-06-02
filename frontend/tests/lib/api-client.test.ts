import { afterEach, describe, expect, it, vi } from "vitest";

import { apiFetch, ApiError, buildQuery } from "@/lib/api/client";

describe("api client", () => {
  afterEach(() => {
    vi.restoreAllMocks();
  });

  it("parses successful JSON responses", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue({
        ok: true,
        status: 200,
        headers: new Headers({ "Content-Type": "application/json" }),
        text: () => Promise.resolve(JSON.stringify({ status: "ok" }))
      })
    );

    await expect(apiFetch<{ status: string }>("/health")).resolves.toEqual({
      status: "ok"
    });
  });

  it("throws ApiError for error responses", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue({
        ok: false,
        status: 404,
        headers: new Headers({ "Content-Type": "application/json" }),
        text: () => Promise.resolve(JSON.stringify({ detail: "Not found" }))
      })
    );

    await expect(apiFetch("/missing")).rejects.toBeInstanceOf(ApiError);
  });

  it("uses structured error response messages", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue({
        ok: false,
        status: 401,
        headers: new Headers({ "Content-Type": "application/json" }),
        text: () => Promise.resolve(JSON.stringify({ error: { message: "Authentication required." } }))
      })
    );

    await expect(apiFetch("/protected")).rejects.toMatchObject({
      message: "Authentication required.",
      status: 401
    });
  });

  it("uses plain-text error responses when JSON is unavailable", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue({
        ok: false,
        status: 500,
        headers: new Headers({ "Content-Type": "text/plain" }),
        text: () => Promise.resolve("Internal Server Error")
      })
    );

    await expect(apiFetch("/broken")).rejects.toMatchObject({
      message: "Internal Server Error",
      status: 500
    });
  });

  it("builds query params", () => {
    expect(buildQuery({ symbol: "BTC/USDT", limit: 200, empty: "" })).toBe(
      "?symbol=BTC%2FUSDT&limit=200"
    );
  });
});
