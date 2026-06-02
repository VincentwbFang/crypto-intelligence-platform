import { apiFetch } from "@/lib/api/client";
import type { AuthUser, TokenResponse, Workspace } from "@/lib/api/types";

export function registerUser(request: {
  email: string;
  password: string;
  full_name?: string | null;
}) {
  return apiFetch<TokenResponse>("/auth/register", {
    method: "POST",
    body: request
  });
}

export function loginUser(request: { email: string; password: string }) {
  return apiFetch<TokenResponse>("/auth/login", {
    method: "POST",
    body: request
  });
}

export function refreshSession(refreshToken: string) {
  return apiFetch<TokenResponse>("/auth/refresh", {
    method: "POST",
    body: { refresh_token: refreshToken }
  });
}

export function logoutUser(refreshToken: string) {
  return apiFetch<{ logged_out: boolean }>("/auth/logout", {
    method: "POST",
    body: { refresh_token: refreshToken }
  });
}

export function getAuthMe() {
  return apiFetch<{ user: AuthUser; workspace?: Workspace | null }>("/auth/me");
}

export function switchWorkspace(workspaceId: string) {
  return apiFetch<TokenResponse>("/auth/switch-workspace", {
    method: "POST",
    body: { workspace_id: workspaceId }
  });
}
