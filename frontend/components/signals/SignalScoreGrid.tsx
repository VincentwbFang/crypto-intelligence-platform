import type { SignalScores } from "@/lib/api/types";

import { SignalScoreCard } from "@/components/signals/SignalScoreCard";

export function SignalScoreGrid({ scores }: { scores: SignalScores }) {
  return (
    <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
      <SignalScoreCard label="Overall Signal" score={scores.overall_signal_score} />
      <SignalScoreCard label="Trend" score={scores.trend_score} />
      <SignalScoreCard label="Momentum" score={scores.momentum_score} />
      <SignalScoreCard label="Volume" score={scores.volume_score} />
      <SignalScoreCard
        label="Relative Strength"
        score={scores.relative_strength_score}
      />
      <SignalScoreCard
        label="Volatility Risk"
        score={scores.volatility_risk_score}
      />
    </div>
  );
}
