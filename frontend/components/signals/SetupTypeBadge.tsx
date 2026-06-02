import { Badge } from "@/components/ui/badge";
import { setupTypeLabel } from "@/lib/format";

export function SetupTypeBadge({ setupType }: { setupType: string }) {
  return <Badge variant="outline">{setupTypeLabel(setupType)}</Badge>;
}
