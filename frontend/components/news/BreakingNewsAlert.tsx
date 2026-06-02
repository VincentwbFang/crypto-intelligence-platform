"use client";

import type { NewsAlert } from "@/lib/api/types";
import { formatDateTime } from "@/lib/format";

export function BreakingNewsAlert({ alerts }: { alerts: NewsAlert[] }) {
  const critical = alerts.find((alert) => alert.severity === "critical") ?? alerts[0];
  if (!critical) {
    return null;
  }
  return (
    <div className="rounded-lg border border-red-200 bg-red-50 p-4 text-red-950">
      <div className="flex flex-col gap-2 md:flex-row md:items-start md:justify-between">
        <div>
          <p className="text-sm font-semibold">重大新闻警告</p>
          <p className="mt-1 text-sm whitespace-pre-line">{critical.message_cn}</p>
        </div>
        <p className="shrink-0 text-xs text-red-800">{formatDateTime(critical.created_at)}</p>
      </div>
    </div>
  );
}
