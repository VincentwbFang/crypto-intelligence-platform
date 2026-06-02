import { SectionCard } from "@/components/common/SectionCard";
import { PageHeader } from "@/components/layout/PageHeader";
import { PaperOrdersExplorer } from "@/components/paper/PaperOrdersExplorer";

export default function PaperOrdersPage() {
  return (
    <div>
      <PageHeader
        title="Simulated Orders"
        description="Inspect virtual market orders created by paper trading workflows."
      />
      <SectionCard
        title="Order Explorer"
        description="Filter by virtual account and status."
      >
        <PaperOrdersExplorer />
      </SectionCard>
    </div>
  );
}
