import { describe, expect, it } from "vitest";

import {
  formatPercent,
  formatPrice,
  formatScore,
  formatSymbolForRoute,
  parseSymbolFromRoute
} from "@/lib/format";

describe("format helpers", () => {
  it("formats prices", () => {
    expect(formatPrice(1234.56)).toBe("$1,234.56");
    expect(formatPrice(null)).toBe("N/A");
  });

  it("formats percentages", () => {
    expect(formatPercent(1.234)).toBe("+1.23%");
    expect(formatPercent(-2)).toBe("-2.00%");
  });

  it("formats scores safely", () => {
    expect(formatScore(67.777)).toBe("67.8");
    expect(formatScore(120)).toBe("100.0");
    expect(formatScore(undefined)).toBe("N/A");
  });

  it("encodes and decodes symbols for routes", () => {
    expect(formatSymbolForRoute("BTC/USDT")).toBe("BTC-USDT");
    expect(parseSymbolFromRoute("btc-usdt")).toBe("BTC/USDT");
  });
});
