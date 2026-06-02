import { EmptyState } from "@/components/common/EmptyState";
import type { PaperPosition } from "@/lib/api/types";
import { formatPercent, formatPrice } from "@/lib/format";

export function PaperPositionTable({ positions }: { positions: PaperPosition[] }) {
  if (!positions.length) {
    return <EmptyState message="No open simulated positions." />;
  }
  return (
    <div className="overflow-x-auto">
      <table className="w-full min-w-[760px] text-left text-sm">
        <thead className="border-b text-xs uppercase text-muted-foreground">
          <tr>
            <th className="py-3 pr-4">Symbol</th>
            <th className="py-3 pr-4">Quantity</th>
            <th className="py-3 pr-4">Entry</th>
            <th className="py-3 pr-4">Current</th>
            <th className="py-3 pr-4">Market Value</th>
            <th className="py-3 pr-4">Unrealized PnL</th>
            <th className="py-3 pr-4">Status</th>
          </tr>
        </thead>
        <tbody>
          {positions.map((position) => (
            <tr className="border-b last:border-0" key={`${position.account_id}-${position.symbol}`}>
              <td className="py-3 pr-4 font-medium">{position.symbol}</td>
              <td className="py-3 pr-4">{position.quantity.toFixed(6)}</td>
              <td className="py-3 pr-4">{formatPrice(position.average_entry_price)}</td>
              <td className="py-3 pr-4">{formatPrice(position.current_price)}</td>
              <td className="py-3 pr-4">{formatPrice(position.market_value)}</td>
              <td className="py-3 pr-4">
                {formatPrice(position.unrealized_pnl)} ({formatPercent(position.unrealized_pnl_pct)})
              </td>
              <td className="py-3 pr-4 capitalize">{position.status}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
