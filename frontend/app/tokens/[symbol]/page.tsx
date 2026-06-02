import { notFound } from "next/navigation";

import { CandleStats } from "@/components/market/CandleStats";
import { MarketSnapshotCard } from "@/components/market/MarketSnapshotCard";
import { OHLCVChart } from "@/components/market/OHLCVChart";
import { TokenSelector } from "@/components/market/TokenSelector";
import { EmptyState } from "@/components/common/EmptyState";
import { ErrorState } from "@/components/common/ErrorState";
import { SectionCard } from "@/components/common/SectionCard";
import { PageHeader } from "@/components/layout/PageHeader";
import { AIExplanationCard } from "@/components/signals/AIExplanationCard";
import { RiskLevelBadge } from "@/components/signals/RiskLevelBadge";
import { SignalDirectionBadge } from "@/components/signals/SignalDirectionBadge";
import { SignalScoreGrid } from "@/components/signals/SignalScoreGrid";
import { getMarketSnapshot, getOHLCV } from "@/lib/api/market";
import { getSignal } from "@/lib/api/signals";
import { parseSymbolFromRoute } from "@/lib/format";

type TokenPageProps = {
  params: Promise<{
    symbol: string;
  }>;
};

export default async function TokenDetailPage({ params }: TokenPageProps) {
  const { symbol: routeSymbol } = await params;
  const symbol = parseSymbolFromRoute(routeSymbol);
  if (!symbol.includes("/")) {
    notFound();
  }

  const [snapshotResult, rowsResult, signalResult] = await Promise.allSettled([
    getMarketSnapshot(symbol, "1h"),
    getOHLCV(symbol, "1h", 200),
    getSignal(symbol, "1h", 200, true)
  ]);

  const snapshot = snapshotResult.status === "fulfilled" ? snapshotResult.value : null;
  const rows = rowsResult.status === "fulfilled" ? rowsResult.value.data : [];
  const signal = signalResult.status === "fulfilled" ? signalResult.value : null;
  const hasError =
    snapshotResult.status === "rejected" ||
    rowsResult.status === "rejected" ||
    signalResult.status === "rejected";

  return (
    <div>
      <PageHeader
        title={symbol}
        description="Token-level market data, latest deterministic signal, and research-only explanation."
        action={<TokenSelector value={symbol} />}
      />
      {hasError ? (
        <ErrorState message="Some token data could not load. Available sections are still shown." />
      ) : null}
      <div className="space-y-6">
        {snapshot ? <MarketSnapshotCard snapshot={snapshot} /> : <EmptyState />}
        {rows.length ? <CandleStats rows={rows} /> : null}
        <SectionCard title="Candlestick Chart">
          <OHLCVChart rows={rows} />
        </SectionCard>
        {signal ? (
          <>
            <SectionCard
              title="Latest Deterministic Signal"
              action={
                <div className="flex gap-2">
                  <SignalDirectionBadge direction={signal.signal_direction} />
                  <RiskLevelBadge level={signal.risk_level} />
                </div>
              }
            >
              <SignalScoreGrid scores={signal.scores} />
              {signal.risk_notes.length ? (
                <ul className="mt-4 list-disc space-y-1 pl-5 text-sm text-muted-foreground">
                  {signal.risk_notes.map((note) => (
                    <li key={note}>{note}</li>
                  ))}
                </ul>
              ) : null}
            </SectionCard>
            <AIExplanationCard explanation={signal.ai_explanation} />
          </>
        ) : (
          <EmptyState message="No deterministic signal is available for this symbol yet." />
        )}
      </div>
    </div>
  );
}
