import { SectionCard } from "@/components/common/SectionCard";
import { EnvironmentBadge } from "@/components/system/EnvironmentBadge";

type SystemStatusCardProps = {
  title: string;
  status?: string | null;
  detail?: string | null;
  environment?: string | null;
};

export function SystemStatusCard({
  title,
  status,
  detail,
  environment
}: SystemStatusCardProps) {
  const normalized = status || "unknown";
  const statusClass =
    normalized === "ok" || normalized === "ready" || normalized === "alive"
      ? "text-emerald-700"
      : normalized === "not_ready" || normalized === "failed"
        ? "text-destructive"
        : "text-muted-foreground";

  return (
    <SectionCard title={title}>
      <div className="flex items-start justify-between gap-4">
        <div>
          <p className={`text-2xl font-semibold ${statusClass}`}>{normalized}</p>
          {detail ? <p className="mt-2 text-sm text-muted-foreground">{detail}</p> : null}
        </div>
        {environment ? <EnvironmentBadge environment={environment} /> : null}
      </div>
    </SectionCard>
  );
}
