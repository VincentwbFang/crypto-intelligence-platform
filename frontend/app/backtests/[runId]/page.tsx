import { notFound } from "next/navigation";

import { BacktestExplanationCard } from "@/components/backtesting/BacktestExplanationCard";
import { BacktestMetricsGrid } from "@/components/backtesting/BacktestMetricsGrid";
import { DrawdownChart } from "@/components/backtesting/DrawdownChart";
import { EquityCurveChart } from "@/components/backtesting/EquityCurveChart";
import { TradeTable } from "@/components/backtesting/TradeTable";
import { ErrorState } from "@/components/common/ErrorState";
import { SectionCard } from "@/components/common/SectionCard";
import { PageHeader } from "@/components/layout/PageHeader";
import { explainBacktest, getBacktest } from "@/lib/api/backtests";
import type { AIBacktestExplanation } from "@/lib/api/types";
import { formatDateTime, formatPercent, formatPrice } from "@/lib/format";

type BacktestDetailPageProps = {
  params: Promise<{
    runId: string;
  }>;
};

export default async function BacktestDetailPage({ params }: BacktestDetailPageProps) {
  const { runId } = await params;
  if (!runId) {
    notFound();
  }

  try {
    const backtest = await getBacktest(runId);
    let explanation: AIBacktestExplanation = {
      enabled: false,
      message: "AI backtest explanation is disabled."
    };
    try {
      explanation = await explainBacktest(runId);
    } catch {
      explanation = {
        enabled: false,
        message: "AI backtest explanation is unavailable."
      };
    }

    return (
      <div>
        <PageHeader
          title={`${backtest.symbol} Backtest`}
          description={`${backtest.strategy_name.replaceAll("_", " ")} · ${backtest.timeframe}`}
        />
        <div className="space-y-6">
          <SectionCard
            title="Run Summary"
            description="Backtest results are hypothetical and based on historical data. They do not guarantee future performance."
          >
            <div className="grid gap-3 md:grid-cols-4">
              <Meta label="Status" value={backtest.status} />
              <Meta label="Created" value={formatDateTime(backtest.created_at)} />
              <Meta label="Initial Capital" value={formatPrice(backtest.initial_capital)} />
              <Meta label="Total Return" value={formatPercent(backtest.total_return_pct)} />
            </div>
            {backtest.error_message ? (
              <div className="mt-4 rounded-md border border-red-200 bg-red-50 p-3 text-sm text-red-800">
                {backtest.error_message}
              </div>
            ) : null}
          </SectionCard>
          <BacktestMetricsGrid metrics={backtest.metrics} />
          <SectionCard title="Equity Curve">
            <EquityCurveChart points={backtest.equity_curve} />
          </SectionCard>
          <SectionCard title="Drawdown">
            <DrawdownChart points={backtest.equity_curve} />
          </SectionCard>
          <SectionCard title="Trades">
            <TradeTable trades={backtest.trades} />
          </SectionCard>
          <SectionCard title="Parameters">
            <pre className="overflow-x-auto rounded-md bg-muted p-4 text-xs">
              {JSON.stringify(backtest.parameters, null, 2)}
            </pre>
          </SectionCard>
          <BacktestExplanationCard explanation={explanation} />
        </div>
      </div>
    );
  } catch (error) {
    return (
      <div>
        <PageHeader title="Backtest Detail" />
        <ErrorState
          message={error instanceof Error ? error.message : "Backtest detail failed."}
        />
      </div>
    );
  }
}

function Meta({ label, value }: { label: string; value: string | number }) {
  return (
    <div className="rounded-md border bg-background p-3">
      <p className="text-xs text-muted-foreground">{label}</p>
      <p className="mt-1 font-medium">{value}</p>
    </div>
  );
}
