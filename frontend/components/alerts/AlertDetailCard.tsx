import type { AlertResponse } from "@/lib/api/types";

import { SectionCard } from "@/components/common/SectionCard";
import { AlertSeverityBadge } from "@/components/alerts/AlertSeverityBadge";
import { AlertStatusBadge } from "@/components/alerts/AlertStatusBadge";
import { AlertTypeBadge } from "@/components/alerts/AlertTypeBadge";
import { RiskLevelBadge } from "@/components/signals/RiskLevelBadge";
import { formatDateTime, formatScore } from "@/lib/format";

export function AlertDetailCard({ alert }: { alert: AlertResponse }) {
  return (
    <SectionCard title={alert.title} description={alert.message}>
      <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
        <Meta label="Symbol" value={alert.symbol} />
        <Meta label="Timeframe" value={alert.timeframe} />
        <Meta label="Created" value={formatDateTime(alert.created_at)} />
        <Meta label="Signal Score" value={formatScore(alert.signal_score)} />
      </div>
      <div className="mt-4 flex flex-wrap gap-2">
        <AlertSeverityBadge severity={alert.severity} />
        <AlertStatusBadge status={alert.status} />
        <AlertTypeBadge type={alert.alert_type} />
        <RiskLevelBadge level={alert.risk_level} />
      </div>
      <details className="mt-5 rounded-md border bg-background p-4">
        <summary className="cursor-pointer text-sm font-medium">Raw payload</summary>
        <pre className="mt-3 max-h-80 overflow-auto text-xs text-muted-foreground">
          {JSON.stringify(alert.raw_payload ?? {}, null, 2)}
        </pre>
      </details>
    </SectionCard>
  );
}

function Meta({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-md border bg-background p-3">
      <p className="text-xs text-muted-foreground">{label}</p>
      <p className="mt-1 font-medium">{value}</p>
    </div>
  );
}
