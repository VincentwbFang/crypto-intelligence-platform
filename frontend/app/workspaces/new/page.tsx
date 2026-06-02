import { PageHeader } from "@/components/layout/PageHeader";
import { WorkspaceForm } from "@/components/workspace/WorkspaceForm";

export default function NewWorkspacePage() {
  return (
    <div className="max-w-xl">
      <PageHeader title="New Workspace" description="Create a separate tenant boundary for research resources." />
      <section className="rounded-lg border bg-card p-5">
        <WorkspaceForm />
      </section>
    </div>
  );
}
