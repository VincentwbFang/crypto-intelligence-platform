import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { PaperAccountCard } from "@/components/paper/PaperAccountCard";
import type { PaperAccount } from "@/lib/api/types";

const account: PaperAccount = {
  account_id: "account-1",
  name: "Main Paper Account",
  initial_balance: 10000,
  cash_balance: 9500,
  equity: 10100,
  realized_pnl: 50,
  unrealized_pnl: 50,
  total_fees: 3,
  status: "paused",
  created_at: "2026-05-27T00:00:00Z",
  updated_at: "2026-05-27T00:00:00Z"
};

describe("PaperAccountCard", () => {
  it("renders account summary", () => {
    render(<PaperAccountCard account={account} />);
    expect(screen.getByText("Main Paper Account")).toBeInTheDocument();
    expect(screen.getByText("$10,100.00")).toBeInTheDocument();
  });

  it("handles paused or closed status", () => {
    render(<PaperAccountCard account={{ ...account, status: "closed" }} />);
    expect(screen.getByText("closed")).toBeInTheDocument();
  });
});
