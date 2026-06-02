import { EmptyState } from "@/components/common/EmptyState";
import type { PaperOrder } from "@/lib/api/types";
import { formatDateTime, formatPrice } from "@/lib/format";

export function PaperOrderTable({ orders }: { orders: PaperOrder[] }) {
  if (!orders.length) {
    return <EmptyState message="No simulated orders found." />;
  }
  return (
    <div className="overflow-x-auto">
      <table className="w-full min-w-[920px] text-left text-sm">
        <thead className="border-b text-xs uppercase text-muted-foreground">
          <tr>
            <th className="py-3 pr-4">Created</th>
            <th className="py-3 pr-4">Symbol</th>
            <th className="py-3 pr-4">Action</th>
            <th className="py-3 pr-4">Notional</th>
            <th className="py-3 pr-4">Filled Price</th>
            <th className="py-3 pr-4">Fee</th>
            <th className="py-3 pr-4">Slippage</th>
            <th className="py-3 pr-4">Status</th>
            <th className="py-3 pr-4">Source</th>
          </tr>
        </thead>
        <tbody>
          {orders.map((order) => (
            <tr className="border-b last:border-0" key={order.order_id}>
              <td className="py-3 pr-4">{formatDateTime(order.created_at)}</td>
              <td className="py-3 pr-4 font-medium">{order.symbol}</td>
              <td className="py-3 pr-4">
                {order.side === "buy" ? "Add virtual exposure" : "Reduce virtual exposure"}
              </td>
              <td className="py-3 pr-4">{formatPrice(order.notional)}</td>
              <td className="py-3 pr-4">{formatPrice(order.filled_price)}</td>
              <td className="py-3 pr-4">{formatPrice(order.fee)}</td>
              <td className="py-3 pr-4">{formatPrice(order.slippage)}</td>
              <td className="py-3 pr-4 capitalize">{order.status}</td>
              <td className="py-3 pr-4">{order.source ?? "manual"}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
