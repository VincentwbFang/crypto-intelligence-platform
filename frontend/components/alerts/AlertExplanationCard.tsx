import type { AIExplanationResponse } from "@/lib/api/types";

import { SectionCard } from "@/components/common/SectionCard";

export function AlertExplanationCard({
  explanation
}: {
  explanation: AIExplanationResponse;
}) {
  if (!explanation.enabled) {
    return (
      <SectionCard title="AI Alert Explanation">
        <p className="text-sm text-muted-foreground">
          {explanation.message || "AI alert explanation is disabled."}
        </p>
      </SectionCard>
    );
  }

  return (
    <SectionCard
      title="AI Alert Explanation"
      description={explanation.disclaimer || undefined}
    >
      {explanation.compliance_warnings?.length ? (
        <div className="mb-4 rounded-md border border-amber-200 bg-amber-50 p-3 text-sm text-amber-800">
          Some AI wording was sanitized by compliance guardrails.
        </div>
      ) : null}
      {explanation.error ? (
        <p className="text-sm text-red-700">{explanation.message || explanation.error}</p>
      ) : (
        <div className="space-y-4 text-sm">
          {explanation.plain_english_summary ? (
            <p>{explanation.plain_english_summary}</p>
          ) : null}
          <List title="Why Triggered" items={explanation.why_triggered} />
          <List title="Risk Context" items={explanation.risk_context} />
          <List title="What To Monitor" items={explanation.what_to_monitor} />
          <List title="Limitations" items={explanation.limitations} />
        </div>
      )}
    </SectionCard>
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
