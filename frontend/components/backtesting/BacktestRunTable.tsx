"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { Trash2 } from "lucide-react";

import { EmptyState } from "@/components/common/EmptyState";
import { ErrorState } from "@/components/common/ErrorState";
import { LoadingState } from "@/components/common/LoadingState";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Select } from "@/components/ui/select";
import { deleteBacktest, listBacktests } from "@/lib/api/backtests";
import type { BacktestRun } from "@/lib/api/types";
import { formatDateTime, formatPercent } from "@/lib/format";

export function BacktestRunTable() {
  const [runs, setRuns] = useState<BacktestRun[]>([]);
  const [symbol, setSymbol] = useState("");
  const [strategyName, setStrategyName] = useState("");
  const [status, setStatus] = useState("");
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  async function loadRuns() {
    setIsLoading(true);
    setError(null);
    try {
      const result = await listBacktests({
        symbol,
        strategy_name: strategyName,
        status,
        limit: 50
      });
      setRuns(result.data);
    } catch (loadError) {
      setRuns([]);
      setError(loadError instanceof Error ? loadError.message : "Backtest list failed.");
    } finally {
      setIsLoading(false);
    }
  }

  async function removeRun(runId: string) {
    setError(null);
    try {
      await deleteBacktest(runId);
      await loadRuns();
    } catch (deleteError) {
      setError(deleteError instanceof Error ? deleteError.message : "Delete failed.");
    }
  }

  useEffect(() => {
    void loadRuns();
  }, []);

  return (
    <div className="space-y-4">
      <form
        className="grid gap-3 md:grid-cols-[1fr_1fr_160px_auto]"
        onSubmit={(event) => {
          event.preventDefault();
          void loadRuns();
        }}
      >
        <Input
          aria-label="Symbol filter"
          onChange={(event) => setSymbol(event.target.value)}
          placeholder="Symbol"
          value={symbol}
        />
        <Input
          aria-label="Strategy filter"
          onChange={(event) => setStrategyName(event.target.value)}
          placeholder="Strategy"
          value={strategyName}
        />
        <Select
          aria-label="Status filter"
          onChange={(event) => setStatus(event.target.value)}
          value={status}
        >
          <option value="">All statuses</option>
          <option value="completed">Completed</option>
          <option value="failed">Failed</option>
          <option value="running">Running</option>
        </Select>
        <Button type="submit">Apply Filters</Button>
      </form>
      {error ? <ErrorState message={error} /> : null}
      {isLoading ? <LoadingState label="Loading backtests" /> : null}
      {!isLoading && !runs.length ? (
        <EmptyState message="No backtest runs are stored yet." />
      ) : null}
      {!isLoading && runs.length ? (
        <div className="overflow-x-auto">
          <table className="w-full min-w-[1000px] text-left text-sm">
            <thead className="border-b text-xs uppercase text-muted-foreground">
              <tr>
                <th className="py-3 pr-4">Created At</th>
                <th className="py-3 pr-4">Symbol</th>
                <th className="py-3 pr-4">Timeframe</th>
                <th className="py-3 pr-4">Strategy</th>
                <th className="py-3 pr-4">Total Return</th>
                <th className="py-3 pr-4">Max Drawdown</th>
                <th className="py-3 pr-4">Sharpe</th>
                <th className="py-3 pr-4">Win Rate</th>
                <th className="py-3 pr-4">Trades</th>
                <th className="py-3 pr-4">Status</th>
                <th className="py-3 pr-4">Actions</th>
              </tr>
            </thead>
            <tbody>
              {runs.map((run) => (
                <tr className="border-b last:border-0" key={run.run_id}>
                  <td className="py-3 pr-4">{formatDateTime(run.created_at)}</td>
                  <td className="py-3 pr-4 font-medium">{run.symbol}</td>
                  <td className="py-3 pr-4">{run.timeframe}</td>
                  <td className="py-3 pr-4">{run.strategy_name.replaceAll("_", " ")}</td>
                  <td className="py-3 pr-4">{formatPercent(run.total_return_pct)}</td>
                  <td className="py-3 pr-4">{formatPercent(run.max_drawdown_pct)}</td>
                  <td className="py-3 pr-4">
                    {run.sharpe_ratio === null || run.sharpe_ratio === undefined
                      ? "N/A"
                      : run.sharpe_ratio.toFixed(2)}
                  </td>
                  <td className="py-3 pr-4">
                    {run.win_rate === null || run.win_rate === undefined
                      ? "N/A"
                      : formatPercent(run.win_rate * 100)}
                  </td>
                  <td className="py-3 pr-4">{run.total_trades ?? 0}</td>
                  <td className="py-3 pr-4 capitalize">{run.status}</td>
                  <td className="py-3 pr-4">
                    <div className="flex gap-2">
                      <Button asChild size="sm" variant="outline">
                        <Link href={`/backtests/${run.run_id}`}>View</Link>
                      </Button>
                      <Button
                        aria-label={`Delete ${run.run_id}`}
                        onClick={() => void removeRun(run.run_id)}
                        size="icon"
                        type="button"
                        variant="ghost"
                      >
                        <Trash2 className="h-4 w-4" />
                      </Button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      ) : null}
    </div>
  );
}
