"use client";

import type { FormEvent } from "react";
import { useState } from "react";

import { ErrorState } from "@/components/common/ErrorState";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Select } from "@/components/ui/select";
import { submitPaperOrder } from "@/lib/api/paper";
import type { PaperOrder } from "@/lib/api/types";

type PaperOrderFormProps = {
  accountId: string;
  onSubmitted?: (order: PaperOrder) => void;
};

export function PaperOrderForm({ accountId, onSubmitted }: PaperOrderFormProps) {
  const [symbol, setSymbol] = useState("BTC/USDT");
  const [timeframe, setTimeframe] = useState("1h");
  const [side, setSide] = useState<"buy" | "sell">("buy");
  const [notional, setNotional] = useState("500");
  const [reason, setReason] = useState("Manual research-only simulated order");
  const [error, setError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  async function submitOrder(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const numericNotional = Number(notional);
    if (!Number.isFinite(numericNotional) || numericNotional <= 0) {
      setError("Enter a positive simulated notional amount.");
      return;
    }
    setError(null);
    setIsSubmitting(true);
    try {
      const order = await submitPaperOrder({
        account_id: accountId,
        symbol,
        timeframe,
        side,
        order_type: "market",
        notional: numericNotional,
        reason
      });
      onSubmitted?.(order);
    } catch (submitError) {
      setError(submitError instanceof Error ? submitError.message : "Simulated order failed.");
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <form className="space-y-4" noValidate onSubmit={(event) => void submitOrder(event)}>
      {error ? <ErrorState message={error} /> : null}
      <div className="grid gap-3 md:grid-cols-2">
        <label className="block text-sm font-medium">
          Symbol
          <Input
            className="mt-1"
            onChange={(event) => setSymbol(event.target.value)}
            value={symbol}
          />
        </label>
        <label className="block text-sm font-medium">
          Timeframe
          <Select
            className="mt-1"
            onChange={(event) => setTimeframe(event.target.value)}
            value={timeframe}
          >
            <option value="1h">1h</option>
            <option value="4h">4h</option>
            <option value="1d">1d</option>
          </Select>
        </label>
        <label className="block text-sm font-medium">
          Simulated Action
          <Select
            className="mt-1"
            onChange={(event) => setSide(event.target.value as "buy" | "sell")}
            value={side}
          >
            <option value="buy">Add virtual exposure</option>
            <option value="sell">Reduce virtual exposure</option>
          </Select>
        </label>
        <label className="block text-sm font-medium">
          Notional
          <Input
            className="mt-1"
            min="1"
            onChange={(event) => setNotional(event.target.value)}
            type="number"
            value={notional}
          />
        </label>
      </div>
      <label className="block text-sm font-medium">
        Reason
        <Input
          className="mt-1"
          onChange={(event) => setReason(event.target.value)}
          value={reason}
        />
      </label>
      <Button disabled={isSubmitting} type="submit">
        Submit simulated order
      </Button>
    </form>
  );
}
