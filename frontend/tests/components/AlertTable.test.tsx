import { fireEvent, render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

import { AlertTable } from "@/components/alerts/AlertTable";
import type { AlertResponse } from "@/lib/api/types";

const alerts: AlertResponse[] = [
  {
    id: 1,
    symbol: "BTC/USDT",
    timeframe: "1h",
    timestamp: "2026-05-27T12:00:00Z",
    alert_type: "high_risk",
    severity: "high",
    title: "Elevated risk detected",
    message: "Risk level increased for monitoring.",
    status: "open",
    source: "signal_engine",
    signal_score: 71,
    risk_level: "high",
    setup_type: "trend_continuation",
    dedup_key: "BTC/USDT:1h:high_risk:trend_continuation:high",
    raw_payload: {},
    created_at: "2026-05-27T12:00:00Z",
    updated_at: "2026-05-27T12:00:00Z",
    resolved_at: null
  }
];

describe("AlertTable", () => {
  it("renders alert rows", () => {
    render(<AlertTable alerts={alerts} />);

    expect(screen.getByText("BTC/USDT")).toBeInTheDocument();
    expect(screen.getByText("Elevated risk detected")).toBeInTheDocument();
  });

  it("renders empty state", () => {
    render(<AlertTable alerts={[]} />);

    expect(screen.getByText("No data yet")).toBeInTheDocument();
  });

  it("action buttons call handlers", () => {
    const onAcknowledge = vi.fn();
    const onResolve = vi.fn();
    const onDismiss = vi.fn();
    render(
      <AlertTable
        alerts={alerts}
        onAcknowledge={onAcknowledge}
        onDismiss={onDismiss}
        onResolve={onResolve}
      />
    );

    fireEvent.click(screen.getByLabelText("Acknowledge alert 1"));
    fireEvent.click(screen.getByLabelText("Resolve alert 1"));
    fireEvent.click(screen.getByLabelText("Dismiss alert 1"));

    expect(onAcknowledge).toHaveBeenCalledWith(1);
    expect(onResolve).toHaveBeenCalledWith(1);
    expect(onDismiss).toHaveBeenCalledWith(1);
  });
});
