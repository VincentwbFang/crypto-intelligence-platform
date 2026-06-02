"use client";

import type { Watchlist } from "@/lib/api/types";

export function WatchlistSelector({
  watchlists,
  value,
  onChange
}: {
  watchlists: Watchlist[];
  value: string;
  onChange: (watchlistId: string) => void;
}) {
  return (
    <select
      className="h-10 rounded-md border bg-background px-3 text-sm"
      onChange={(event) => onChange(event.target.value)}
      value={value}
    >
      {watchlists.map((watchlist) => (
        <option key={watchlist.watchlist_id} value={watchlist.watchlist_id}>
          {watchlist.name}
        </option>
      ))}
    </select>
  );
}
