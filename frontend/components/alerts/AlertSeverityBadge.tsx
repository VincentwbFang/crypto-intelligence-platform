import { Badge } from "@/components/ui/badge";
import { severityLabel } from "@/lib/format";

export function AlertSeverityBadge({
  severity
}: {
  severity: string | null | undefined;
}) {
  const normalized = String(severity || "").toLowerCase();
  const variant =
    normalized === "info" || normalized === "low"
      ? "info"
      : normalized === "medium"
        ? "warning"
        : normalized === "high" || normalized === "critical"
          ? "danger"
          : "secondary";
  return (
    <Badge aria-label={`Alert severity ${severityLabel(severity)}`} variant={variant}>
      {severityLabel(severity)}
    </Badge>
  );
}
