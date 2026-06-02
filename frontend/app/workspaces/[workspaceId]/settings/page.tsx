import { PageHeader } from "@/components/layout/PageHeader";

export default async function WorkspaceSettingsPage({
  params
}: {
  params: Promise<{ workspaceId: string }>;
}) {
  const { workspaceId } = await params;
  return (
    <div>
      <PageHeader title="Workspace Settings" description="Billing integration is intentionally not enabled in Phase 8." />
      <section className="rounded-lg border bg-card p-5 text-sm text-muted-foreground">
        Workspace <span className="font-mono">{workspaceId}</span> can be renamed through the API.
        Upgrade checkout is coming later.
      </section>
    </div>
  );
}
