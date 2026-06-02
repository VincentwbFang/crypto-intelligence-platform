"use client";

import { useEffect, useState } from "react";

import { AlertEvaluationForm } from "@/components/alerts/AlertEvaluationForm";
import { AlertTable } from "@/components/alerts/AlertTable";
import { ErrorState } from "@/components/common/ErrorState";
import { LoadingState } from "@/components/common/LoadingState";
import { SectionCard } from "@/components/common/SectionCard";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Select } from "@/components/ui/select";
import {
  listAlerts,
  resolveAlert,
  updateAlertStatus
} from "@/lib/api/alerts";
import type { AlertResponse } from "@/lib/api/types";

export function AlertCenter() {
  const [alerts, setAlerts] = useState<AlertResponse[]>([]);
  const [symbol, setSymbol] = useState("");
  const [severity, setSeverity] = useState("");
  const [status, setStatus] = useState("");
  const [alertType, setAlertType] = useState("");
  const [timeframe, setTimeframe] = useState("");
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  async function loadAlerts() {
    setIsLoading(true);
    setError(null);
    try {
      const result = await listAlerts({
        symbol,
        severity,
        status,
        alert_type: alertType,
        timeframe,
        limit: 100
      });
      setAlerts(result.data);
    } catch (loadError) {
      setAlerts([]);
      setError(loadError instanceof Error ? loadError.message : "Alert data failed.");
    } finally {
      setIsLoading(false);
    }
  }

  async function patchStatus(alertId: number, nextStatus: string) {
    try {
      await updateAlertStatus(alertId, nextStatus);
      await loadAlerts();
    } catch (updateError) {
      setError(updateError instanceof Error ? updateError.message : "Status update failed.");
    }
  }

  async function markResolved(alertId: number) {
    try {
      await resolveAlert(alertId);
      await loadAlerts();
    } catch (resolveError) {
      setError(resolveError instanceof Error ? resolveError.message : "Resolve failed.");
    }
  }

  useEffect(() => {
    void loadAlerts();
  }, []);

  return (
    <div className="space-y-6">
      <SectionCard title="Manual Alert Evaluation">
        <AlertEvaluationForm onEvaluated={() => void loadAlerts()} />
      </SectionCard>
      <SectionCard title="Filters">
        <form
          className="grid gap-3 md:grid-cols-6"
          onSubmit={(event) => {
            event.preventDefault();
            void loadAlerts();
          }}
        >
          <Input
            aria-label="Symbol filter"
            onChange={(event) => setSymbol(event.target.value)}
            placeholder="Symbol"
            value={symbol}
          />
          <Input
            aria-label="Timeframe filter"
            onChange={(event) => setTimeframe(event.target.value)}
            placeholder="Timeframe"
            value={timeframe}
          />
          <Select
            aria-label="Severity filter"
            onChange={(event) => setSeverity(event.target.value)}
            value={severity}
          >
            <option value="">All severities</option>
            <option value="info">Info</option>
            <option value="low">Low</option>
            <option value="medium">Medium</option>
            <option value="high">High</option>
            <option value="critical">Critical</option>
          </Select>
          <Select
            aria-label="Status filter"
            onChange={(event) => setStatus(event.target.value)}
            value={status}
          >
            <option value="">All statuses</option>
            <option value="open">Open</option>
            <option value="acknowledged">Acknowledged</option>
            <option value="resolved">Resolved</option>
            <option value="dismissed">Dismissed</option>
          </Select>
          <Input
            aria-label="Alert type filter"
            onChange={(event) => setAlertType(event.target.value)}
            placeholder="Alert type"
            value={alertType}
          />
          <Button type="submit">Apply Filters</Button>
        </form>
      </SectionCard>
      {error ? <ErrorState message={error} /> : null}
      {isLoading ? <LoadingState label="Loading alerts" /> : null}
      {!isLoading ? (
        <AlertTable
          alerts={alerts}
          onAcknowledge={(alertId) => void patchStatus(alertId, "acknowledged")}
          onDismiss={(alertId) => void patchStatus(alertId, "dismissed")}
          onResolve={(alertId) => void markResolved(alertId)}
        />
      ) : null}
    </div>
  );
}
