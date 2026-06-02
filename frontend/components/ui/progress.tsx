import { cn } from "@/lib/utils";

type ProgressProps = {
  value: number | null | undefined;
  className?: string;
  indicatorClassName?: string;
  label?: string;
};

export function Progress({
  value,
  className,
  indicatorClassName,
  label
}: ProgressProps) {
  const safeValue = Math.min(Math.max(Number(value ?? 0), 0), 100);
  return (
    <div
      aria-label={label}
      aria-valuemin={0}
      aria-valuemax={100}
      aria-valuenow={safeValue}
      role="progressbar"
      className={cn("h-2 w-full overflow-hidden rounded-sm bg-muted", className)}
    >
      <div
        className={cn("h-full bg-primary transition-all", indicatorClassName)}
        style={{ width: `${safeValue}%` }}
      />
    </div>
  );
}
