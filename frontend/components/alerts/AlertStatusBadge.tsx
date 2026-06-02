import { Badge } from "@/components/ui/badge";

const labels: Record<string, string> = {
  open: "Open",
  acknowledged: "Acknowledged",
  resolved: "Resolved",
  dismissed: "Dismissed"
};

export function AlertStatusBadge({ status }: { status: string | null | undefined }) {
  const normalized = String(status || "").toLowerCase();
  const variant =
    normalized === "resolved"
      ? "success"
      : normalized === "acknowledged"
        ? "info"
        : normalized === "dismissed"
          ? "secondary"
          : "warning";
  return <Badge variant={variant}>{labels[normalized] ?? "Unknown"}</Badge>;
}
