import { describe, expect, it } from "vitest";

import { clearStoredTokens, getStoredTokens, setStoredTokens } from "@/lib/auth/token-storage";

describe("token storage", () => {
  it("stores and clears tokens", () => {
    clearStoredTokens();
    expect(getStoredTokens()).toBeNull();
    setStoredTokens({ accessToken: "access", refreshToken: "refresh" });
    expect(getStoredTokens()).toEqual({ accessToken: "access", refreshToken: "refresh" });
    clearStoredTokens();
    expect(getStoredTokens()).toBeNull();
  });
});
