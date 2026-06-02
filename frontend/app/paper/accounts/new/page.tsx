import { SectionCard } from "@/components/common/SectionCard";
import { PageHeader } from "@/components/layout/PageHeader";
import { PaperAccountForm } from "@/components/paper/PaperAccountForm";

export default function NewPaperAccountPage() {
  return (
    <div>
      <PageHeader
        title="Create Virtual Account"
        description="Start a paper trading account with virtual capital only."
      />
      <SectionCard
        title="Account Setup"
        description="No wallet, private exchange key, or real trading connection is used."
      >
        <PaperAccountForm />
      </SectionCard>
    </div>
  );
}
