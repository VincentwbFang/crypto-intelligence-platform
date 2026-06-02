import { afterEach, describe, expect, it, vi } from "vitest";

import { loginUser, registerUser, switchWorkspace } from "@/lib/api/auth";

describe("auth api", () => {
  afterEach(() => {
    vi.restoreAllMocks();
  });

  it("calls login and register endpoints", async () => {
    const response = {
      access_token: "access",
      refresh_token: "refresh",
      token_type: "bearer",
      expires_in: 1800,
      user: { user_id: "u1", email: "a@example.com", is_active: true, is_verified: false, is_superuser: false },
      workspace: null
    };
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue({
      ok: true,
      status: 200,
      headers: new Headers({ "Content-Type": "application/json" }),
      text: () => Promise.resolve(JSON.stringify(response))
    }));
    await expect(loginUser({ email: "a@example.com", password: "Password123" })).resolves.toMatchObject({ access_token: "access" });
    await expect(registerUser({ email: "a@example.com", password: "Password123" })).resolves.toMatchObject({ refresh_token: "refresh" });
  });

  it("switches workspace", async () => {
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue({
      ok: true,
      status: 200,
      headers: new Headers({ "Content-Type": "application/json" }),
      text: () => Promise.resolve(JSON.stringify({
        access_token: "new",
        refresh_token: "refresh",
        token_type: "bearer",
        expires_in: 1800,
        user: { user_id: "u1", email: "a@example.com", is_active: true, is_verified: false, is_superuser: false },
        workspace: { workspace_id: "w1", name: "W", slug: "w", owner_user_id: "u1", plan: "free", status: "active" }
      }))
    }));
    await expect(switchWorkspace("w1")).resolves.toMatchObject({ access_token: "new" });
  });
});
