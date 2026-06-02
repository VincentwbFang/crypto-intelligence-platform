import { Badge } from "@/components/ui/badge";

export function SignalDirectionBadge({ direction }: { direction: string }) {
  const normalized = String(direction || "").toLowerCase();
  const variant =
    normalized === "bullish"
      ? "success"
      : normalized === "bearish"
        ? "danger"
        : normalized === "mixed"
          ? "warning"
          : "secondary";
  const label =
    normalized === "bullish"
      ? "Bullish Bias"
      : normalized === "bearish"
        ? "Bearish Bias"
        : normalized === "mixed"
          ? "Mixed Bias"
          : "Neutral Bias";
  return <Badge variant={variant}>{label}</Badge>;
}
