"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { createWorkspace } from "@/lib/api/workspaces";

export function WorkspaceForm() {
  const router = useRouter();
  const [name, setName] = useState("");
  const [error, setError] = useState<string | null>(null);

  async function onSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!name.trim()) {
      setError("Workspace name is required.");
      return;
    }
    try {
      const workspace = await createWorkspace({ name });
      router.push(`/workspaces/${workspace.workspace_id}/members`);
    } catch (error_) {
      setError(error_ instanceof Error ? error_.message : "Could not create workspace.");
    }
  }

  return (
    <form className="space-y-4" onSubmit={onSubmit}>
      <label className="block text-sm font-medium">
        Workspace Name
        <Input className="mt-1" onChange={(event) => setName(event.target.value)} value={name} />
      </label>
      {error ? <p className="text-sm text-destructive">{error}</p> : null}
      <Button type="submit">Create workspace</Button>
    </form>
  );
}
