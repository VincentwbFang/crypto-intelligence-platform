"use client";

import { useEffect, useMemo, useState } from "react";

import { EmptyState } from "@/components/common/EmptyState";
import { ErrorState } from "@/components/common/ErrorState";
import { LoadingState } from "@/components/common/LoadingState";
import { SectionCard } from "@/components/common/SectionCard";
import { Button } from "@/components/ui/button";
import { BreakingNewsAlert } from "@/components/news/BreakingNewsAlert";
import { NewsCard } from "@/components/news/NewsCard";
import { NewsTicker } from "@/components/news/NewsTicker";
import { SymbolNewsFilter } from "@/components/news/SymbolNewsFilter";
import { getLatestNews, getNewsAlerts, getNewsBriefing } from "@/lib/api/news";
import type { NewsAlert, NewsBroadcast, NewsItem } from "@/lib/api/types";
import { formatDateTime } from "@/lib/format";

const urgencyFilters = ["all", "critical", "high", "medium", "low"];

export function NewsBroadcastPanel() {
  const [news, setNews] = useState<NewsItem[]>([]);
  const [alerts, setAlerts] = useState<NewsAlert[]>([]);
  const [briefings, setBriefings] = useState<Record<string, NewsBroadcast | null>>({});
  const [symbol, setSymbol] = useState("ALL");
  const [urgency, setUrgency] = useState("all");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let active = true;
    Promise.all([
      getLatestNews({ limit: 30 }),
      getNewsAlerts(10),
      getNewsBriefing("morning"),
      getNewsBriefing("intraday"),
      getNewsBriefing("breaking")
    ])
      .then(([latest, alertResponse, morning, intraday, breaking]) => {
        if (!active) {
          return;
        }
        setNews(latest.data);
        setAlerts(alertResponse.data);
        setBriefings({
          morning: morning.data,
          intraday: intraday.data,
          breaking: breaking.data
        });
      })
      .catch((err: Error) => {
        if (active) {
          setError(err.message);
        }
      })
      .finally(() => {
        if (active) {
          setLoading(false);
        }
      });
    return () => {
      active = false;
    };
  }, []);

  const filteredNews = useMemo(() => {
    return news.filter((item) => {
      const analysis = item.analysis;
      if (symbol !== "ALL") {
        const symbols = analysis?.symbols || [];
        const sectors = analysis?.sectors || [];
        if (!symbols.includes(symbol) && !sectors.includes(symbol)) {
          return false;
        }
      }
      if (urgency !== "all" && analysis?.urgency_level !== urgency) {
        return false;
      }
      return true;
    });
  }, [news, symbol, urgency]);

  if (loading) {
    return <LoadingState label="Loading news broadcast" />;
  }
  if (error) {
    return <ErrorState title="News unavailable" message={error} />;
  }

  return (
    <div className="space-y-5">
      <BreakingNewsAlert alerts={alerts} />
      <NewsTicker items={news} />
      <SectionCard
        title="News Broadcast"
        description="AI-assisted Chinese news briefings and rule-based crypto news impact analysis."
      >
        <div className="grid gap-4 lg:grid-cols-3">
          <BriefingCard label="今日早报" briefing={briefings.morning} />
          <BriefingCard label="盘中快报" briefing={briefings.intraday} />
          <BriefingCard label="突发新闻" briefing={briefings.breaking} />
        </div>
      </SectionCard>

      <SectionCard
        title="Latest Crypto News"
        description="Filtered by recognized symbol, sector, and urgency level."
      >
        <div className="mb-4 space-y-3">
          <SymbolNewsFilter value={symbol} onChange={setSymbol} />
          <div className="flex flex-wrap gap-2">
            {urgencyFilters.map((item) => (
              <Button
                key={item}
                onClick={() => setUrgency(item)}
                size="sm"
                type="button"
                variant={urgency === item ? "default" : "outline"}
              >
                {item}
              </Button>
            ))}
          </div>
        </div>
        {filteredNews.length ? (
          <div className="space-y-3">
            {filteredNews.map((item) => (
              <NewsCard item={item} key={item.id} />
            ))}
          </div>
        ) : (
          <EmptyState message="No matching news yet. RSS and GDELT will populate this section after the scheduler runs." />
        )}
      </SectionCard>
      <p className="text-xs text-muted-foreground">
        This platform provides data-driven market intelligence for educational and research purposes
        only. It is not personalized financial advice.
      </p>
    </div>
  );
}

function BriefingCard({
  label,
  briefing
}: {
  label: string;
  briefing?: NewsBroadcast | null;
}) {
  return (
    <div className="rounded-lg border bg-background p-4">
      <p className="text-xs font-medium uppercase tracking-wide text-muted-foreground">{label}</p>
      <h3 className="mt-2 font-semibold">{briefing?.title || "暂无播报"}</h3>
      <p className="mt-2 whitespace-pre-line text-sm text-muted-foreground">
        {briefing?.content_cn || "等待定时任务生成新闻播报。"}
      </p>
      {briefing?.top_symbols?.length ? (
        <div className="mt-3 flex flex-wrap gap-2">
          {briefing.top_symbols.map((symbol) => (
            <span className="rounded-full border bg-muted px-2 py-1 text-xs" key={symbol}>
              {symbol}
            </span>
          ))}
        </div>
      ) : null}
      {briefing?.created_at ? (
        <p className="mt-3 text-xs text-muted-foreground">{formatDateTime(briefing.created_at)}</p>
      ) : null}
    </div>
  );
}
