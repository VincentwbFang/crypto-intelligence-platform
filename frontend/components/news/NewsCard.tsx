"use client";

import type { NewsItem } from "@/lib/api/types";
import { formatDateTime, formatScore } from "@/lib/format";
import { cn } from "@/lib/utils";

export function NewsCard({ item }: { item: NewsItem }) {
  const analysis = item.analysis;
  const summary = analysis?.ai_summary_json;
  return (
    <article className="rounded-lg border bg-background p-4">
      <div className="flex flex-col gap-3 md:flex-row md:items-start md:justify-between">
        <div>
          <a className="font-semibold hover:underline" href={item.url} rel="noreferrer" target="_blank">
            {summary?.headline_cn || item.title}
          </a>
          <p className="mt-1 text-xs text-muted-foreground">
            {item.source} · {formatDateTime(item.published_at)}
            {item.published_at_estimated ? " · estimated time" : ""}
          </p>
        </div>
        {analysis ? <UrgencyBadge urgency={analysis.urgency_level} /> : null}
      </div>
      <p className="mt-3 text-sm text-muted-foreground">
        {summary?.summary_cn || item.summary_raw || "暂无摘要。"}
      </p>
      {summary?.why_it_matters ? (
        <p className="mt-2 text-sm">
          <span className="font-medium">为什么重要：</span>
          {summary.why_it_matters}
        </p>
      ) : null}
      <div className="mt-3 flex flex-wrap gap-2 text-xs">
        {(analysis?.symbols || []).map((symbol) => (
          <span className="rounded-full border bg-muted px-2 py-1" key={symbol}>
            {symbol}
          </span>
        ))}
        {(analysis?.sectors || []).map((sector) => (
          <span className="rounded-full border bg-card px-2 py-1" key={sector}>
            {sector}
          </span>
        ))}
      </div>
      {analysis ? (
        <div className="mt-3 grid gap-2 text-xs text-muted-foreground sm:grid-cols-3">
          <span>Impact {formatScore(analysis.impact_score)}</span>
          <span>Sentiment {analysis.impact_direction}</span>
          <span>Relevance {formatScore(analysis.relevance_score)}</span>
        </div>
      ) : null}
    </article>
  );
}

function UrgencyBadge({ urgency }: { urgency: string }) {
  return (
    <span
      className={cn(
        "inline-flex rounded-full border px-2 py-1 text-xs font-medium",
        urgency === "critical" && "border-red-200 bg-red-50 text-red-700",
        urgency === "high" && "border-amber-200 bg-amber-50 text-amber-800",
        urgency === "medium" && "border-sky-200 bg-sky-50 text-sky-700",
        urgency === "low" && "border-slate-200 bg-slate-50 text-slate-600"
      )}
    >
      {urgency}
    </span>
  );
}
