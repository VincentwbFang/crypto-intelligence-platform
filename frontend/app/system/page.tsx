"use client";

import { useEffect, useState } from "react";

import { ErrorState } from "@/components/common/ErrorState";
import { SectionCard } from "@/components/common/SectionCard";
import { PageHeader } from "@/components/layout/PageHeader";
import { SystemStatusCard } from "@/components/system/SystemStatusCard";
import { getSystemHealth, getSystemReady, getSystemVersion } from "@/lib/api/system";
import type { SystemHealth, SystemReady, SystemVersion } from "@/lib/api/types";

export default function SystemPage() {
  const [health, setHealth] = useState<SystemHealth | null>(null);
  const [ready, setReady] = useState<SystemReady | null>(null);
  const [version, setVersion] = useState<SystemVersion | null>(null);
  const [error, setError] = useState(false);

  useEffect(() => {
    Promise.all([getSystemHealth(), getSystemReady(), getSystemVersion()])
      .then(([healthResult, readyResult, versionResult]) => {
        setHealth(healthResult);
        setReady(readyResult);
        setVersion(versionResult);
      })
      .catch(() => setError(true));
  }, []);

  const apiBaseUrl = process.env.NEXT_PUBLIC_API_BASE_URL || "/api/backend";

  return (
    <div className="space-y-6">
      <PageHeader
        title="System"
        description="Operational status, version, and environment metadata."
      />
      {error ? <ErrorState message="System status could not be loaded." /> : null}
      <div className="grid gap-4 md:grid-cols-3">
        <SystemStatusCard
          detail={health?.service}
          environment={health?.environment}
          status={health?.status}
          title="API Health"
        />
        <SystemStatusCard
          detail={ready ? Object.entries(ready.checks).map(([k, v]) => `${k}: ${v}`).join(", ") : null}
          status={ready?.status}
          title="Readiness"
        />
        <SystemStatusCard
          detail={version?.service}
          environment={version?.environment}
          status={version?.version}
          title="Version"
        />
      </div>
      <SectionCard title="Frontend Runtime">
        <dl className="grid gap-3 text-sm md:grid-cols-2">
          <div>
            <dt className="text-muted-foreground">Frontend version</dt>
            <dd className="font-medium">{process.env.NEXT_PUBLIC_APP_VERSION || "not set"}</dd>
          </div>
          <div>
            <dt className="text-muted-foreground">Frontend environment</dt>
            <dd className="font-medium">{process.env.NEXT_PUBLIC_DEPLOYMENT_ENV || "local"}</dd>
          </div>
          <div>
            <dt className="text-muted-foreground">API base URL</dt>
            <dd className="font-medium">{apiBaseUrl}</dd>
          </div>
          <div>
            <dt className="text-muted-foreground">Metrics</dt>
            <dd className="font-medium">Available at /metrics when enabled</dd>
          </div>
        </dl>
      </SectionCard>
    </div>
  );
}

