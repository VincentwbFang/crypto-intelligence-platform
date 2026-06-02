import { render, screen, waitFor } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

import SystemPage from "@/app/system/page";

vi.mock("@/lib/api/system", () => ({
  getSystemHealth: () =>
    Promise.resolve({
      status: "ok",
      service: "crypto-intelligence-platform",
      version: "0.1.0",
      environment: "test"
    }),
  getSystemReady: () =>
    Promise.resolve({
      status: "ready",
      checks: { database: "ok", redis: "ok" }
    }),
  getSystemVersion: () =>
    Promise.resolve({
      version: "0.1.0",
      service: "crypto-intelligence-platform",
      environment: "test"
    })
}));

describe("SystemPage", () => {
  it("renders health readiness and version without secrets", async () => {
    render(<SystemPage />);
    await waitFor(() => expect(screen.getByText("API Health")).toBeInTheDocument());
    expect(screen.getByText("Readiness")).toBeInTheDocument();
    expect(screen.getByText("Version")).toBeInTheDocument();
    expect(screen.queryByText(/secret/i)).not.toBeInTheDocument();
  });
});

