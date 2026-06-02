import { SectionCard } from "@/components/common/SectionCard";
import { PageHeader } from "@/components/layout/PageHeader";

export default function SettingsPage() {
  const browserBase = process.env.NEXT_PUBLIC_API_BASE_URL || "/api/backend";
  const internalBase = process.env.BACKEND_INTERNAL_URL || "http://localhost:8000";

  return (
    <div>
      <PageHeader
        title="Settings"
        description="Read-only operational guide for the current frontend deployment."
      />
      <div className="space-y-6">
        <SectionCard title="API Connectivity">
          <dl className="grid gap-3 text-sm md:grid-cols-2">
            <div className="rounded-md border bg-background p-3">
              <dt className="text-muted-foreground">Browser API path</dt>
              <dd className="mt-1 font-mono">{browserBase}</dd>
            </div>
            <div className="rounded-md border bg-background p-3">
              <dt className="text-muted-foreground">Server-side backend URL</dt>
              <dd className="mt-1 font-mono">{internalBase}</dd>
            </div>
          </dl>
        </SectionCard>
        <SectionCard title="Feature Flags">
          <ul className="grid gap-3 text-sm md:grid-cols-2">
            {[
              ["ENABLE_AI_SIGNAL_EXPLANATION", "Optional signal explanation"],
              ["ENABLE_AI_ALERT_EXPLANATION", "Optional alert explanation"],
              ["ENABLE_AI_BACKTEST_EXPLANATION", "Optional backtest explanation"],
              ["ENABLE_AI_PAPER_TRADING_EXPLANATION", "Optional paper trading explanation"],
              ["ENABLE_SIGNAL_TO_PAPER_TRADE", "Research-only signal simulation"],
              ["ENABLE_ALERT_SCHEDULER", "Periodic alert evaluation"],
              ["ENABLE_WEBHOOK_NOTIFICATIONS", "Webhook alert delivery"]
            ].map(([key, description]) => (
              <li className="rounded-md border bg-background p-3" key={key}>
                <p className="font-mono text-xs text-muted-foreground">{key}</p>
                <p className="mt-1">{description}</p>
              </li>
            ))}
          </ul>
        </SectionCard>
        <SectionCard title="Environment Examples">
          <pre className="overflow-auto rounded-md bg-slate-950 p-4 text-xs text-slate-100">
            {`NEXT_PUBLIC_API_BASE_URL=
BACKEND_INTERNAL_URL=http://localhost:8000
ENABLE_AI_BACKTEST_EXPLANATION=false
ENABLE_AI_PAPER_TRADING_EXPLANATION=false
ENABLE_SIGNAL_TO_PAPER_TRADE=false

# Docker compose
BACKEND_INTERNAL_URL=http://backend:8000`}
          </pre>
        </SectionCard>
        <SectionCard title="Research-Only Notice">
          <p className="text-sm text-muted-foreground">
            This platform provides data-driven market intelligence for educational
            and research purposes only. It is not personalized financial advice.
          </p>
        </SectionCard>
      </div>
    </div>
  );
}
