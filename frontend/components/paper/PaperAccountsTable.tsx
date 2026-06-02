"use client";

import { useEffect, useState } from "react";

import { EmptyState } from "@/components/common/EmptyState";
import { ErrorState } from "@/components/common/ErrorState";
import { LoadingState } from "@/components/common/LoadingState";
import { PaperAccountCard } from "@/components/paper/PaperAccountCard";
import { listPaperAccounts } from "@/lib/api/paper";
import type { PaperAccount } from "@/lib/api/types";

export function PaperAccountsTable() {
  const [accounts, setAccounts] = useState<PaperAccount[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function loadAccounts() {
      setError(null);
      try {
        setAccounts((await listPaperAccounts()).data);
      } catch (loadError) {
        setError(loadError instanceof Error ? loadError.message : "Accounts failed.");
      } finally {
        setIsLoading(false);
      }
    }
    void loadAccounts();
  }, []);

  if (isLoading) {
    return <LoadingState label="Loading virtual accounts" />;
  }
  if (error) {
    return <ErrorState message={error} />;
  }
  if (!accounts.length) {
    return <EmptyState message="No virtual accounts are stored yet." />;
  }
  return (
    <div className="grid gap-4 lg:grid-cols-2">
      {accounts.map((account) => (
        <PaperAccountCard account={account} key={account.account_id} />
      ))}
    </div>
  );
}
