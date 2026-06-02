import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { BacktestMetricsGrid } from "@/components/backtesting/BacktestMetricsGrid";
import type { BacktestMetrics } from "@/lib/api/types";

const metrics: BacktestMetrics = {
  initial_capital: 10000,
  final_equity: 11000,
  total_return_pct: 10,
  max_drawdown_pct: -5,
  sharpe_ratio: null,
  win_rate: 0.5,
  profit_factor: null,
  total_trades: 0,
  average_trade_return_pct: 0,
  average_holding_period_bars: 0,
  exposure_time_pct: 20
};

describe("BacktestMetricsGrid", () => {
  it("renders metrics", () => {
    render(<BacktestMetricsGrid metrics={{ ...metrics, total_trades: 3 }} />);
    expect(screen.getByText("Final Equity")).toBeInTheDocument();
    expect(screen.getByText("+10.00%")).toBeInTheDocument();
    expect(screen.getByText("3")).toBeInTheDocument();
  });

  it("handles null Sharpe", () => {
    render(<BacktestMetricsGrid metrics={metrics} />);
    expect(screen.getAllByText("N/A").length).toBeGreaterThan(0);
  });

  it("handles zero trades", () => {
    render(<BacktestMetricsGrid metrics={metrics} />);
    expect(screen.getByText("0")).toBeInTheDocument();
  });
});
