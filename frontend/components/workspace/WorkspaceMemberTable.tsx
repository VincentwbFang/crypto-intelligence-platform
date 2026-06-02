"use client";

import type { WorkspaceMember } from "@/lib/api/types";

export function WorkspaceMemberTable({
  members,
  currentRole = "viewer"
}: {
  members: WorkspaceMember[];
  currentRole?: string;
}) {
  const canManage = currentRole === "owner" || currentRole === "admin";
  if (!members.length) {
    return <div className="rounded-lg border bg-card p-6 text-sm text-muted-foreground">No members found.</div>;
  }
  return (
    <div className="overflow-hidden rounded-lg border">
      <table className="w-full text-sm">
        <thead className="bg-muted text-left">
          <tr>
            <th className="p-3">User</th>
            <th className="p-3">Role</th>
            <th className="p-3">Status</th>
            <th className="p-3">Actions</th>
          </tr>
        </thead>
        <tbody>
          {members.map((member) => (
            <tr className="border-t" key={`${member.workspace_id}-${member.user_id}`}>
              <td className="p-3 font-mono text-xs">{member.user_id}</td>
              <td className="p-3">{member.role}</td>
              <td className="p-3">{member.status}</td>
              <td className="p-3 text-muted-foreground">
                {canManage && member.role !== "owner" ? "Manage" : "Read only"}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
