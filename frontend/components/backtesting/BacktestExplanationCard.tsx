import { SectionCard } from "@/components/common/SectionCard";
import type { AIBacktestExplanation } from "@/lib/api/types";

export function BacktestExplanationCard({
  explanation
}: {
  explanation: AIBacktestExplanation;
}) {
  if (!explanation.enabled) {
    return (
      <SectionCard title="AI Backtest Explanation">
        <p className="text-sm text-muted-foreground">
          {explanation.message || "AI backtest explanation is disabled."}
        </p>
      </SectionCard>
    );
  }

  return (
    <SectionCard
      title="AI Backtest Explanation"
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
          {explanation.plain_english_summary ? <p>{explanation.plain_english_summary}</p> : null}
          <List title="Performance Interpretation" items={explanation.performance_interpretation} />
          <List title="Risk Interpretation" items={explanation.risk_interpretation} />
          <List title="Strategy Behavior" items={explanation.strategy_behavior} />
          <List title="Main Weaknesses" items={explanation.main_weaknesses} />
          <List title="What To Validate Next" items={explanation.what_to_validate_next} />
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
