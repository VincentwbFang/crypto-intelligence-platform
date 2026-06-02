import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { SystemStatusCard } from "@/components/system/SystemStatusCard";

describe("SystemStatusCard", () => {
  it("renders healthy state", () => {
    render(<SystemStatusCard environment="production" status="ready" title="Readiness" />);
    expect(screen.getByText("Readiness")).toBeInTheDocument();
    expect(screen.getByText("ready")).toBeInTheDocument();
    expect(screen.getByText("production")).toBeInTheDocument();
  });

  it("renders degraded state", () => {
    render(<SystemStatusCard detail="database: ok, redis: failed" status="not_ready" title="Readiness" />);
    expect(screen.getByText("not_ready")).toBeInTheDocument();
    expect(screen.getByText(/redis: failed/)).toBeInTheDocument();
  });

  it("renders unknown state safely", () => {
    render(<SystemStatusCard title="Metrics" />);
    expect(screen.getByText("unknown")).toBeInTheDocument();
  });
});

