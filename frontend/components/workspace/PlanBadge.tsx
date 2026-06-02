import { Badge } from "@/components/ui/badge";

export function PlanBadge({ plan }: { plan?: string | null }) {
  const label = plan || "free";
  return <Badge variant="outline">{label}</Badge>;
}
