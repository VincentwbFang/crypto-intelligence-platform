"use client";

import { useEffect, useMemo, useState } from "react";
import { useRouter } from "next/navigation";

import { ErrorState } from "@/components/common/ErrorState";
import { LoadingState } from "@/components/common/LoadingState";
import { StrategySelector } from "@/components/backtesting/StrategySelector";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Select } from "@/components/ui/select";
import { listStrategies, runBacktest } from "@/lib/api/backtests";
import type { BacktestStrategyInfo } from "@/lib/api/types";

const disclaimer =
  "Backtest results are hypothetical and based on historical data. They do not guarantee future performance.";

export function BacktestForm() {
  const router = useRouter();
  const [strategies, setStrategies] = useState<BacktestStrategyInfo[]>([]);
  const [strategyName, setStrategyName] = useState("");
  const [symbol, setSymbol] = useState("BTC/USDT");
  const [timeframe, setTimeframe] = useState("1h");
  const [startDate, setStartDate] = useState("2025-01-01T00:00");
  const [endDate, setEndDate] = useState("2025-03-01T00:00");
  const [initialCapital, setInitialCapital] = useState("10000");
  const [feeBps, setFeeBps] = useState("10");
  const [slippageBps, setSlippageBps] = useState("5");
  const [maxPositionPct, setMaxPositionPct] = useState("1");
  const [parameters, setParameters] = useState<Record<string, string>>({});
  const [isLoading, setIsLoading] = useState(true);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const selectedStrategy = useMemo(
    () => strategies.find((strategy) => strategy.name === strategyName),
    [strategies, strategyName]
  );

  useEffect(() => {
    async function load() {
      setIsLoading(true);
      setError(null);
      try {
        const result = await listStrategies();
        setStrategies(result.data);
        const first = result.data[0];
        if (first) {
          setStrategyName(first.name);
          setParameters(stringifyParameters(first.default_parameters));
        }
      } catch (loadError) {
        setError(loadError instanceof Error ? loadError.message : "Strategy loading failed.");
      } finally {
        setIsLoading(false);
      }
    }
    void load();
  }, []);

  function changeStrategy(nextStrategyName: string) {
    setStrategyName(nextStrategyName);
    const nextStrategy = strategies.find((strategy) => strategy.name === nextStrategyName);
    setParameters(stringifyParameters(nextStrategy?.default_parameters || {}));
  }

  async function submit() {
    setIsSubmitting(true);
    setError(null);
    try {
      if (!symbol.trim() || !strategyName || !startDate || !endDate) {
        throw new Error("Symbol, strategy, start date, and end date are required.");
      }
      const response = await runBacktest({
        symbol: symbol.trim(),
        timeframe,
        strategy_name: strategyName,
        start_date: new Date(startDate).toISOString(),
        end_date: new Date(endDate).toISOString(),
        initial_capital: Number(initialCapital),
        fee_bps: Number(feeBps),
        slippage_bps: Number(slippageBps),
        max_position_pct: Number(maxPositionPct),
        parameters: parseParameters(parameters)
      });
      router.push(`/backtests/${response.run_id}`);
    } catch (submitError) {
      setError(submitError instanceof Error ? submitError.message : "Backtest run failed.");
    } finally {
      setIsSubmitting(false);
    }
  }

  if (isLoading) {
    return <LoadingState label="Loading strategies" />;
  }

  return (
    <form
      className="space-y-6"
      onSubmit={(event) => {
        event.preventDefault();
        void submit();
      }}
    >
      {error ? <ErrorState message={error} /> : null}
      <div className="grid gap-4 md:grid-cols-2">
        <label className="space-y-2 text-sm font-medium">
          Symbol
          <Input value={symbol} onChange={(event) => setSymbol(event.target.value)} />
        </label>
        <label className="space-y-2 text-sm font-medium">
          Timeframe
          <Select value={timeframe} onChange={(event) => setTimeframe(event.target.value)}>
            <option value="1h">1h</option>
            <option value="4h">4h</option>
            <option value="1d">1d</option>
          </Select>
        </label>
        <label className="space-y-2 text-sm font-medium">
          Strategy
          <StrategySelector
            onChange={changeStrategy}
            strategies={strategies}
            value={strategyName}
          />
        </label>
        <div className="rounded-md border bg-muted/40 p-3 text-sm text-muted-foreground">
          {selectedStrategy?.description || "Select a deterministic strategy."}
        </div>
        <label className="space-y-2 text-sm font-medium">
          Start Date
          <Input
            type="datetime-local"
            value={startDate}
            onChange={(event) => setStartDate(event.target.value)}
          />
        </label>
        <label className="space-y-2 text-sm font-medium">
          End Date
          <Input
            type="datetime-local"
            value={endDate}
            onChange={(event) => setEndDate(event.target.value)}
          />
        </label>
        <label className="space-y-2 text-sm font-medium">
          Initial Capital
          <Input
            min="1"
            type="number"
            value={initialCapital}
            onChange={(event) => setInitialCapital(event.target.value)}
          />
        </label>
        <label className="space-y-2 text-sm font-medium">
          Max Position Pct
          <Input
            max="1"
            min="0.01"
            step="0.01"
            type="number"
            value={maxPositionPct}
            onChange={(event) => setMaxPositionPct(event.target.value)}
          />
        </label>
        <label className="space-y-2 text-sm font-medium">
          Fee Bps
          <Input
            min="0"
            type="number"
            value={feeBps}
            onChange={(event) => setFeeBps(event.target.value)}
          />
        </label>
        <label className="space-y-2 text-sm font-medium">
          Slippage Bps
          <Input
            min="0"
            type="number"
            value={slippageBps}
            onChange={(event) => setSlippageBps(event.target.value)}
          />
        </label>
      </div>
      <div>
        <h2 className="mb-3 text-sm font-semibold">Strategy Parameters</h2>
        <div className="grid gap-4 md:grid-cols-3">
          {Object.entries(parameters).map(([key, value]) => (
            <label className="space-y-2 text-sm font-medium" key={key}>
              {key.replaceAll("_", " ")}
              <Input
                value={value}
                onChange={(event) =>
                  setParameters((current) => ({ ...current, [key]: event.target.value }))
                }
              />
            </label>
          ))}
        </div>
      </div>
      <p className="text-sm text-muted-foreground">{disclaimer}</p>
      <Button disabled={isSubmitting || !strategies.length} type="submit">
        {isSubmitting ? "Running..." : "Run research backtest"}
      </Button>
    </form>
  );
}

function stringifyParameters(
  parameters: Record<string, string | number | boolean>
): Record<string, string> {
  return Object.fromEntries(
    Object.entries(parameters).map(([key, value]) => [key, String(value)])
  );
}

function parseParameters(parameters: Record<string, string>) {
  return Object.fromEntries(
    Object.entries(parameters).map(([key, value]) => {
      const numeric = Number(value);
      if (value.trim() !== "" && Number.isFinite(numeric)) {
        return [key, numeric];
      }
      if (value === "true" || value === "false") {
        return [key, value === "true"];
      }
      return [key, value];
    })
  );
}
