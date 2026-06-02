"use client";

import Link from "next/link";
import { useEffect, useState } from "react";

import { EmptyState } from "@/components/common/EmptyState";
import { ErrorState } from "@/components/common/ErrorState";
import { LoadingState } from "@/components/common/LoadingState";
import { PaperAccountCard } from "@/components/paper/PaperAccountCard";
import { PaperOrderTable } from "@/components/paper/PaperOrderTable";
import { Button } from "@/components/ui/button";
import { listPaperAccounts, listPaperOrders } from "@/lib/api/paper";
import type { PaperAccount, PaperOrder } from "@/lib/api/types";

export function PaperOverview() {
  const [accounts, setAccounts] = useState<PaperAccount[]>([]);
  const [orders, setOrders] = useState<PaperOrder[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function load() {
      setError(null);
      setIsLoading(true);
      try {
        const accountResult = await listPaperAccounts();
        setAccounts(accountResult.data);
        if (accountResult.data[0]) {
          const orderResult = await listPaperOrders(accountResult.data[0].account_id, undefined, 10);
          setOrders(orderResult.data);
        }
      } catch (loadError) {
        setError(loadError instanceof Error ? loadError.message : "Paper trading data failed.");
      } finally {
        setIsLoading(false);
      }
    }
    void load();
  }, []);

  if (isLoading) {
    return <LoadingState label="Loading paper trading data" />;
  }
  return (
    <div className="space-y-6">
      {error ? <ErrorState message={error} /> : null}
      {accounts.length ? (
        <div className="grid gap-4 lg:grid-cols-2">
          {accounts.slice(0, 4).map((account) => (
            <PaperAccountCard account={account} key={account.account_id} />
          ))}
        </div>
      ) : (
        <EmptyState message="No virtual accounts exist yet." />
      )}
      <div className="flex justify-end">
        <Button asChild variant="outline">
          <Link href="/paper/accounts/new">Create Virtual Account</Link>
        </Button>
      </div>
      <PaperOrderTable orders={orders} />
    </div>
  );
}
