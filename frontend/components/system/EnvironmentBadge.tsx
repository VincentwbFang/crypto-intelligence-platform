import { cn } from "@/lib/utils";

export function EnvironmentBadge({ environment }: { environment?: string | null }) {
  const value = environment || "unknown";
  const isProduction = value === "production";
  return (
    <span
      className={cn(
        "inline-flex rounded-full border px-2 py-1 text-xs font-medium",
        isProduction
          ? "border-emerald-500/40 bg-emerald-500/10 text-emerald-700"
          : "border-amber-500/40 bg-amber-500/10 text-amber-700"
      )}
    >
      {value}
    </span>
  );
}

