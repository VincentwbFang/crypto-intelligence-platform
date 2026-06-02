import { Badge } from "@/components/ui/badge";
import { riskLevelLabel } from "@/lib/format";

type RiskLevelBadgeProps = {
  level: string | null | undefined;
};

export function RiskLevelBadge({ level }: RiskLevelBadgeProps) {
  const normalized = String(level || "").toLowerCase();
  const variant =
    normalized === "low"
      ? "success"
      : normalized === "medium"
        ? "warning"
        : normalized === "high" || normalized === "extreme"
          ? "danger"
          : "secondary";
  return (
    <Badge aria-label={`Risk level ${riskLevelLabel(level)}`} variant={variant}>
      {riskLevelLabel(level)}
    </Badge>
  );
}
