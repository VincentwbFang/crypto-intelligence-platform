import { afterEach, describe, expect, it, vi } from "vitest";

import { backfillMarketData, getMarketUniverse } from "@/lib/api/market";

describe("market api", () => {
  afterEach(() => {
    vi.restoreAllMocks();
  });

  it("loads the market universe", async () => {
    const fetchMock = vi.fn().mockResolvedValue({
      ok: true,
      status: 200,
      headers: new Headers({ "Content-Type": "application/json" }),
      text: () =>
        Promise.resolve(
          JSON.stringify({
            exchange: "okx",
            top_n: 30,
            quote: "USDT",
            source: "test",
            symbols: ["BTC/USDT", "ETH/USDT"],
            skipped: []
          })
        )
    });
    vi.stubGlobal("fetch", fetchMock);

    const result = await getMarketUniverse("okx", 30);

    expect(result.symbols).toEqual(["BTC/USDT", "ETH/USDT"]);
    expect(fetchMock).toHaveBeenCalledWith(
      expect.stringContaining("/market/universe?exchange=okx&top_n=30"),
      expect.any(Object)
    );
  });

  it("starts a market backfill request", async () => {
    const fetchMock = vi.fn().mockResolvedValue({
      ok: true,
      status: 200,
      headers: new Headers({ "Content-Type": "application/json" }),
      text: () =>
        Promise.resolve(
          JSON.stringify({
            exchange: "okx",
            timeframe: "1h",
            years: 3,
            symbols: ["BTC/USDT"],
            skipped: [],
            results: {
              "BTC/USDT": {
                symbol: "BTC/USDT",
                timeframe: "1h",
                fetched: 300,
                inserted: 300,
                duplicates: 0,
                batches: 1,
                last_timestamp: "2026-01-01T00:00:00Z"
              }
            }
          })
        )
    });
    vi.stubGlobal("fetch", fetchMock);

    const result = await backfillMarketData({
      exchange: "okx",
      symbols: null,
      use_top_market_cap: true,
      top_n: 30,
      timeframe: "1h",
      years: 3,
      batch_limit: 300,
      max_batches_per_symbol: 1
    });

    expect(result.results["BTC/USDT"].inserted).toBe(300);
    expect(fetchMock).toHaveBeenCalledWith(
      expect.stringContaining("/market/backfill"),
      expect.objectContaining({
        method: "POST"
      })
    );
  });
});
