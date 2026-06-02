import { PageHeader } from "@/components/layout/PageHeader";
import { MarketExplorer } from "@/components/market/MarketExplorer";

export default function MarketsPage() {
  return (
    <div>
      <PageHeader
        title="Markets"
        description="Ingest public OHLCV data, inspect snapshots, and review recent candles."
      />
      <MarketExplorer />
    </div>
  );
}
