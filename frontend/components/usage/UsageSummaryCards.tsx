import { StatCard } from "@/components/common/StatCard";
import type { UsageSummary } from "@/lib/api/types";

export function UsageSummaryCards({ summary }: { summary: UsageSummary }) {
  return (
    <div className="grid gap-4 md:grid-cols-4">
      <StatCard label="AI Explanations" value={summary.usage.ai_explanation ?? 0} detail="This month" />
      <StatCard label="Backtests" value={summary.usage.backtest_run ?? 0} detail="This month" />
      <StatCard label="Paper Orders" value={summary.usage.paper_order ?? 0} detail="This month" />
      <StatCard label="Watchlist Adds" value={summary.usage.watchlist_symbol_added ?? 0} detail="This month" />
    </div>
  );
}
