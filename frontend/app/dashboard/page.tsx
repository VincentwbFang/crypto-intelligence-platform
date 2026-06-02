import Link from "next/link";

import { EmptyState } from "@/components/common/EmptyState";
import { ErrorState } from "@/components/common/ErrorState";
import { SectionCard } from "@/components/common/SectionCard";
import { StatCard } from "@/components/common/StatCard";
import { PageHeader } from "@/components/layout/PageHeader";
import { MarketOverviewCards } from "@/components/market/MarketOverviewCards";
import { RelativeStrengthDashboardCard } from "@/components/market/RelativeStrengthDashboardCard";
import { NewsBroadcastPanel } from "@/components/news/NewsBroadcastPanel";
import { AlertTable } from "@/components/alerts/AlertTable";
import { SignalRankTable } from "@/components/signals/SignalRankTable";
import { Button } from "@/components/ui/button";
import { listAlerts } from "@/lib/api/alerts";
import { getMarketSnapshot } from "@/lib/api/market";
import { rankSignals } from "@/lib/api/signals";
import type { AlertResponse, MarketSnapshot, SignalResponse } from "@/lib/api/types";

const defaultSymbols = ["BTC/USDT", "ETH/USDT", "SOL/USDT"];

export default async function DashboardPage() {
  const [snapshotsResult, rankingsResult, alertsResult] = await Promise.allSettled([
    Promise.all(defaultSymbols.map((symbol) => getMarketSnapshot(symbol, "1h"))),
    rankSignals(defaultSymbols, "1h", 200),
    listAlerts({ limit: 10 })
  ]);

  const snapshots =
    snapshotsResult.status === "fulfilled"
      ? snapshotsResult.value.filter(Boolean)
      : ([] as MarketSnapshot[]);
  const signals =
    rankingsResult.status === "fulfilled"
      ? rankingsResult.value.data
      : ([] as SignalResponse[]);
  const alerts =
    alertsResult.status === "fulfilled"
      ? alertsResult.value.data
      : ([] as AlertResponse[]);

  const hasError =
    snapshotsResult.status === "rejected" ||
    rankingsResult.status === "rejected" ||
    alertsResult.status === "rejected";

  return (
    <div>
      <PageHeader
        title="Dashboard"
        description="Overview of tracked symbols, deterministic signal ranking, and recent alerts."
        action={
          <Button asChild variant="outline">
            <Link href="/markets">Open Markets</Link>
          </Button>
        }
      />
      {hasError ? (
        <ErrorState message="One or more dashboard sections could not load. Existing sections remain visible when available." />
      ) : null}
      <div className="grid gap-4 md:grid-cols-3">
        <StatCard label="Tracked Symbols" value={defaultSymbols.length} detail="BTC, ETH, SOL" />
        <StatCard label="Signals Loaded" value={signals.length} detail="Ranked by deterministic score" />
        <StatCard label="Recent Alerts" value={alerts.length} detail="Newest stored alerts" />
      </div>
      <div className="mt-6 space-y-6">
        <SectionCard
          title="Market Status"
          description="Latest snapshots from stored OHLCV candles."
        >
          <MarketOverviewCards snapshots={snapshots} />
        </SectionCard>
        <NewsBroadcastPanel />
        <RelativeStrengthDashboardCard />
        <SectionCard title="Top Signal Ranking">
          {signals.length ? (
            <SignalRankTable signals={signals.slice(0, 5)} />
          ) : (
            <EmptyState message="Generate signals after ingesting OHLCV data to populate rankings." />
          )}
        </SectionCard>
        <SectionCard title="Recent Alerts">
          <AlertTable alerts={alerts} />
        </SectionCard>
      </div>
    </div>
  );
}
