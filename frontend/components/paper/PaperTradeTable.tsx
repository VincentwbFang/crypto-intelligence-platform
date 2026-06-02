import { EmptyState } from "@/components/common/EmptyState";
import type { PaperTrade } from "@/lib/api/types";
import { formatDateTime, formatPercent, formatPrice } from "@/lib/format";

export function PaperTradeTable({ trades }: { trades: PaperTrade[] }) {
  if (!trades.length) {
    return <EmptyState message="No simulated trade history yet." />;
  }
  return (
    <div className="overflow-x-auto">
      <table className="w-full min-w-[880px] text-left text-sm">
        <thead className="border-b text-xs uppercase text-muted-foreground">
          <tr>
            <th className="py-3 pr-4">Exit Time</th>
            <th className="py-3 pr-4">Symbol</th>
            <th className="py-3 pr-4">Quantity</th>
            <th className="py-3 pr-4">Entry</th>
            <th className="py-3 pr-4">Exit</th>
            <th className="py-3 pr-4">Realized PnL</th>
            <th className="py-3 pr-4">Reason</th>
          </tr>
        </thead>
        <tbody>
          {trades.map((trade) => (
            <tr className="border-b last:border-0" key={trade.trade_id ?? trade.id}>
              <td className="py-3 pr-4">{formatDateTime(trade.exit_time)}</td>
              <td className="py-3 pr-4 font-medium">{trade.symbol}</td>
              <td className="py-3 pr-4">{trade.quantity?.toFixed(6) ?? "N/A"}</td>
              <td className="py-3 pr-4">{formatPrice(trade.entry_price)}</td>
              <td className="py-3 pr-4">{formatPrice(trade.exit_price)}</td>
              <td className="py-3 pr-4">
                {formatPrice(trade.realized_pnl)} ({formatPercent(trade.realized_pnl_pct)})
              </td>
              <td className="py-3 pr-4">{trade.exit_reason ?? "simulated order"}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
