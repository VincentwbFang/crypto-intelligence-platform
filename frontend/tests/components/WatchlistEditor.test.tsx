import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";

import { WatchlistEditor } from "@/components/watchlists/WatchlistEditor";
import { addWatchlistSymbol, removeWatchlistSymbol } from "@/lib/api/watchlists";

const { watchlist } = vi.hoisted(() => ({
  watchlist: {
  watchlist_id: "wl1",
  workspace_id: "w1",
  name: "Default",
  created_by_user_id: "u1",
  symbols: [{ symbol: "BTC/USDT", display_order: 0 }]
  }
}));

vi.mock("@/lib/api/watchlists", () => ({
  listWatchlists: vi.fn().mockResolvedValue({ data: [watchlist] }),
  addWatchlistSymbol: vi.fn().mockResolvedValue({
    ...watchlist,
    symbols: [...watchlist.symbols, { symbol: "ETH/USDT", display_order: 1 }]
  }),
  removeWatchlistSymbol: vi.fn().mockResolvedValue({ ...watchlist, symbols: [] })
}));

describe("WatchlistEditor", () => {
  it("adds and removes symbols", async () => {
    render(<WatchlistEditor />);
    expect(await screen.findByText("BTC/USDT")).toBeInTheDocument();
    await userEvent.type(screen.getByPlaceholderText("BTC/USDT"), "ETH/USDT");
    await userEvent.click(screen.getByText("Add symbol"));
    expect(addWatchlistSymbol).toHaveBeenCalledWith("wl1", "ETH/USDT");
    await userEvent.click(screen.getAllByText("Remove")[0]);
    expect(removeWatchlistSymbol).toHaveBeenCalledWith("wl1", "BTC/USDT");
  });
});
