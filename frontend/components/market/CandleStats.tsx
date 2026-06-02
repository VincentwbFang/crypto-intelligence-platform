import type { OHLCVRow } from "@/lib/api/types";

import { StatCard } from "@/components/common/StatCard";
import { formatDateTime, formatPrice } from "@/lib/format";

export function CandleStats({ rows }: { rows: OHLCVRow[] }) {
  const latest = rows.at(-1);
  if (!latest) {
    return null;
  }
  return (
    <div className="grid gap-4 md:grid-cols-4">
      <StatCard label="Open" value={formatPrice(latest.open)} />
      <StatCard label="High" value={formatPrice(latest.high)} />
      <StatCard label="Low" value={formatPrice(latest.low)} />
      <StatCard
        label="Volume"
        value={latest.volume.toLocaleString("en-US", { maximumFractionDigits: 2 })}
        detail={formatDateTime(latest.timestamp)}
      />
    </div>
  );
}
