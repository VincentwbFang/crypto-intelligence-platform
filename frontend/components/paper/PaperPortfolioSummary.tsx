import { StatCard } from "@/components/common/StatCard";
import type { PaperPortfolio } from "@/lib/api/types";
import { formatPrice } from "@/lib/format";

export function PaperPortfolioSummary({ portfolio }: { portfolio: PaperPortfolio }) {
  return (
    <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
      <StatCard label="Virtual Cash" value={formatPrice(portfolio.account.cash_balance)} />
      <StatCard label="Equity" value={formatPrice(portfolio.account.equity)} />
      <StatCard label="Realized PnL" value={formatPrice(portfolio.account.realized_pnl)} />
      <StatCard label="Open Positions" value={String(portfolio.positions.length)} />
    </div>
  );
}
