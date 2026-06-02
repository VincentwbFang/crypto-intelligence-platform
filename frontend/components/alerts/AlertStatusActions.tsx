"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";

import { Button } from "@/components/ui/button";
import { resolveAlert, updateAlertStatus } from "@/lib/api/alerts";

export function AlertStatusActions({ alertId }: { alertId: number }) {
  const router = useRouter();
  const [isLoading, setIsLoading] = useState(false);
  const [message, setMessage] = useState<string | null>(null);

  async function run(action: "acknowledged" | "dismissed" | "resolved") {
    setIsLoading(true);
    setMessage(null);
    try {
      if (action === "resolved") {
        await resolveAlert(alertId);
      } else {
        await updateAlertStatus(alertId, action);
      }
      router.refresh();
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "Status update failed.");
    } finally {
      setIsLoading(false);
    }
  }

  return (
    <div className="flex flex-wrap items-center gap-2">
      <Button
        disabled={isLoading}
        onClick={() => void run("acknowledged")}
        variant="secondary"
      >
        Acknowledge
      </Button>
      <Button disabled={isLoading} onClick={() => void run("resolved")} variant="secondary">
        Resolve
      </Button>
      <Button disabled={isLoading} onClick={() => void run("dismissed")} variant="ghost">
        Dismiss
      </Button>
      {message ? <p className="text-sm text-red-700">{message}</p> : null}
    </div>
  );
}
