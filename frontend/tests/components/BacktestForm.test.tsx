import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

import { BacktestForm } from "@/components/backtesting/BacktestForm";
import { listStrategies, runBacktest } from "@/lib/api/backtests";

const push = vi.fn();

vi.mock("next/navigation", () => ({
  useRouter: () => ({ push })
}));

vi.mock("@/lib/api/backtests", () => ({
  listStrategies: vi.fn(),
  runBacktest: vi.fn()
}));

const strategies = [
  {
    name: "ema_crossover",
    description: "EMA crossover",
    default_parameters: { fast_ema: 20, slow_ema: 50 },
    supported_positioning: "long_only"
  }
];

describe("BacktestForm", () => {
  it("renders strategy selector and loads default parameters", async () => {
    vi.mocked(listStrategies).mockResolvedValueOnce({ data: strategies });
    render(<BacktestForm />);

    expect(await screen.findByLabelText("Strategy")).toBeInTheDocument();
    expect(screen.getByDisplayValue("20")).toBeInTheDocument();
    expect(screen.getByDisplayValue("50")).toBeInTheDocument();
  });

  it("validates required fields", async () => {
    vi.mocked(listStrategies).mockResolvedValueOnce({ data: strategies });
    render(<BacktestForm />);

    const symbol = await screen.findByLabelText("Symbol");
    fireEvent.change(symbol, { target: { value: "" } });
    fireEvent.click(screen.getByRole("button", { name: /run research backtest/i }));

    expect(await screen.findByText(/required/i)).toBeInTheDocument();
  });

  it("submits request", async () => {
    vi.mocked(listStrategies).mockResolvedValueOnce({ data: strategies });
    vi.mocked(runBacktest).mockResolvedValueOnce({
      run_id: "run-1",
      symbol: "BTC/USDT",
      timeframe: "1h",
      strategy_name: "ema_crossover",
      parameters: {},
      initial_capital: 10000,
      status: "completed",
      trades: [],
      equity_curve: []
    });
    render(<BacktestForm />);

    await screen.findByLabelText("Strategy");
    fireEvent.click(screen.getByRole("button", { name: /run research backtest/i }));

    await waitFor(() => expect(runBacktest).toHaveBeenCalled());
    expect(push).toHaveBeenCalledWith("/backtests/run-1");
  });
});
