"use client";

import { useEffect, useState } from "react";

import { EmptyState } from "@/components/common/EmptyState";
import { ErrorState } from "@/components/common/ErrorState";
import { LoadingState } from "@/components/common/LoadingState";
import { SignalRankTable } from "@/components/signals/SignalRankTable";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Select } from "@/components/ui/select";
import { rankSignals } from "@/lib/api/signals";
import { TOP_30_MARKET_SYMBOLS_TEXT } from "@/lib/market-universe";
import type { SignalResponse } from "@/lib/api/types";

export function SignalRankExplorer() {
  const [symbols, setSymbols] = useState(TOP_30_MARKET_SYMBOLS_TEXT);
  const [timeframe, setTimeframe] = useState("1h");
  const [signals, setSignals] = useState<SignalResponse[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  async function loadRankings() {
    setIsLoading(true);
    setError(null);
    try {
      const result = await rankSignals(
        symbols.split(",").map((symbol) => symbol.trim()).filter(Boolean),
        timeframe,
        200
      );
      setSignals(result.data);
    } catch (rankError) {
      setSignals([]);
      setError(rankError instanceof Error ? rankError.message : "Signal ranking failed.");
    } finally {
      setIsLoading(false);
    }
  }

  useEffect(() => {
    void loadRankings();
  }, []);

  return (
    <div className="space-y-6">
      <form
        className="grid gap-3 rounded-lg border bg-card p-4 md:grid-cols-[1fr_120px_auto]"
        onSubmit={(event) => {
          event.preventDefault();
          void loadRankings();
        }}
      >
        <Input
          aria-label="Symbols"
          onChange={(event) => setSymbols(event.target.value)}
          value={symbols}
        />
        <Select
          aria-label="Timeframe"
          onChange={(event) => setTimeframe(event.target.value)}
          value={timeframe}
        >
          <option value="1h">1h</option>
          <option value="4h">4h</option>
          <option value="1d">1d</option>
        </Select>
        <Button type="submit">Refresh Rankings</Button>
      </form>
      {error ? <ErrorState message={error} /> : null}
      {isLoading ? <LoadingState label="Loading signal rankings" /> : null}
      {!isLoading && !signals.length && !error ? <EmptyState /> : null}
      {!isLoading && signals.length ? <SignalRankTable signals={signals} /> : null}
    </div>
  );
}
