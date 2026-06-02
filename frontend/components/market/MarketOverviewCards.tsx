import { EmptyState } from "@/components/common/EmptyState";
import { MarketSnapshotCard } from "@/components/market/MarketSnapshotCard";
import type { MarketSnapshot } from "@/lib/api/types";

export function MarketOverviewCards({ snapshots }: { snapshots: MarketSnapshot[] }) {
  if (!snapshots.length) {
    return (
      <EmptyState message="No market snapshots are available. Ingest OHLCV data to populate this section." />
    );
  }
  return (
    <div className="grid gap-4 md:grid-cols-3">
      {snapshots.map((snapshot) => (
        <MarketSnapshotCard key={snapshot.symbol} snapshot={snapshot} />
      ))}
    </div>
  );
}
