import { notFound } from "next/navigation";

import { EmptyState } from "@/components/common/EmptyState";
import { ErrorState } from "@/components/common/ErrorState";
import { SectionCard } from "@/components/common/SectionCard";
import { PageHeader } from "@/components/layout/PageHeader";
import { TokenSelector } from "@/components/market/TokenSelector";
import { AIExplanationCard } from "@/components/signals/AIExplanationCard";
import { IndicatorTable } from "@/components/signals/IndicatorTable";
import { RelativeStrengthCard } from "@/components/signals/RelativeStrengthCard";
import { RiskLevelBadge } from "@/components/signals/RiskLevelBadge";
import { SetupTypeBadge } from "@/components/signals/SetupTypeBadge";
import { SignalDirectionBadge } from "@/components/signals/SignalDirectionBadge";
import { SignalScoreGrid } from "@/components/signals/SignalScoreGrid";
import { getSignal } from "@/lib/api/signals";
import { formatDateTime, formatPrice, parseSymbolFromRoute } from "@/lib/format";

type SignalDetailPageProps = {
  params: Promise<{
    symbol: string;
  }>;
};

export default async function SignalDetailPage({ params }: SignalDetailPageProps) {
  const { symbol: routeSymbol } = await params;
  const symbol = parseSymbolFromRoute(routeSymbol);
  if (!symbol.includes("/")) {
    notFound();
  }

  try {
    const signal = await getSignal(symbol, "1h", 200, true);
    return (
      <div>
        <PageHeader
          title={`${symbol} Signal`}
          description="Deterministic market intelligence with optional research-only AI explanation."
          action={<TokenSelector basePath="signals" value={symbol} />}
        />
        <div className="space-y-6">
          <SectionCard
            title="Signal Summary"
            description={`${formatDateTime(signal.timestamp)} · latest close ${formatPrice(
              signal.latest_close
            )}`}
            action={
              <div className="flex flex-wrap gap-2">
                <SignalDirectionBadge direction={signal.signal_direction} />
                <SetupTypeBadge setupType={signal.setup_type} />
                <RiskLevelBadge level={signal.risk_level} />
              </div>
            }
          >
            <SignalScoreGrid scores={signal.scores} />
          </SectionCard>
          {!signal.data_quality.has_sufficient_data ? (
            <ErrorState
              title="Data quality warning"
              message="This signal has limited candle history and should be interpreted cautiously."
            />
          ) : null}
          <SectionCard title="Risk Notes">
            {signal.risk_notes.length ? (
              <ul className="list-disc space-y-1 pl-5 text-sm text-muted-foreground">
                {signal.risk_notes.map((note) => (
                  <li key={note}>{note}</li>
                ))}
              </ul>
            ) : (
              <EmptyState message="No risk notes were generated for this signal." />
            )}
          </SectionCard>
          <RelativeStrengthCard relativeStrength={signal.relative_strength} />
          <SectionCard title="Indicators">
            <IndicatorTable indicators={signal.indicators} />
          </SectionCard>
          <SectionCard title="Data Quality">
            <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
              <Quality label="Candles" value={String(signal.data_quality.candle_count)} />
              <Quality
                label="Minimum Required"
                value={String(signal.data_quality.min_required_candles)}
              />
              <Quality
                label="Sufficient Data"
                value={signal.data_quality.has_sufficient_data ? "Yes" : "No"}
              />
              <Quality
                label="Missing Indicator"
                value={signal.data_quality.missing_indicator_warning ? "Yes" : "No"}
              />
            </div>
          </SectionCard>
          <AIExplanationCard explanation={signal.ai_explanation} />
        </div>
      </div>
    );
  } catch (error) {
    return (
      <div>
        <PageHeader title={`${symbol} Signal`} />
        <ErrorState
          message={error instanceof Error ? error.message : "Signal data failed."}
        />
      </div>
    );
  }
}

function Quality({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-md border bg-background p-3">
      <p className="text-xs text-muted-foreground">{label}</p>
      <p className="mt-1 font-medium">{value}</p>
    </div>
  );
}
