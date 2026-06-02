import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { PaperPerformanceGrid } from "@/components/paper/PaperPerformanceGrid";
import type { PaperPerformance } from "@/lib/api/types";

const performance: PaperPerformance = {
  initial_balance: 10000,
  current_equity: 10000,
  total_return_pct: 0,
  realized_pnl: 0,
  unrealized_pnl: 0,
  total_fees: 0,
  total_trades: 0,
  win_rate: 0,
  profit_factor: null,
  max_drawdown_pct: 0,
  open_positions_count: 0,
  exposure_pct: 0
};

describe("PaperPerformanceGrid", () => {
  it("renders metrics", () => {
    render(<PaperPerformanceGrid performance={{ ...performance, total_return_pct: 3.2 }} />);
    expect(screen.getByText("Current Equity")).toBeInTheDocument();
    expect(screen.getByText("+3.20%")).toBeInTheDocument();
  });

  it("handles zero trades", () => {
    render(<PaperPerformanceGrid performance={performance} />);
    expect(screen.getByText("Trade Count")).toBeInTheDocument();
    expect(screen.getAllByText("0").length).toBeGreaterThan(0);
  });
});
