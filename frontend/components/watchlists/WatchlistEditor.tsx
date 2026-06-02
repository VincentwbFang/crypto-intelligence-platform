"use client";

import { useEffect, useState } from "react";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { WatchlistSelector } from "@/components/watchlists/WatchlistSelector";
import { WatchlistSymbolTable } from "@/components/watchlists/WatchlistSymbolTable";
import { addWatchlistSymbol, listWatchlists, removeWatchlistSymbol } from "@/lib/api/watchlists";
import type { Watchlist } from "@/lib/api/types";

export function WatchlistEditor() {
  const [watchlists, setWatchlists] = useState<Watchlist[]>([]);
  const [selectedId, setSelectedId] = useState("");
  const [symbol, setSymbol] = useState("");
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    listWatchlists()
      .then((response) => {
        setWatchlists(response.data);
        setSelectedId(response.data[0]?.watchlist_id ?? "");
      })
      .catch((error_) => setError(error_ instanceof Error ? error_.message : "Could not load watchlists."));
  }, []);

  const selected = watchlists.find((watchlist) => watchlist.watchlist_id === selectedId);

  async function refresh(updated: Watchlist) {
    setWatchlists((items) => items.map((item) => (item.watchlist_id === updated.watchlist_id ? updated : item)));
  }

  async function addSymbol(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!selectedId || !symbol.trim()) {
      return;
    }
    try {
      setError(null);
      await refresh(await addWatchlistSymbol(selectedId, symbol));
      setSymbol("");
    } catch (error_) {
      setError(error_ instanceof Error ? error_.message : "Your current plan has reached the watchlist symbol limit.");
    }
  }

  async function removeSymbol(symbolToRemove: string) {
    if (!selectedId) {
      return;
    }
    await refresh(await removeWatchlistSymbol(selectedId, symbolToRemove));
  }

  return (
    <section className="space-y-4">
      <div className="flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
        <WatchlistSelector onChange={setSelectedId} value={selectedId} watchlists={watchlists} />
        <form className="flex gap-2" onSubmit={addSymbol}>
          <Input onChange={(event) => setSymbol(event.target.value)} placeholder="BTC/USDT" value={symbol} />
          <Button type="submit">Add symbol</Button>
        </form>
      </div>
      {error ? <p className="text-sm text-destructive">{error}</p> : null}
      <WatchlistSymbolTable onRemove={removeSymbol} symbols={selected?.symbols ?? []} />
    </section>
  );
}
