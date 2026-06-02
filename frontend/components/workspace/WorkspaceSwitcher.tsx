"use client";

import { useEffect, useState } from "react";

import { PlanBadge } from "@/components/workspace/PlanBadge";
import { listWorkspaces } from "@/lib/api/workspaces";
import { switchWorkspace } from "@/lib/api/auth";
import { saveSession } from "@/lib/auth/session";
import type { Workspace } from "@/lib/api/types";

export function WorkspaceSwitcher() {
  const [workspaces, setWorkspaces] = useState<Workspace[]>([]);
  const [currentId, setCurrentId] = useState("");

  useEffect(() => {
    listWorkspaces()
      .then((response) => {
        setWorkspaces(response.data);
        setCurrentId(response.data[0]?.workspace_id ?? "");
      })
      .catch(() => setWorkspaces([]));
  }, []);

  async function onChange(workspaceId: string) {
    setCurrentId(workspaceId);
    const response = await switchWorkspace(workspaceId);
    saveSession(response.access_token, response.refresh_token);
    window.location.reload();
  }

  const current = workspaces.find((workspace) => workspace.workspace_id === currentId);

  if (!workspaces.length) {
    return <span className="text-xs text-muted-foreground">No workspace</span>;
  }

  return (
    <div className="flex items-center gap-2">
      <select
        aria-label="Workspace"
        className="h-9 rounded-md border bg-background px-2 text-sm"
        onChange={(event) => onChange(event.target.value)}
        value={currentId}
      >
        {workspaces.map((workspace) => (
          <option key={workspace.workspace_id} value={workspace.workspace_id}>
            {workspace.name}
          </option>
        ))}
      </select>
      <PlanBadge plan={current?.plan} />
    </div>
  );
}
