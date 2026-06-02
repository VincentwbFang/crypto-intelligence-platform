import { notFound } from "next/navigation";

import { AlertDetailCard } from "@/components/alerts/AlertDetailCard";
import { AlertExplanationCard } from "@/components/alerts/AlertExplanationCard";
import { AlertStatusActions } from "@/components/alerts/AlertStatusActions";
import { ErrorState } from "@/components/common/ErrorState";
import { PageHeader } from "@/components/layout/PageHeader";
import { explainAlert, getAlert } from "@/lib/api/alerts";
import type { AIExplanationResponse } from "@/lib/api/types";

type AlertDetailPageProps = {
  params: Promise<{
    alertId: string;
  }>;
};

export default async function AlertDetailPage({ params }: AlertDetailPageProps) {
  const { alertId: routeAlertId } = await params;
  const alertId = Number(routeAlertId);
  if (!Number.isInteger(alertId)) {
    notFound();
  }

  try {
    const alert = await getAlert(alertId);
    let explanation: AIExplanationResponse = {
      enabled: false,
      message: "AI alert explanation is disabled."
    };
    try {
      explanation = await explainAlert(alertId);
    } catch {
      explanation = {
        enabled: false,
        message: "AI alert explanation is unavailable."
      };
    }
    return (
      <div>
        <PageHeader
          title={`Alert ${alert.id}`}
          description="Deterministic alert details and optional research-only AI explanation."
          action={<AlertStatusActions alertId={alert.id} />}
        />
        <div className="space-y-6">
          <AlertDetailCard alert={alert} />
          <AlertExplanationCard explanation={explanation} />
        </div>
      </div>
    );
  } catch (error) {
    return (
      <div>
        <PageHeader title={`Alert ${alertId}`} />
        <ErrorState
          message={error instanceof Error ? error.message : "Alert detail failed."}
        />
      </div>
    );
  }
}
