import { Progress } from "@/components/ui/progress";
import { formatScore } from "@/lib/format";

type SignalScoreCardProps = {
  label: string;
  score?: number | null;
  explanation?: string;
};

export function SignalScoreCard({ label, score, explanation }: SignalScoreCardProps) {
  const numericScore =
    typeof score === "number" && Number.isFinite(score)
      ? Math.min(Math.max(score, 0), 100)
      : null;
  return (
    <div className="rounded-lg border bg-card p-4 shadow-panel">
      <div className="flex items-start justify-between gap-3">
        <div>
          <p className="text-sm font-medium text-muted-foreground">{label}</p>
          <p className="mt-1 text-2xl font-semibold">{formatScore(numericScore)}</p>
        </div>
      </div>
      <Progress
        className="mt-4"
        label={`${label} score`}
        value={numericScore ?? 0}
      />
      {explanation ? (
        <p className="mt-3 text-sm text-muted-foreground">{explanation}</p>
      ) : null}
    </div>
  );
}
