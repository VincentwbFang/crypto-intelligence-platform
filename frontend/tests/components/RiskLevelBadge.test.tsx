import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { RiskLevelBadge } from "@/components/signals/RiskLevelBadge";

describe("RiskLevelBadge", () => {
  it.each([
    ["low", "Low Risk"],
    ["medium", "Medium Risk"],
    ["high", "High Risk"],
    ["extreme", "Extreme Risk"]
  ])("renders %s risk level", (level, label) => {
    render(<RiskLevelBadge level={level} />);

    expect(screen.getByText(label)).toBeInTheDocument();
  });

  it("handles unknown risk level safely", () => {
    render(<RiskLevelBadge level="unknown" />);

    expect(screen.getByText("Unknown Risk")).toBeInTheDocument();
  });
});
