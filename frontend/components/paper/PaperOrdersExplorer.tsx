"use client";

import { useState } from "react";

import { ErrorState } from "@/components/common/ErrorState";
import { PaperOrderTable } from "@/components/paper/PaperOrderTable";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Select } from "@/components/ui/select";
import { listPaperOrders } from "@/lib/api/paper";
import type { PaperOrder } from "@/lib/api/types";

export function PaperOrdersExplorer() {
  const [accountId, setAccountId] = useState("");
  const [status, setStatus] = useState("");
  const [orders, setOrders] = useState<PaperOrder[]>([]);
  const [error, setError] = useState<string | null>(null);

  async function loadOrders() {
    if (!accountId.trim()) {
      setError("Enter a virtual account id.");
      return;
    }
    setError(null);
    try {
      setOrders((await listPaperOrders(accountId.trim(), status || undefined, 100)).data);
    } catch (loadError) {
      setError(loadError instanceof Error ? loadError.message : "Orders failed.");
    }
  }

  return (
    <div className="space-y-4">
      <div className="grid gap-3 md:grid-cols-[1fr_180px_auto]">
        <Input
          aria-label="Account id"
          onChange={(event) => setAccountId(event.target.value)}
          placeholder="Account ID"
          value={accountId}
        />
        <Select
          aria-label="Order status"
          onChange={(event) => setStatus(event.target.value)}
          value={status}
        >
          <option value="">All statuses</option>
          <option value="filled">Filled</option>
          <option value="pending">Pending</option>
          <option value="rejected">Rejected</option>
          <option value="cancelled">Cancelled</option>
        </Select>
        <Button onClick={() => void loadOrders()} type="button">
          Load simulated orders
        </Button>
      </div>
      {error ? <ErrorState message={error} /> : null}
      <PaperOrderTable orders={orders} />
    </div>
  );
}
