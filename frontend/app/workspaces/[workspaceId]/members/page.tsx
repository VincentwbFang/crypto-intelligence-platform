import { PageHeader } from "@/components/layout/PageHeader";
import { WorkspaceMembersPanel } from "@/components/workspace/WorkspaceMembersPanel";

export default async function WorkspaceMembersPage({
  params
}: {
  params: Promise<{ workspaceId: string }>;
}) {
  const { workspaceId } = await params;
  return (
    <div className="space-y-6">
      <PageHeader title="Workspace Members" description="Owners and admins can manage workspace access." />
      <WorkspaceMembersPanel workspaceId={workspaceId} />
    </div>
  );
}
