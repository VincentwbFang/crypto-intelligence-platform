"use client";

import { useEffect, useState } from "react";
import { RefreshCw } from "lucide-react";

import { CandleStats } from "@/components/market/CandleStats";
import { MarketSnapshotCard } from "@/components/market/MarketSnapshotCard";
import { OHLCVChart } from "@/components/market/OHLCVChart";
import { EmptyState } from "@/components/common/EmptyState";
import { ErrorState } from "@/components/common/ErrorState";
import { LoadingState } from "@/components/common/LoadingState";
import { SectionCard } from "@/components/common/SectionCard";
import { Button } from "@/components/ui/button";
import { Select } from "@/components/ui/select";
import { getMarketSnapshot, getOHLCV, ingestMarketData } from "@/lib/api/market";
import type { MarketSnapshot, OHLCVRow } from "@/lib/api/types";

const symbols = ["BTC/USDT", "ETH/USDT", "SOL/USDT"];

export function MarketExplorer() {
  const [symbol, setSymbol] = useState("BTC/USDT");
  const [timeframe, setTimeframe] = useState("1h");
  const [snapshot, setSnapshot] = useState<MarketSnapshot | null>(null);
  const [rows, setRows] = useState<OHLCVRow[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isIngesting, setIsIngesting] = useState(false);
  const [message, setMessage] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  async function loadData() {
    setIsLoading(true);
    setError(null);
    try {
      const [snapshotResponse, ohlcvResponse] = await Promise.all([
        getMarketSnapshot(symbol, timeframe),
        getOHLCV(symbol, timeframe, 200)
      ]);
      setSnapshot(snapshotResponse);
      setRows(ohlcvResponse.data);
    } catch (loadError) {
      setSnapshot(null);
      setRows([]);
      setError(loadError instanceof Error ? loadError.message : "Market data failed.");
    } finally {
      setIsLoading(false);
    }
  }

  async function handleIngest() {
    setIsIngesting(true);
    setMessage(null);
    setError(null);
    try {
      const result = await ingestMarketData({
        exchange: "okx",
        symbols,
        timeframe,
        limit: 200
      });
      setMessage(
        Object.entries(result.results)
          .map(([resultSymbol, count]) => `${resultSymbol}: ${count}`)
          .join(" · ")
      );
      await loadData();
    } catch (ingestError) {
      setError(ingestError instanceof Error ? ingestError.message : "Ingestion failed.");
    } finally {
      setIsIngesting(false);
    }
  }

  useEffect(() => {
    void loadData();
  }, [symbol, timeframe]);

  return (
    <div className="space-y-6">
      <SectionCard title="Market Controls">
        <div className="grid gap-3 md:grid-cols-[180px_120px_auto]">
          <Select
            aria-label="Symbol"
            onChange={(event) => setSymbol(event.target.value)}
            value={symbol}
          >
            {symbols.map((item) => (
              <option key={item} value={item}>
                {item}
              </option>
            ))}
          </Select>
          <Select
            aria-label="Timeframe"
            onChange={(event) => setTimeframe(event.target.value)}
            value={timeframe}
          >
            <option value="1h">1h</option>
            <option value="4h">4h</option>
            <option value="1d">1d</option>
          </Select>
          <Button disabled={isIngesting} onClick={handleIngest}>
            <RefreshCw className="h-4 w-4" />
            {isIngesting ? "Ingesting" : "Ingest Market Data"}
          </Button>
        </div>
        {message ? <p className="mt-3 text-sm text-muted-foreground">{message}</p> : null}
      </SectionCard>

      {error ? <ErrorState message={error} /> : null}
      {isLoading ? <LoadingState /> : null}
      {!isLoading && !snapshot && !error ? <EmptyState /> : null}
      {snapshot ? <MarketSnapshotCard snapshot={snapshot} /> : null}
      {rows.length ? <CandleStats rows={rows} /> : null}
      <SectionCard title="OHLCV Chart">
        <OHLCVChart rows={rows} />
      </SectionCard>
    </div>
  );
}
