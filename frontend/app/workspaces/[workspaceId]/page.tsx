import Link from "next/link";

import { PageHeader } from "@/components/layout/PageHeader";
import { Button } from "@/components/ui/button";

export default async function WorkspaceDetailPage({
  params
}: {
  params: Promise<{ workspaceId: string }>;
}) {
  const { workspaceId } = await params;
  return (
    <div>
      <PageHeader
        title="Workspace"
        description="Workspace resources are isolated by tenant."
        action={<Button asChild variant="outline"><Link href={`/workspaces/${workspaceId}/members`}>Members</Link></Button>}
      />
      <section className="rounded-lg border bg-card p-5 text-sm">
        Workspace ID: <span className="font-mono">{workspaceId}</span>
      </section>
    </div>
  );
}
