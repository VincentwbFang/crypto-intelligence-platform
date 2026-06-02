import { PageHeader } from "@/components/layout/PageHeader";
import { WatchlistEditor } from "@/components/watchlists/WatchlistEditor";

export default function WatchlistsPage() {
  return (
    <div>
      <PageHeader
        title="Watchlists"
        description="Workspace-scoped symbol lists with plan-aware symbol limits."
      />
      <WatchlistEditor />
    </div>
  );
}
