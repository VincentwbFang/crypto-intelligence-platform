"use client";

import { useState } from "react";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { inviteWorkspaceMember } from "@/lib/api/workspaces";

export function InviteMemberForm({ workspaceId }: { workspaceId: string }) {
  const [email, setEmail] = useState("");
  const [role, setRole] = useState("member");
  const [message, setMessage] = useState<string | null>(null);

  async function onSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    try {
      await inviteWorkspaceMember(workspaceId, { email, role });
      setMessage("Member added when the email belongs to an existing user.");
      setEmail("");
    } catch (error_) {
      setMessage(error_ instanceof Error ? error_.message : "Could not add member.");
    }
  }

  return (
    <form className="grid gap-3 rounded-lg border bg-card p-5 md:grid-cols-[1fr_160px_auto]" onSubmit={onSubmit}>
      <Input onChange={(event) => setEmail(event.target.value)} placeholder="teammate@example.com" type="email" value={email} />
      <select className="h-10 rounded-md border bg-background px-3 text-sm" onChange={(event) => setRole(event.target.value)} value={role}>
        <option value="viewer">Viewer</option>
        <option value="member">Member</option>
        <option value="admin">Admin</option>
      </select>
      <Button type="submit">Add member</Button>
      {message ? <p className="text-sm text-muted-foreground md:col-span-3">{message}</p> : null}
    </form>
  );
}
