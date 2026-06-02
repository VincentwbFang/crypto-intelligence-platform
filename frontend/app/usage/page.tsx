"use client";

import { useEffect, useState } from "react";

import { ErrorState } from "@/components/common/ErrorState";
import { PageHeader } from "@/components/layout/PageHeader";
import { PlanLimitsTable } from "@/components/usage/PlanLimitsTable";
import { UsageSummaryCards } from "@/components/usage/UsageSummaryCards";
import { getUsageLimits, getUsageSummary } from "@/lib/api/usage";
import type { PlanLimits, UsageSummary } from "@/lib/api/types";

export default function UsagePage() {
  const [summary, setSummary] = useState<UsageSummary | null>(null);
  const [limits, setLimits] = useState<PlanLimits | null>(null);
  const [error, setError] = useState(false);

  useEffect(() => {
    Promise.all([getUsageSummary(), getUsageLimits()])
      .then(([summaryResponse, limitsResponse]) => {
        setSummary(summaryResponse);
        setLimits(limitsResponse);
      })
      .catch(() => setError(true));
  }, []);

  return (
    <div className="space-y-6">
      <PageHeader title="Usage" description="Monthly usage counters for subscription-ready feature gates." />
      {error ? <ErrorState message="Usage data could not be loaded." /> : null}
      {summary ? <UsageSummaryCards summary={summary} /> : null}
      {limits ? <PlanLimitsTable limits={limits} /> : null}
    </div>
  );
}
