import { apiFetch } from "@/lib/api/client";
import type { AuthUser, UserPreference } from "@/lib/api/types";

export function getCurrentUser() {
  return apiFetch<AuthUser>("/users/me");
}

export function updateCurrentUser(request: { full_name?: string | null }) {
  return apiFetch<AuthUser>("/users/me", {
    method: "PATCH",
    body: request
  });
}

export function getUserPreferences() {
  return apiFetch<UserPreference>("/users/me/preferences");
}

export function updateUserPreferences(request: Partial<UserPreference>) {
  return apiFetch<UserPreference>("/users/me/preferences", {
    method: "PATCH",
    body: request
  });
}
