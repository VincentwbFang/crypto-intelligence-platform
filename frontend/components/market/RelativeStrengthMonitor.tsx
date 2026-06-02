"use client";

import { useEffect, useMemo, useState } from "react";

import { EmptyState } from "@/components/common/EmptyState";
import { ErrorState } from "@/components/common/ErrorState";
import { LoadingState } from "@/components/common/LoadingState";
import { SectionCard } from "@/components/common/SectionCard";
import { StatCard } from "@/components/common/StatCard";
import {
  getRelativeStrengthHistory,
  getRelativeStrengthRanking,
  listRelativeStrengthAlerts,
  markRelativeStrengthAlertRead
} from "@/lib/api/market-comparison";
import type { RelativeStrengthAlert, RelativeStrengthSnapshot } from "@/lib/api/types";
import { formatDateTime, formatPercent, formatPrice, formatScore } from "@/lib/format";
import { cn } from "@/lib/utils";

type SortKey =
  | "symbol"
  | "brsi_score"
  | "excess_return_24h"
  | "excess_return_7d"
  | "excess_return_30d"
  | "brsi_change_1h"
  | "status";

export function RelativeStrengthMonitor() {
  const [ranking, setRanking] = useState<RelativeStrengthSnapshot[]>([]);
  const [alerts, setAlerts] = useState<RelativeStrengthAlert[]>([]);
  const [selectedSymbol, setSelectedSymbol] = useState<string | null>(null);
  const [history, setHistory] = useState<RelativeStrengthSnapshot[]>([]);
  const [sortKey, setSortKey] = useState<SortKey>("brsi_score");
  const [sortDirection, setSortDirection] = useState<"asc" | "desc">("desc");
  const [loading, setLoading] = useState(true);
  const [historyLoading, setHistoryLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let active = true;
    Promise.all([getRelativeStrengthRanking(100), listRelativeStrengthAlerts(12)])
      .then(([rankingResponse, alertResponse]) => {
        if (!active) {
          return;
        }
        setRanking(rankingResponse.data);
        setAlerts(alertResponse.data);
        setSelectedSymbol(rankingResponse.data[0]?.symbol ?? null);
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

  useEffect(() => {
    if (!selectedSymbol) {
      setHistory([]);
      return;
    }
    let active = true;
    setHistoryLoading(true);
    getRelativeStrengthHistory(selectedSymbol, 240)
      .then((response) => {
        if (active) {
          setHistory(response.data);
        }
      })
      .catch(() => {
        if (active) {
          setHistory([]);
        }
      })
      .finally(() => {
        if (active) {
          setHistoryLoading(false);
        }
      });
    return () => {
      active = false;
    };
  }, [selectedSymbol]);

  const sortedRanking = useMemo(() => {
    return [...ranking].sort((a, b) => {
      const direction = sortDirection === "asc" ? 1 : -1;
      const left = a[sortKey];
      const right = b[sortKey];
      if (typeof left === "string" || typeof right === "string") {
        return String(left ?? "").localeCompare(String(right ?? "")) * direction;
      }
      return ((left ?? -Infinity) - (right ?? -Infinity)) * direction;
    });
  }, [ranking, sortDirection, sortKey]);

  const strongest = ranking.find((item) => item.brsi_score !== null) ?? null;
  const weakest = useMemo(
    () =>
      [...ranking]
        .filter((item) => item.brsi_score !== null)
        .sort((a, b) => (a.brsi_score ?? 0) - (b.brsi_score ?? 0))[0] ?? null,
    [ranking]
  );
  const biggestChange = useMemo(
    () =>
      [...ranking]
        .filter((item) => item.brsi_change_1h !== null)
        .sort((a, b) => Math.abs(b.brsi_change_1h ?? 0) - Math.abs(a.brsi_change_1h ?? 0))[0] ??
      null,
    [ranking]
  );

  function updateSort(key: SortKey) {
    if (key === sortKey) {
      setSortDirection((current) => (current === "asc" ? "desc" : "asc"));
      return;
    }
    setSortKey(key);
    setSortDirection(key === "symbol" || key === "status" ? "asc" : "desc");
  }

  async function markRead(alertId: number) {
    const updated = await markRelativeStrengthAlertRead(alertId);
    setAlerts((current) => current.map((alert) => (alert.id === alertId ? updated : alert)));
  }

  if (loading) {
    return <LoadingState label="Loading BTC relative strength monitor" />;
  }

  if (error) {
    return (
      <ErrorState
        message={`The relative strength monitor could not load. ${error}`}
        title="Relative strength unavailable"
      />
    );
  }

  if (!ranking.length) {
    return (
      <EmptyState
        title="No BRSI snapshots yet"
        message="Ingest 1h OHLCV data and run the relative strength scheduler to populate this monitor."
      />
    );
  }

  return (
    <div className="space-y-6">
      <div className="grid gap-4 lg:grid-cols-4">
        <StatCard
          label="Strongest vs BTC"
          value={strongest?.symbol ?? "N/A"}
          detail={`${formatScore(strongest?.brsi_score)} BRSI · ${strongest?.status ?? "N/A"}`}
        />
        <StatCard
          label="Weakest vs BTC"
          value={weakest?.symbol ?? "N/A"}
          detail={`${formatScore(weakest?.brsi_score)} BRSI · ${weakest?.status ?? "N/A"}`}
        />
        <StatCard
          label="Biggest 1h BRSI Change"
          value={biggestChange?.symbol ?? "N/A"}
          detail={`${formatScore(biggestChange?.brsi_change_1h)} points`}
        />
        <StatCard
          label="Recent RS Alerts"
          value={alerts.length}
          detail="Relative strength monitor alerts"
        />
      </div>

      <SectionCard
        title="Tracked Coin Ranking"
        description="BRSI compares each coin's multi-timeframe behavior against BTC on stored 1h candles."
      >
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y text-sm">
            <thead>
              <tr className="text-left text-xs uppercase text-muted-foreground">
                <SortableHeader label="Symbol" sortKey="symbol" onSort={updateSort} />
                <SortableHeader label="BRSI" sortKey="brsi_score" onSort={updateSort} />
                <SortableHeader label="Status" sortKey="status" onSort={updateSort} />
                <SortableHeader label="24h Excess" sortKey="excess_return_24h" onSort={updateSort} />
                <SortableHeader label="7d Excess" sortKey="excess_return_7d" onSort={updateSort} />
                <SortableHeader label="30d Excess" sortKey="excess_return_30d" onSort={updateSort} />
                <SortableHeader label="1h Change" sortKey="brsi_change_1h" onSort={updateSort} />
                <th className="px-3 py-2">Updated</th>
              </tr>
            </thead>
            <tbody className="divide-y">
              {sortedRanking.map((item) => (
                <tr
                  className={cn(
                    "cursor-pointer hover:bg-muted/50",
                    selectedSymbol === item.symbol && "bg-muted"
                  )}
                  key={item.symbol}
                  onClick={() => setSelectedSymbol(item.symbol)}
                >
                  <td className="px-3 py-3 font-medium">{item.symbol}</td>
                  <td className="px-3 py-3">{formatScore(item.brsi_score)}</td>
                  <td className="px-3 py-3">
                    <StatusBadge status={item.status} />
                  </td>
                  <td className="px-3 py-3">{formatPercent(item.excess_return_24h)}</td>
                  <td className="px-3 py-3">{formatPercent(item.excess_return_7d)}</td>
                  <td className="px-3 py-3">{formatPercent(item.excess_return_30d)}</td>
                  <td className="px-3 py-3">{formatScore(item.brsi_change_1h)}</td>
                  <td className="px-3 py-3">{formatDateTime(item.created_at)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </SectionCard>

      <div className="grid gap-6 xl:grid-cols-[1fr_360px]">
        <SectionCard
          title={selectedSymbol ? `${selectedSymbol} Detail Series` : "Detail Series"}
          description="Price, relative price, BRSI, and volume confirmation score."
        >
          {historyLoading ? (
            <LoadingState label="Loading symbol history" />
          ) : history.length ? (
            <RelativeStrengthChart data={history} />
          ) : (
            <EmptyState message="Select a symbol with stored relative strength snapshots." />
          )}
        </SectionCard>

        <SectionCard title="Recent Relative Strength Alerts">
          {alerts.length ? (
            <div className="space-y-3">
              {alerts.map((alert) => (
                <div className="rounded-md border bg-background p-3" key={alert.id}>
                  <div className="flex items-start justify-between gap-3">
                    <div>
                      <p className="text-sm font-semibold">{alert.title}</p>
                      <p className="mt-1 text-xs text-muted-foreground">
                        {alert.symbol} · {alert.alert_level} · {formatDateTime(alert.created_at)}
                      </p>
                    </div>
                    {!alert.is_read ? (
                      <button
                        className="text-xs font-medium text-primary"
                        onClick={() => markRead(alert.id)}
                        type="button"
                      >
                        Mark read
                      </button>
                    ) : null}
                  </div>
                  <p className="mt-2 text-sm text-muted-foreground">{alert.message}</p>
                </div>
              ))}
            </div>
          ) : (
            <EmptyState message="No relative strength alerts have been generated yet." />
          )}
        </SectionCard>
      </div>
    </div>
  );
}

function SortableHeader({
  label,
  sortKey,
  onSort
}: {
  label: string;
  sortKey: SortKey;
  onSort: (key: SortKey) => void;
}) {
  return (
    <th className="px-3 py-2">
      <button className="font-medium hover:text-foreground" onClick={() => onSort(sortKey)} type="button">
        {label}
      </button>
    </th>
  );
}

function StatusBadge({ status }: { status: string }) {
  const normalized = status.toLowerCase();
  return (
    <span
      className={cn(
        "inline-flex rounded-full border px-2 py-1 text-xs font-medium",
        normalized.includes("strong") && !normalized.includes("weak")
          ? "border-emerald-200 bg-emerald-50 text-emerald-700"
          : null,
        normalized.includes("weak") ? "border-amber-200 bg-amber-50 text-amber-800" : null,
        normalized.includes("insufficient") ? "border-slate-200 bg-slate-50 text-slate-600" : null
      )}
    >
      {status}
    </span>
  );
}

function RelativeStrengthChart({ data }: { data: RelativeStrengthSnapshot[] }) {
  const lines = [
    { key: "price", label: "Price", color: "#0f766e", formatter: formatPrice },
    { key: "relative_price", label: "Relative Price", color: "#2563eb", formatter: formatSmallNumber },
    { key: "brsi_score", label: "BRSI", color: "#9333ea", formatter: formatScore },
    { key: "volume_score", label: "Volume Score", color: "#ea580c", formatter: formatScore }
  ] as const;

  return (
    <div className="grid gap-4 md:grid-cols-2">
      {lines.map((line) => (
        <div className="rounded-md border bg-background p-4" key={line.key}>
          <div className="flex items-center justify-between gap-3">
            <p className="text-sm font-semibold">{line.label}</p>
            <p className="text-sm text-muted-foreground">
              {line.formatter(data[data.length - 1]?.[line.key])}
            </p>
          </div>
          <MiniLineChart color={line.color} data={data.map((item) => item[line.key])} />
        </div>
      ))}
    </div>
  );
}

function MiniLineChart({ data, color }: { data: Array<number | null>; color: string }) {
  const valid = data
    .map((value, index) => ({ value, index }))
    .filter((point): point is { value: number; index: number } => point.value !== null);
  if (valid.length < 2) {
    return <div className="mt-4 text-sm text-muted-foreground">Not enough chart data.</div>;
  }
  const values = valid.map((point) => point.value);
  const min = Math.min(...values);
  const max = Math.max(...values);
  const width = 320;
  const height = 110;
  const path = valid
    .map((point, position) => {
      const x = (position / (valid.length - 1)) * width;
      const y = height - ((point.value - min) / (max - min || 1)) * height;
      return `${position === 0 ? "M" : "L"} ${x.toFixed(2)} ${y.toFixed(2)}`;
    })
    .join(" ");
  return (
    <svg
      aria-label="Relative strength metric trend"
      className="mt-4 h-32 w-full"
      preserveAspectRatio="none"
      viewBox={`0 0 ${width} ${height}`}
    >
      <path d={path} fill="none" stroke={color} strokeLinecap="round" strokeWidth="3" />
    </svg>
  );
}

function formatSmallNumber(value: number | null | undefined) {
  if (value === null || value === undefined || Number.isNaN(value)) {
    return "N/A";
  }
  return value.toFixed(8);
}
