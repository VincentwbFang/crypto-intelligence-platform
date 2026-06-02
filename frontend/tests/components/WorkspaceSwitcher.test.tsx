import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";

import { WorkspaceSwitcher } from "@/components/workspace/WorkspaceSwitcher";
import { switchWorkspace } from "@/lib/api/auth";

vi.mock("@/lib/api/workspaces", () => ({
  listWorkspaces: vi.fn().mockResolvedValue({
    data: [
      { workspace_id: "w1", name: "Main", slug: "main", owner_user_id: "u1", plan: "free", status: "active" },
      { workspace_id: "w2", name: "Research", slug: "research", owner_user_id: "u1", plan: "pro", status: "active" }
    ]
  })
}));

vi.mock("@/lib/api/auth", () => ({
  switchWorkspace: vi.fn().mockResolvedValue({ access_token: "access", refresh_token: "refresh" })
}));

describe("WorkspaceSwitcher", () => {
  it("renders current workspace and switches", async () => {
    Object.defineProperty(window, "location", {
      value: { reload: vi.fn() },
      writable: true
    });
    render(<WorkspaceSwitcher />);
    expect(await screen.findByDisplayValue("Main")).toBeInTheDocument();
    await userEvent.selectOptions(screen.getByLabelText("Workspace"), "w2");
    expect(switchWorkspace).toHaveBeenCalledWith("w2");
  });
});
