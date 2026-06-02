"use client";

import type { NewsItem } from "@/lib/api/types";
import { formatDateTime } from "@/lib/format";

export function NewsTicker({ items }: { items: NewsItem[] }) {
  const tickerItems = items
    .filter((item) => ["high", "critical"].includes(item.analysis?.urgency_level || ""))
    .slice(0, 5);
  if (!tickerItems.length) {
    return null;
  }
  return (
    <div className="overflow-hidden rounded-lg border border-amber-200 bg-amber-50 px-4 py-3 text-sm text-amber-950">
      <div className="flex gap-6 overflow-x-auto whitespace-nowrap">
        {tickerItems.map((item) => (
          <a className="shrink-0 hover:underline" href={item.url} key={item.id} rel="noreferrer" target="_blank">
            <span className="font-semibold">{item.source}</span>
            <span className="mx-2">·</span>
            <span>{item.title}</span>
            <span className="mx-2">·</span>
            <span>{(item.analysis?.symbols || []).join(", ") || "MARKET"}</span>
            <span className="mx-2">·</span>
            <span>{item.analysis?.impact_direction || "neutral"}</span>
            <span className="mx-2">·</span>
            <span>{formatDateTime(item.published_at)}</span>
          </a>
        ))}
      </div>
    </div>
  );
}
