"use client";

import { useEffect, useState } from "react";
import { Database, RefreshCw } from "lucide-react";

import { CandleStats } from "@/components/market/CandleStats";
import { MarketSnapshotCard } from "@/components/market/MarketSnapshotCard";
import { OHLCVChart } from "@/components/market/OHLCVChart";
import { EmptyState } from "@/components/common/EmptyState";
import { ErrorState } from "@/components/common/ErrorState";
import { LoadingState } from "@/components/common/LoadingState";
import { SectionCard } from "@/components/common/SectionCard";
import { Button } from "@/components/ui/button";
import { Select } from "@/components/ui/select";
import {
  backfillMarketData,
  getMarketSnapshot,
  getMarketUniverse,
  getOHLCV,
  ingestMarketData
} from "@/lib/api/market";
import { TOP_30_MARKET_SYMBOLS } from "@/lib/market-universe";
import type { MarketBackfillResponse, MarketSnapshot, OHLCVRow } from "@/lib/api/types";

const fallbackSymbols = TOP_30_MARKET_SYMBOLS;

export function MarketExplorer() {
  const [symbol, setSymbol] = useState("BTC/USDT");
  const [symbols, setSymbols] = useState(fallbackSymbols);
  const [timeframe, setTimeframe] = useState("1h");
  const [snapshot, setSnapshot] = useState<MarketSnapshot | null>(null);
  const [rows, setRows] = useState<OHLCVRow[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isIngesting, setIsIngesting] = useState(false);
  const [isBackfilling, setIsBackfilling] = useState(false);
  const [message, setMessage] = useState<string | null>(null);
  const [backfillResult, setBackfillResult] = useState<MarketBackfillResponse | null>(null);
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

  async function handleBackfillSmoke() {
    setIsBackfilling(true);
    setMessage(null);
    setBackfillResult(null);
    setError(null);
    try {
      const result = await backfillMarketData({
        exchange: "okx",
        symbols: null,
        use_top_market_cap: true,
        top_n: 30,
        timeframe: "1h",
        years: 3,
        batch_limit: 300,
        max_batches_per_symbol: 1
      });
      const inserted = Object.values(result.results).reduce(
        (total, item) => total + item.inserted,
        0
      );
      setBackfillResult(result);
      setMessage(
        `Top 30 smoke backfill completed. ${inserted} new candles inserted across ${result.symbols.length} symbols.`
      );
      await loadData();
    } catch (backfillError) {
      setError(backfillError instanceof Error ? backfillError.message : "Backfill failed.");
    } finally {
      setIsBackfilling(false);
    }
  }

  useEffect(() => {
    getMarketUniverse("okx", 30)
      .then((universe) => {
        if (universe.symbols.length) {
          setSymbols(universe.symbols);
        }
      })
      .catch(() => {
        setSymbols(fallbackSymbols);
      });
  }, []);

  useEffect(() => {
    void loadData();
  }, [symbol, timeframe]);

  return (
    <div className="space-y-6">
      <SectionCard title="Market Controls">
        <div className="grid gap-3 lg:grid-cols-[180px_120px_auto_auto]">
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
          <Button disabled={isBackfilling} onClick={handleBackfillSmoke} variant="outline">
            <Database className="h-4 w-4" />
            {isBackfilling ? "Backfilling" : "Smoke Backfill Top 30"}
          </Button>
        </div>
        <p className="mt-3 text-sm text-muted-foreground">
          The default universe focuses on the top 30 major USDT pairs. The smoke
          backfill runs one batch per symbol; use the API for a full three-year
          historical backfill.
        </p>
        {message ? <p className="mt-3 text-sm text-muted-foreground">{message}</p> : null}
        {backfillResult ? (
          <div className="mt-3 max-h-36 overflow-auto rounded-md border bg-muted/30 p-3 text-xs text-muted-foreground">
            {Object.entries(backfillResult.results).map(([resultSymbol, result]) => (
              <div key={resultSymbol}>
                {resultSymbol}: inserted {result.inserted}, fetched {result.fetched}
                {result.error ? `, error: ${result.error}` : ""}
              </div>
            ))}
          </div>
        ) : null}
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
