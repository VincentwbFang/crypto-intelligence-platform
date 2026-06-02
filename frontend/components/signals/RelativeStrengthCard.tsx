import type { RelativeStrengthResult } from "@/lib/api/types";

import { SectionCard } from "@/components/common/SectionCard";
import { formatPercent, formatScore } from "@/lib/format";

export function RelativeStrengthCard({
  relativeStrength
}: {
  relativeStrength: RelativeStrengthResult;
}) {
  return (
    <SectionCard title="Relative Strength" description={relativeStrength.explanation}>
      <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
        <Metric label="Score" value={formatScore(relativeStrength.relative_strength_score)} />
        <Metric label="24h Return" value={formatPercent(relativeStrength.return_24h)} />
        <Metric
          label="Reference 24h"
          value={formatPercent(relativeStrength.reference_return_24h)}
        />
        <Metric
          label="7d Relative"
          value={formatPercent(relativeStrength.relative_return_7d)}
        />
      </div>
    </SectionCard>
  );
}

function Metric({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-md border bg-background p-3">
      <p className="text-xs text-muted-foreground">{label}</p>
      <p className="mt-1 text-lg font-semibold">{value}</p>
    </div>
  );
}
