import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { PaperPositionTable } from "@/components/paper/PaperPositionTable";

describe("PaperPositionTable", () => {
  it("renders positions", () => {
    render(
      <PaperPositionTable
        positions={[
          {
            account_id: "account-1",
            symbol: "BTC/USDT",
            quantity: 0.1,
            average_entry_price: 100,
            current_price: 110,
            market_value: 11,
            unrealized_pnl: 1,
            unrealized_pnl_pct: 10,
            status: "open"
          }
        ]}
      />
    );
    expect(screen.getByText("BTC/USDT")).toBeInTheDocument();
    expect(screen.getByText(/\+10.00%/)).toBeInTheDocument();
  });

  it("renders empty state", () => {
    render(<PaperPositionTable positions={[]} />);
    expect(screen.getByText("No open simulated positions.")).toBeInTheDocument();
  });
});
