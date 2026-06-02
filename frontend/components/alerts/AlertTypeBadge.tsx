import { Badge } from "@/components/ui/badge";

export function AlertTypeBadge({ type }: { type: string | null | undefined }) {
  const label = String(type || "unknown")
    .replaceAll("_", " ")
    .replace(/\b\w/g, (match) => match.toUpperCase());
  return <Badge variant="outline">{label}</Badge>;
}
