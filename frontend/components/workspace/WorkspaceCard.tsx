import Link from "next/link";

import { PlanBadge } from "@/components/workspace/PlanBadge";
import type { Workspace } from "@/lib/api/types";

export function WorkspaceCard({ workspace }: { workspace: Workspace }) {
  return (
    <article className="rounded-lg border bg-card p-5">
      <div className="flex items-center justify-between gap-3">
        <div>
          <h2 className="font-semibold">{workspace.name}</h2>
          <p className="text-sm text-muted-foreground">{workspace.role ?? "member"}</p>
        </div>
        <PlanBadge plan={workspace.plan} />
      </div>
      <Link className="mt-4 inline-flex text-sm text-primary" href={`/workspaces/${workspace.workspace_id}/members`}>
        Manage members
      </Link>
    </article>
  );
}
