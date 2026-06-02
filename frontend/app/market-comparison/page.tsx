import { PageHeader } from "@/components/layout/PageHeader";
import { RelativeStrengthMonitor } from "@/components/market/RelativeStrengthMonitor";

export default function MarketComparisonPage() {
  return (
    <div>
      <PageHeader
        title="BTC Relative Strength Monitor"
        description="Compare tracked major coins against BTC with BRSI rankings, relative movement alerts, and historical context."
      />
      <RelativeStrengthMonitor />
      <p className="mt-6 text-xs text-muted-foreground">
        This platform provides data-driven market intelligence for educational and research
        purposes only. It is not personalized financial advice.
      </p>
    </div>
  );
}
