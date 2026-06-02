import { PageHeader } from "@/components/layout/PageHeader";
import { SignalRankExplorer } from "@/components/signals/SignalRankExplorer";

export default function SignalsPage() {
  return (
    <div>
      <PageHeader
        title="Signal Ranking"
        description="Compare deterministic scores, relative strength, and risk levels across tracked symbols."
      />
      <SignalRankExplorer />
    </div>
  );
}
