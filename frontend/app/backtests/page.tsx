import Link from "next/link";

import { BacktestRunTable } from "@/components/backtesting/BacktestRunTable";
import { SectionCard } from "@/components/common/SectionCard";
import { PageHeader } from "@/components/layout/PageHeader";
import { Button } from "@/components/ui/button";

export default function BacktestsPage() {
  return (
    <div>
      <PageHeader
        title="Backtests"
        description="Review historical research backtests created from stored OHLCV data."
        action={
          <Button asChild>
            <Link href="/backtests/new">New Backtest</Link>
          </Button>
        }
      />
      <SectionCard
        title="Backtest Runs"
        description="Backtest results are hypothetical and based on historical data. They do not guarantee future performance."
      >
        <BacktestRunTable />
      </SectionCard>
    </div>
  );
}
