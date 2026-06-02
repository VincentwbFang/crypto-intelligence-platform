import { AlertCenter } from "@/components/alerts/AlertCenter";
import { PageHeader } from "@/components/layout/PageHeader";

export default function AlertsPage() {
  return (
    <div>
      <PageHeader
        title="Alert Center"
        description="Review deterministic market intelligence alerts, update status, and run manual evaluations."
      />
      <AlertCenter />
    </div>
  );
}
