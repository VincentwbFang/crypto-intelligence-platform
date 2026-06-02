"use client";

import { useEffect, useState } from "react";

import { InviteMemberForm } from "@/components/workspace/InviteMemberForm";
import { WorkspaceMemberTable } from "@/components/workspace/WorkspaceMemberTable";
import { listWorkspaceMembers } from "@/lib/api/workspaces";
import type { WorkspaceMember } from "@/lib/api/types";

export function WorkspaceMembersPanel({ workspaceId }: { workspaceId: string }) {
  const [members, setMembers] = useState<WorkspaceMember[]>([]);
  useEffect(() => {
    listWorkspaceMembers(workspaceId)
      .then((response) => setMembers(response.data))
      .catch(() => setMembers([]));
  }, [workspaceId]);
  return (
    <div className="space-y-6">
      <InviteMemberForm workspaceId={workspaceId} />
      <WorkspaceMemberTable currentRole="owner" members={members} />
    </div>
  );
}
