import Link from "next/link";

import { Button } from "@/components/ui/button";
import type { PaperAccount } from "@/lib/api/types";
import { formatDateTime, formatPrice, formatPercent } from "@/lib/format";

type PaperAccountCardProps = {
  account: PaperAccount;
};

export function PaperAccountCard({ account }: PaperAccountCardProps) {
  const returnPct =
    account.initial_balance > 0
      ? ((account.equity - account.initial_balance) / account.initial_balance) * 100
      : 0;
  return (
    <article className="rounded-lg border bg-card p-4">
      <div className="flex items-start justify-between gap-4">
        <div>
          <h3 className="font-semibold">{account.name}</h3>
          <p className="text-sm text-muted-foreground">{account.account_id}</p>
        </div>
        <span className="rounded-full border px-2 py-1 text-xs capitalize">
          {account.status}
        </span>
      </div>
      <div className="mt-4 grid gap-3 text-sm sm:grid-cols-2">
        <div>
          <p className="text-muted-foreground">Equity</p>
          <p className="font-medium">{formatPrice(account.equity)}</p>
        </div>
        <div>
          <p className="text-muted-foreground">Cash</p>
          <p className="font-medium">{formatPrice(account.cash_balance)}</p>
        </div>
        <div>
          <p className="text-muted-foreground">Simulated Return</p>
          <p className="font-medium">{formatPercent(returnPct)}</p>
        </div>
        <div>
          <p className="text-muted-foreground">Created</p>
          <p className="font-medium">{formatDateTime(account.created_at)}</p>
        </div>
      </div>
      <Button asChild className="mt-4" size="sm" variant="outline">
        <Link href={`/paper/accounts/${account.account_id}`}>View Portfolio</Link>
      </Button>
    </article>
  );
}
