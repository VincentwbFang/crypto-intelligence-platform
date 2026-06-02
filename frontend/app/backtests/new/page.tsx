import { BacktestForm } from "@/components/backtesting/BacktestForm";
import { SectionCard } from "@/components/common/SectionCard";
import { PageHeader } from "@/components/layout/PageHeader";

export default function NewBacktestPage() {
  return (
    <div>
      <PageHeader
        title="Run Research Backtest"
        description="Evaluate a deterministic long-only strategy on stored historical OHLCV candles."
      />
      <SectionCard
        title="Backtest Configuration"
        description="Backtest results are hypothetical and based on historical data. They do not guarantee future performance."
      >
        <BacktestForm />
      </SectionCard>
    </div>
  );
}
