import { PageHeader } from "@/components/layout/PageHeader";
import { PaperAccountDashboard } from "@/components/paper/PaperAccountDashboard";

type PaperAccountDetailPageProps = {
  params: Promise<{ accountId: string }>;
};

export default async function PaperAccountDetailPage({
  params
}: PaperAccountDetailPageProps) {
  const { accountId } = await params;
  return (
    <div>
      <PageHeader
        title="Paper Portfolio"
        description="Monitor simulated positions, virtual balances, and research-only activity."
      />
      <PaperAccountDashboard accountId={accountId} />
    </div>
  );
}
