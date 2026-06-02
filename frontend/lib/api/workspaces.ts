import { apiFetch } from "@/lib/api/client";
import type { PlanLimits, Workspace, WorkspaceMember } from "@/lib/api/types";

export function listWorkspaces() {
  return apiFetch<{ data: Workspace[] }>("/workspaces");
}

export function createWorkspace(request: { name: string }) {
  return apiFetch<Workspace>("/workspaces", {
    method: "POST",
    body: request
  });
}

export function getWorkspace(workspaceId: string) {
  return apiFetch<Workspace>(`/workspaces/${workspaceId}`);
}

export function updateWorkspace(workspaceId: string, request: { name?: string }) {
  return apiFetch<Workspace>(`/workspaces/${workspaceId}`, {
    method: "PATCH",
    body: request
  });
}

export function listWorkspaceMembers(workspaceId: string) {
  return apiFetch<{ data: WorkspaceMember[] }>(`/workspaces/${workspaceId}/members`);
}

export function inviteWorkspaceMember(workspaceId: string, request: { email: string; role: string }) {
  return apiFetch<WorkspaceMember>(`/workspaces/${workspaceId}/members`, {
    method: "POST",
    body: request
  });
}

export function updateWorkspaceMemberRole(workspaceId: string, userId: string, role: string) {
  return apiFetch<WorkspaceMember>(`/workspaces/${workspaceId}/members/${userId}`, {
    method: "PATCH",
    body: { role }
  });
}

export function removeWorkspaceMember(workspaceId: string, userId: string) {
  return apiFetch<WorkspaceMember>(`/workspaces/${workspaceId}/members/${userId}`, {
    method: "DELETE"
  });
}

export function getWorkspacePlan(workspaceId: string) {
  return apiFetch<PlanLimits>(`/workspaces/${workspaceId}/plan`);
}
