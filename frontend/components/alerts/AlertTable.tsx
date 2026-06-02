"use client";

import Link from "next/link";

import { EmptyState } from "@/components/common/EmptyState";
import { Button } from "@/components/ui/button";
import { AlertSeverityBadge } from "@/components/alerts/AlertSeverityBadge";
import { AlertStatusBadge } from "@/components/alerts/AlertStatusBadge";
import { AlertTypeBadge } from "@/components/alerts/AlertTypeBadge";
import { RiskLevelBadge } from "@/components/signals/RiskLevelBadge";
import type { AlertResponse } from "@/lib/api/types";
import { formatDateTime, formatScore } from "@/lib/format";

type AlertTableProps = {
  alerts: AlertResponse[];
  onAcknowledge?: (alertId: number) => void;
  onResolve?: (alertId: number) => void;
  onDismiss?: (alertId: number) => void;
};

export function AlertTable({
  alerts,
  onAcknowledge,
  onResolve,
  onDismiss
}: AlertTableProps) {
  if (!alerts.length) {
    return <EmptyState message="No alerts match the current filters." />;
  }

  return (
    <div className="overflow-x-auto rounded-lg border bg-card">
      <table className="w-full min-w-[980px] text-left text-sm">
        <thead className="bg-muted">
          <tr>
            <th className="px-4 py-3 font-medium">Created At</th>
            <th className="px-4 py-3 font-medium">Symbol</th>
            <th className="px-4 py-3 font-medium">Timeframe</th>
            <th className="px-4 py-3 font-medium">Severity</th>
            <th className="px-4 py-3 font-medium">Alert Type</th>
            <th className="px-4 py-3 font-medium">Title</th>
            <th className="px-4 py-3 font-medium">Status</th>
            <th className="px-4 py-3 font-medium">Risk Level</th>
            <th className="px-4 py-3 font-medium">Signal Score</th>
            <th className="px-4 py-3 font-medium">Actions</th>
          </tr>
        </thead>
        <tbody>
          {alerts.map((alert) => (
            <tr className="border-t align-top" key={alert.id}>
              <td className="px-4 py-3 text-muted-foreground">
                {formatDateTime(alert.created_at)}
              </td>
              <td className="px-4 py-3 font-medium">{alert.symbol}</td>
              <td className="px-4 py-3">{alert.timeframe}</td>
              <td className="px-4 py-3">
                <AlertSeverityBadge severity={alert.severity} />
              </td>
              <td className="px-4 py-3">
                <AlertTypeBadge type={alert.alert_type} />
              </td>
              <td className="px-4 py-3">{alert.title}</td>
              <td className="px-4 py-3">
                <AlertStatusBadge status={alert.status} />
              </td>
              <td className="px-4 py-3">
                <RiskLevelBadge level={alert.risk_level} />
              </td>
              <td className="px-4 py-3">{formatScore(alert.signal_score)}</td>
              <td className="px-4 py-3">
                <div className="flex flex-wrap gap-2">
                  <Button asChild size="sm" variant="outline">
                    <Link href={`/alerts/${alert.id}`}>View</Link>
                  </Button>
                  <Button
                    aria-label={`Acknowledge alert ${alert.id}`}
                    onClick={() => onAcknowledge?.(alert.id)}
                    size="sm"
                    variant="secondary"
                  >
                    Acknowledge
                  </Button>
                  <Button
                    aria-label={`Resolve alert ${alert.id}`}
                    onClick={() => onResolve?.(alert.id)}
                    size="sm"
                    variant="secondary"
                  >
                    Resolve
                  </Button>
                  <Button
                    aria-label={`Dismiss alert ${alert.id}`}
                    onClick={() => onDismiss?.(alert.id)}
                    size="sm"
                    variant="ghost"
                  >
                    Dismiss
                  </Button>
                </div>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
