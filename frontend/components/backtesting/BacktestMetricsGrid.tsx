import { StatCard } from "@/components/common/StatCard";
import type { BacktestMetrics } from "@/lib/api/types";
import { formatPercent, formatPrice } from "@/lib/format";

export function BacktestMetricsGrid({ metrics }: { metrics?: BacktestMetrics | null }) {
  if (!metrics) {
    return (
      <div className="grid gap-4 md:grid-cols-3">
        <StatCard label="Final Equity" value="N/A" />
        <StatCard label="Total Return" value="N/A" />
        <StatCard label="Total Trades" value="0" />
      </div>
    );
  }

  return (
    <div className="grid gap-4 md:grid-cols-3 xl:grid-cols-4">
      <StatCard label="Final Equity" value={formatPrice(metrics.final_equity)} />
      <StatCard label="Total Return" value={formatPercent(metrics.total_return_pct)} />
      <StatCard label="Max Drawdown" value={formatPercent(metrics.max_drawdown_pct)} />
      <StatCard
        label="Sharpe"
        value={metrics.sharpe_ratio === null ? "N/A" : metrics.sharpe_ratio.toFixed(2)}
      />
      <StatCard label="Win Rate" value={formatPercent(metrics.win_rate * 100)} />
      <StatCard
        label="Profit Factor"
        value={metrics.profit_factor === null ? "N/A" : metrics.profit_factor.toFixed(2)}
      />
      <StatCard label="Total Trades" value={metrics.total_trades} />
      <StatCard label="Exposure" value={formatPercent(metrics.exposure_time_pct)} />
    </div>
  );
}
