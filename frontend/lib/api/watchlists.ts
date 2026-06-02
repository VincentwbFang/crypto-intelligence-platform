import { apiFetch } from "@/lib/api/client";
import type { Watchlist } from "@/lib/api/types";

export function listWatchlists() {
  return apiFetch<{ data: Watchlist[] }>("/watchlists");
}

export function createWatchlist(request: { name: string }) {
  return apiFetch<Watchlist>("/watchlists", {
    method: "POST",
    body: request
  });
}

export function getWatchlist(watchlistId: string) {
  return apiFetch<Watchlist>(`/watchlists/${watchlistId}`);
}

export function addWatchlistSymbol(watchlistId: string, symbol: string) {
  return apiFetch<Watchlist>(`/watchlists/${watchlistId}/symbols`, {
    method: "POST",
    body: { symbol }
  });
}

export function removeWatchlistSymbol(watchlistId: string, symbol: string) {
  return apiFetch<Watchlist>(`/watchlists/${watchlistId}/symbols/${encodeURIComponent(symbol)}`, {
    method: "DELETE"
  });
}

export function reorderWatchlistSymbols(watchlistId: string, symbols: string[]) {
  return apiFetch<Watchlist>(`/watchlists/${watchlistId}/reorder`, {
    method: "PATCH",
    body: { symbols }
  });
}

export function deleteWatchlist(watchlistId: string) {
  return apiFetch<{ watchlist_id: string; deleted: boolean }>(`/watchlists/${watchlistId}`, {
    method: "DELETE"
  });
}
