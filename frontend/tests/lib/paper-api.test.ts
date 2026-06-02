import { afterEach, describe, expect, it, vi } from "vitest";

import { ApiError } from "@/lib/api/client";
import {
  createPaperAccount,
  getPaperPerformance,
  getPaperPortfolio,
  submitPaperOrder
} from "@/lib/api/paper";

describe("paper api", () => {
  afterEach(() => {
    vi.restoreAllMocks();
  });

  function mockJson(data: unknown, ok = true, status = 200) {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue({
        ok,
        status,
        headers: new Headers({ "Content-Type": "application/json" }),
        text: () => Promise.resolve(JSON.stringify(data))
      })
    );
  }

  it("creates paper account", async () => {
    mockJson({ account_id: "account-1" });
    await expect(
      createPaperAccount({ name: "Main", initial_balance: 10000 })
    ).resolves.toEqual({ account_id: "account-1" });
  });

  it("submits paper order", async () => {
    mockJson({ order_id: "order-1", status: "filled" });
    await expect(
      submitPaperOrder({
        account_id: "account-1",
        symbol: "BTC/USDT",
        timeframe: "1h",
        side: "buy",
        order_type: "market",
        notional: 500
      })
    ).resolves.toEqual({ order_id: "order-1", status: "filled" });
  });

  it("gets portfolio and performance", async () => {
    mockJson({ account: { account_id: "account-1" }, positions: [], open_orders: [] });
    await expect(getPaperPortfolio("account-1")).resolves.toEqual({
      account: { account_id: "account-1" },
      positions: [],
      open_orders: []
    });

    mockJson({ current_equity: 10000 });
    await expect(getPaperPerformance("account-1")).resolves.toEqual({
      current_equity: 10000
    });
  });

  it("uses shared error handling", async () => {
    mockJson({ detail: "Paper error" }, false, 400);
    await expect(getPaperPortfolio("missing")).rejects.toBeInstanceOf(ApiError);
  });
});
