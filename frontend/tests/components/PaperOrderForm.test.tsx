import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";

import { PaperOrderForm } from "@/components/paper/PaperOrderForm";

vi.mock("@/lib/api/paper", () => ({
  submitPaperOrder: vi.fn().mockResolvedValue({
    order_id: "order-1",
    account_id: "account-1",
    symbol: "BTC/USDT",
    timeframe: "1h",
    side: "buy",
    order_type: "market",
    notional: 500,
    status: "filled"
  })
}));

describe("PaperOrderForm", () => {
  it("renders fields", () => {
    render(<PaperOrderForm accountId="account-1" />);
    expect(screen.getByLabelText("Symbol")).toBeInTheDocument();
    expect(screen.getByText("Submit simulated order")).toBeInTheDocument();
  });

  it("validates notional", async () => {
    render(<PaperOrderForm accountId="account-1" />);
    await userEvent.clear(screen.getByLabelText("Notional"));
    await userEvent.type(screen.getByLabelText("Notional"), "0");
    await userEvent.click(screen.getByText("Submit simulated order"));
    expect(screen.getByText("Enter a positive simulated notional amount.")).toBeInTheDocument();
  });

  it("submits simulated order", async () => {
    const onSubmitted = vi.fn();
    render(<PaperOrderForm accountId="account-1" onSubmitted={onSubmitted} />);
    await userEvent.click(screen.getByText("Submit simulated order"));
    expect(await screen.findByText("Submit simulated order")).toBeInTheDocument();
    expect(onSubmitted).toHaveBeenCalled();
  });
});
