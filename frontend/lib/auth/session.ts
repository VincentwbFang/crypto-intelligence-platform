"use client";

import { clearStoredTokens, getStoredTokens, setStoredTokens } from "@/lib/auth/token-storage";

export function hasSession() {
  return getStoredTokens() !== null;
}

export function saveSession(accessToken: string, refreshToken: string) {
  setStoredTokens({ accessToken, refreshToken });
}

export function clearSession() {
  clearStoredTokens();
}
