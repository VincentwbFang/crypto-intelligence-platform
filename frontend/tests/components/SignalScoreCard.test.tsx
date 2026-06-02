import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { SignalScoreCard } from "@/components/signals/SignalScoreCard";

describe("SignalScoreCard", () => {
  it("renders score and label", () => {
    render(<SignalScoreCard label="Overall Signal" score={72.4} />);

    expect(screen.getByText("Overall Signal")).toBeInTheDocument();
    expect(screen.getByText("72.4")).toBeInTheDocument();
  });

  it("handles missing score", () => {
    render(<SignalScoreCard label="Momentum" score={null} />);

    expect(screen.getByText("N/A")).toBeInTheDocument();
  });

  it("clamps displayed score safely", () => {
    render(<SignalScoreCard label="Volatility Risk" score={120} />);

    expect(screen.getByText("100.0")).toBeInTheDocument();
  });
});
