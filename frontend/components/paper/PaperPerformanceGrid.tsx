import { StatCard } from "@/components/common/StatCard";
import type { PaperPerformance } from "@/lib/api/types";
import { formatPercent, formatPrice } from "@/lib/format";

export function PaperPerformanceGrid({ performance }: { performance: PaperPerformance }) {
  return (
    <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
      <StatCard label="Current Equity" value={formatPrice(performance.current_equity)} />
      <StatCard label="Simulated Return" value={formatPercent(performance.total_return_pct)} />
      <StatCard label="Realized PnL" value={formatPrice(performance.realized_pnl)} />
      <StatCard label="Unrealized PnL" value={formatPrice(performance.unrealized_pnl)} />
      <StatCard label="Total Fees" value={formatPrice(performance.total_fees)} />
      <StatCard label="Trade Count" value={String(performance.total_trades)} />
      <StatCard label="Win Rate" value={formatPercent(performance.win_rate * 100)} />
      <StatCard label="Exposure" value={formatPercent(performance.exposure_pct)} />
    </div>
  );
}
