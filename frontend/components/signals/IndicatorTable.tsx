import type { SignalIndicators } from "@/lib/api/types";

import { formatScore } from "@/lib/format";

const indicatorLabels: Array<[keyof SignalIndicators, string]> = [
  ["ema_20", "EMA 20"],
  ["ema_50", "EMA 50"],
  ["ema_200", "EMA 200"],
  ["rsi_14", "RSI 14"],
  ["macd", "MACD"],
  ["macd_signal", "MACD Signal"],
  ["macd_histogram", "MACD Histogram"],
  ["atr_14", "ATR 14"],
  ["volume_zscore_20", "Volume Z-Score"],
  ["realized_volatility_20", "Realized Volatility"]
];

export function IndicatorTable({ indicators }: { indicators: SignalIndicators }) {
  return (
    <div className="overflow-hidden rounded-lg border bg-card">
      <table className="w-full text-left text-sm">
        <thead className="bg-muted">
          <tr>
            <th className="px-4 py-3 font-medium">Indicator</th>
            <th className="px-4 py-3 font-medium">Value</th>
          </tr>
        </thead>
        <tbody>
          {indicatorLabels.map(([key, label]) => (
            <tr className="border-t" key={key}>
              <td className="px-4 py-3 text-muted-foreground">{label}</td>
              <td className="px-4 py-3 font-medium">
                {indicators[key] === null ? "N/A" : formatScore(indicators[key])}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
