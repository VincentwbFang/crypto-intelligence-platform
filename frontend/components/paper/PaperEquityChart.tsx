import type { PaperEquitySnapshot } from "@/lib/api/types";

export function PaperEquityChart({ snapshots }: { snapshots: PaperEquitySnapshot[] }) {
  if (!snapshots.length) {
    return (
      <div className="flex h-48 items-center justify-center rounded-md border text-sm text-muted-foreground">
        No equity snapshots yet.
      </div>
    );
  }
  const values = snapshots.map((point) => point.equity);
  const min = Math.min(...values);
  const max = Math.max(...values);
  const range = max - min || 1;
  const points = snapshots
    .map((point, index) => {
      const x = snapshots.length === 1 ? 0 : (index / (snapshots.length - 1)) * 100;
      const y = 100 - ((point.equity - min) / range) * 100;
      return `${x},${y}`;
    })
    .join(" ");
  return (
    <div className="h-48 rounded-md border p-4">
      <svg aria-label="Virtual equity chart" className="h-full w-full" viewBox="0 0 100 100">
        <polyline
          fill="none"
          points={points}
          stroke="currentColor"
          strokeLinecap="round"
          strokeLinejoin="round"
          strokeWidth="2"
          vectorEffect="non-scaling-stroke"
        />
      </svg>
    </div>
  );
}
