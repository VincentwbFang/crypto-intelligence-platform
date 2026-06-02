import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";

import { RegisterForm } from "@/components/auth/RegisterForm";
import { registerUser } from "@/lib/api/auth";

vi.mock("next/navigation", () => ({ useRouter: () => ({ push: vi.fn() }) }));
vi.mock("@/lib/api/auth", () => ({
  registerUser: vi.fn().mockResolvedValue({ access_token: "access", refresh_token: "refresh" })
}));

describe("RegisterForm", () => {
  it("validates required fields", async () => {
    render(<RegisterForm />);
    await userEvent.click(screen.getByText("Create account"));
    expect(screen.getByText("Email and password are required.")).toBeInTheDocument();
  });

  it("submits registration", async () => {
    render(<RegisterForm />);
    await userEvent.type(screen.getByLabelText("Email"), "a@example.com");
    await userEvent.type(screen.getByLabelText("Password"), "Password123");
    await userEvent.click(screen.getByText("Create account"));
    expect(registerUser).toHaveBeenCalledWith({
      email: "a@example.com",
      password: "Password123",
      full_name: null
    });
  });
});
