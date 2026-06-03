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
  const loopItems = [...tickerItems, ...tickerItems];
  return (
    <div className="overflow-hidden rounded-lg border border-amber-200 bg-amber-50 px-4 py-3 text-sm text-amber-950">
      <div className="news-ticker-track flex w-max gap-6 whitespace-nowrap">
        {loopItems.map((item, index) => (
          <a
            aria-hidden={index >= tickerItems.length}
            className="shrink-0 hover:underline"
            href={item.url}
            key={`${item.id}-${index}`}
            rel="noreferrer"
            tabIndex={index >= tickerItems.length ? -1 : 0}
            target="_blank"
          >
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
