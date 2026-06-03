"use client";

import { useCallback, useEffect, useMemo, useState } from "react";

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
const DEFAULT_NEWS_POLL_INTERVAL_MS = 30000;

export function NewsBroadcastPanel() {
  const [news, setNews] = useState<NewsItem[]>([]);
  const [alerts, setAlerts] = useState<NewsAlert[]>([]);
  const [briefings, setBriefings] = useState<Record<string, NewsBroadcast | null>>({});
  const [symbol, setSymbol] = useState("ALL");
  const [urgency, setUrgency] = useState("all");
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [lastUpdatedAt, setLastUpdatedAt] = useState<Date | null>(null);
  const [error, setError] = useState<string | null>(null);
  const pollIntervalMs = getNewsPollIntervalMs();

  const loadNews = useCallback(
    async (isInitialLoad = false, isMounted: () => boolean = () => true) => {
      if (isInitialLoad) {
        setLoading(true);
      } else {
        setRefreshing(true);
      }
      try {
        const [latest, alertResponse, morning, intraday, breaking] = await Promise.all([
          getLatestNews({ limit: 30 }),
          getNewsAlerts(10),
          getNewsBriefing("morning"),
          getNewsBriefing("intraday"),
          getNewsBriefing("breaking")
        ]);
        if (!isMounted()) {
          return;
        }
        setNews(latest.data);
        setAlerts(alertResponse.data);
        setBriefings({
          morning: morning.data,
          intraday: intraday.data,
          breaking: breaking.data
        });
        setLastUpdatedAt(new Date());
        setError(null);
      } catch (err) {
        if (isMounted()) {
          setError(err instanceof Error ? err.message : "News refresh failed.");
        }
      } finally {
        if (isMounted()) {
          setLoading(false);
          setRefreshing(false);
        }
      }
    },
    []
  );

  useEffect(() => {
    let active = true;
    const isMounted = () => active;
    void loadNews(true, isMounted);
    const interval = window.setInterval(() => {
      void loadNews(false, isMounted);
    }, pollIntervalMs);
    return () => {
      active = false;
      window.clearInterval(interval);
    };
  }, [loadNews, pollIntervalMs]);

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

  if (loading && !news.length) {
    return <LoadingState label="Loading news broadcast" />;
  }
  if (error && !news.length) {
    return <ErrorState title="News unavailable" message={error} />;
  }

  return (
    <div className="space-y-5">
      <BreakingNewsAlert alerts={alerts} />
      <NewsTicker items={news} />
      <SectionCard
        title="News Broadcast"
        description="Live-updating Chinese briefings and rule-based crypto news impact analysis."
      >
        <div className="mb-4 flex flex-col gap-2 rounded-lg border bg-muted/40 px-3 py-2 text-xs text-muted-foreground sm:flex-row sm:items-center sm:justify-between">
          <span>
            <span className="mr-2 inline-flex h-2 w-2 rounded-full bg-emerald-500" />
            实时新闻流 · 每 {Math.round(pollIntervalMs / 1000)} 秒自动更新
          </span>
          <span>
            {refreshing ? "正在更新..." : "最后更新 "}
            {!refreshing && lastUpdatedAt ? formatDateTime(lastUpdatedAt.toISOString()) : null}
          </span>
        </div>
        {error ? (
          <div className="mb-4 rounded-lg border border-amber-200 bg-amber-50 px-3 py-2 text-xs text-amber-900">
            最新一轮更新失败：{error}。页面继续展示最近一次成功获取的新闻。
          </div>
        ) : null}
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
          <div className="max-h-[680px] space-y-3 overflow-y-auto pr-2">
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

function getNewsPollIntervalMs() {
  const rawValue = process.env.NEXT_PUBLIC_NEWS_POLL_INTERVAL_MS;
  const parsed = rawValue ? Number.parseInt(rawValue, 10) : DEFAULT_NEWS_POLL_INTERVAL_MS;
  if (!Number.isFinite(parsed)) {
    return DEFAULT_NEWS_POLL_INTERVAL_MS;
  }
  return Math.max(5000, parsed);
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
