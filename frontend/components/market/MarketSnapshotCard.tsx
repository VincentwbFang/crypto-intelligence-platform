import type { MarketSnapshot } from "@/lib/api/types";

import { StatCard } from "@/components/common/StatCard";
import { formatDateTime, formatPercent, formatPrice } from "@/lib/format";

export function MarketSnapshotCard({ snapshot }: { snapshot: MarketSnapshot }) {
  return (
    <StatCard
      label={snapshot.symbol}
      value={formatPrice(snapshot.latest_close)}
      detail={
        <div className="space-y-1">
          <div>{formatPercent(snapshot.return_pct)} from prior close</div>
          <div>{snapshot.candle_count} candles · {formatDateTime(snapshot.timestamp)}</div>
        </div>
      }
    />
  );
}
