import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";

import { LoginForm } from "@/components/auth/LoginForm";
import { loginUser } from "@/lib/api/auth";

vi.mock("next/navigation", () => ({ useRouter: () => ({ push: vi.fn() }) }));
vi.mock("@/lib/api/auth", () => ({
  loginUser: vi.fn().mockResolvedValue({ access_token: "access", refresh_token: "refresh" })
}));

describe("LoginForm", () => {
  it("renders and submits credentials", async () => {
    render(<LoginForm />);
    await userEvent.type(screen.getByLabelText("Email"), "a@example.com");
    await userEvent.type(screen.getByLabelText("Password"), "Password123");
    await userEvent.click(screen.getByText("Sign in"));
    expect(loginUser).toHaveBeenCalledWith({ email: "a@example.com", password: "Password123" });
  });
});
