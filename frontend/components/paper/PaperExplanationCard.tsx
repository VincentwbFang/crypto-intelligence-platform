import { EmptyState } from "@/components/common/EmptyState";
import type { AIPaperTradingExplanation } from "@/lib/api/types";

export function PaperExplanationCard({
  explanation
}: {
  explanation: AIPaperTradingExplanation | null;
}) {
  if (!explanation) {
    return <EmptyState message="No AI paper trading explanation loaded." />;
  }
  if (!explanation.enabled) {
    return <EmptyState message={explanation.message ?? "AI paper trading explanation is disabled."} />;
  }
  return (
    <div className="space-y-4 text-sm">
      {explanation.compliance_warnings?.length ? (
        <div className="rounded-md border border-amber-300 bg-amber-50 p-3 text-amber-900">
          Some AI wording was sanitized by compliance guardrails.
        </div>
      ) : null}
      <p>{explanation.plain_english_summary}</p>
      <List title="Performance Observations" items={explanation.performance_observations} />
      <List title="Risk Observations" items={explanation.risk_observations} />
      <List title="Position Notes" items={explanation.position_notes} />
      <List title="What To Monitor" items={explanation.what_to_monitor} />
      <p className="text-muted-foreground">{explanation.disclaimer}</p>
    </div>
  );
}

function List({ title, items }: { title: string; items?: string[] | null }) {
  if (!items?.length) {
    return null;
  }
  return (
    <div>
      <h3 className="font-medium">{title}</h3>
      <ul className="mt-2 list-disc space-y-1 pl-5 text-muted-foreground">
        {items.map((item) => (
          <li key={item}>{item}</li>
        ))}
      </ul>
    </div>
  );
}
