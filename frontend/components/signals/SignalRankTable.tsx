import Link from "next/link";

import { EmptyState } from "@/components/common/EmptyState";
import { Progress } from "@/components/ui/progress";
import { RiskLevelBadge } from "@/components/signals/RiskLevelBadge";
import { SetupTypeBadge } from "@/components/signals/SetupTypeBadge";
import { SignalDirectionBadge } from "@/components/signals/SignalDirectionBadge";
import type { SignalResponse } from "@/lib/api/types";
import { formatDateTime, formatScore, formatSymbolForRoute } from "@/lib/format";

export function SignalRankTable({ signals }: { signals: SignalResponse[] }) {
  if (!signals.length) {
    return <EmptyState message="No ranked signals are available yet." />;
  }
  return (
    <div className="overflow-x-auto rounded-lg border bg-card">
      <table className="w-full min-w-[980px] text-left text-sm">
        <thead className="bg-muted">
          <tr>
            <th className="px-4 py-3 font-medium">Symbol</th>
            <th className="px-4 py-3 font-medium">Direction</th>
            <th className="px-4 py-3 font-medium">Setup Type</th>
            <th className="px-4 py-3 font-medium">Overall</th>
            <th className="px-4 py-3 font-medium">Trend</th>
            <th className="px-4 py-3 font-medium">Momentum</th>
            <th className="px-4 py-3 font-medium">Volume</th>
            <th className="px-4 py-3 font-medium">Relative Strength</th>
            <th className="px-4 py-3 font-medium">Volatility Risk</th>
            <th className="px-4 py-3 font-medium">Risk Level</th>
            <th className="px-4 py-3 font-medium">Timestamp</th>
          </tr>
        </thead>
        <tbody>
          {signals.map((signal) => (
            <tr className="border-t hover:bg-muted/40" key={signal.symbol}>
              <td className="px-4 py-3 font-medium">
                <Link href={`/signals/${formatSymbolForRoute(signal.symbol)}`}>
                  {signal.symbol}
                </Link>
              </td>
              <td className="px-4 py-3">
                <SignalDirectionBadge direction={signal.signal_direction} />
              </td>
              <td className="px-4 py-3">
                <SetupTypeBadge setupType={signal.setup_type} />
              </td>
              <ScoreCell value={signal.scores.overall_signal_score} />
              <ScoreCell value={signal.scores.trend_score} />
              <ScoreCell value={signal.scores.momentum_score} />
              <ScoreCell value={signal.scores.volume_score} />
              <ScoreCell value={signal.scores.relative_strength_score} />
              <ScoreCell value={signal.scores.volatility_risk_score} />
              <td className="px-4 py-3">
                <RiskLevelBadge level={signal.risk_level} />
              </td>
              <td className="px-4 py-3 text-muted-foreground">
                {formatDateTime(signal.timestamp)}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

function ScoreCell({ value }: { value: number }) {
  return (
    <td className="px-4 py-3">
      <div className="min-w-28">
        <div className="mb-1 font-medium">{formatScore(value)}</div>
        <Progress value={value} label="Score" />
      </div>
    </td>
  );
}
