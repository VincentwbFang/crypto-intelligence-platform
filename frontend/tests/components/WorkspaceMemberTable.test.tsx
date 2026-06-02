import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { WorkspaceMemberTable } from "@/components/workspace/WorkspaceMemberTable";

describe("WorkspaceMemberTable", () => {
  it("renders role badges and conditional action text", () => {
    render(
      <WorkspaceMemberTable
        currentRole="admin"
        members={[
          { workspace_id: "w1", user_id: "u1", role: "owner", status: "active" },
          { workspace_id: "w1", user_id: "u2", role: "viewer", status: "active" }
        ]}
      />
    );
    expect(screen.getByText("owner")).toBeInTheDocument();
    expect(screen.getByText("viewer")).toBeInTheDocument();
    expect(screen.getByText("Manage")).toBeInTheDocument();
  });
});
