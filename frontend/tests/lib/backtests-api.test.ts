import { afterEach, describe, expect, it, vi } from "vitest";

import {
  getBacktest,
  listStrategies,
  runBacktest
} from "@/lib/api/backtests";
import { ApiError } from "@/lib/api/client";

describe("backtests api", () => {
  afterEach(() => {
    vi.restoreAllMocks();
  });

  it("lists strategies", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue({
        ok: true,
        status: 200,
        headers: new Headers({ "Content-Type": "application/json" }),
        text: () => Promise.resolve(JSON.stringify({ data: [{ name: "ema_crossover" }] }))
      })
    );

    await expect(listStrategies()).resolves.toEqual({
      data: [{ name: "ema_crossover" }]
    });
  });

  it("runs a backtest", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue({
        ok: true,
        status: 200,
        headers: new Headers({ "Content-Type": "application/json" }),
        text: () => Promise.resolve(JSON.stringify({ run_id: "run-1" }))
      })
    );

    await expect(
      runBacktest({
        symbol: "BTC/USDT",
        timeframe: "1h",
        strategy_name: "ema_crossover",
        start_date: "2025-01-01T00:00:00Z",
        end_date: "2025-02-01T00:00:00Z",
        initial_capital: 10000,
        fee_bps: 10,
        slippage_bps: 5,
        max_position_pct: 1,
        parameters: {}
      })
    ).resolves.toEqual({ run_id: "run-1" });
  });

  it("gets a backtest", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue({
        ok: true,
        status: 200,
        headers: new Headers({ "Content-Type": "application/json" }),
        text: () => Promise.resolve(JSON.stringify({ run_id: "run-1" }))
      })
    );

    await expect(getBacktest("run-1")).resolves.toEqual({ run_id: "run-1" });
  });

  it("uses shared error handling", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue({
        ok: false,
        status: 500,
        headers: new Headers({ "Content-Type": "text/plain" }),
        text: () => Promise.resolve("Backtest failed")
      })
    );

    await expect(getBacktest("missing")).rejects.toBeInstanceOf(ApiError);
  });
});
