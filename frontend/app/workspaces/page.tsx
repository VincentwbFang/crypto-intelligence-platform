"use client";

import Link from "next/link";
import { useEffect, useState } from "react";

import { EmptyState } from "@/components/common/EmptyState";
import { PageHeader } from "@/components/layout/PageHeader";
import { Button } from "@/components/ui/button";
import { WorkspaceCard } from "@/components/workspace/WorkspaceCard";
import { listWorkspaces } from "@/lib/api/workspaces";
import type { Workspace } from "@/lib/api/types";

export default function WorkspacesPage() {
  const [workspaces, setWorkspaces] = useState<Workspace[]>([]);
  useEffect(() => {
    listWorkspaces().then((response) => setWorkspaces(response.data)).catch(() => setWorkspaces([]));
  }, []);
  return (
    <div>
      <PageHeader
        title="Workspaces"
        description="Manage SaaS-ready research workspaces and roles."
        action={<Button asChild><Link href="/workspaces/new">New workspace</Link></Button>}
      />
      {workspaces.length ? (
        <div className="grid gap-4 md:grid-cols-2">{workspaces.map((workspace) => <WorkspaceCard key={workspace.workspace_id} workspace={workspace} />)}</div>
      ) : (
        <EmptyState message="No workspaces loaded yet." />
      )}
    </div>
  );
}
