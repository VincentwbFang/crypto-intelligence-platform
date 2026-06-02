import type { ReactNode } from "react";

import { cn } from "@/lib/utils";

type StatCardProps = {
  label: string;
  value: ReactNode;
  detail?: ReactNode;
  className?: string;
};

export function StatCard({ label, value, detail, className }: StatCardProps) {
  return (
    <div className={cn("rounded-lg border bg-card p-4 shadow-panel", className)}>
      <p className="text-xs font-medium uppercase tracking-wide text-muted-foreground">
        {label}
      </p>
      <div className="mt-2 text-2xl font-semibold">{value}</div>
      {detail ? <div className="mt-2 text-sm text-muted-foreground">{detail}</div> : null}
    </div>
  );
}
