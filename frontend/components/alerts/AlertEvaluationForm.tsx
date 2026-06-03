"use client";

import type { FormEvent } from "react";
import { useState } from "react";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Select } from "@/components/ui/select";
import { evaluateAlerts } from "@/lib/api/alerts";
import { TOP_30_MARKET_SYMBOLS_TEXT } from "@/lib/market-universe";
import type { AlertEvaluateResponse } from "@/lib/api/types";

type AlertEvaluationFormProps = {
  onEvaluated?: (result: AlertEvaluateResponse) => void;
};

export function AlertEvaluationForm({ onEvaluated }: AlertEvaluationFormProps) {
  const [symbols, setSymbols] = useState(TOP_30_MARKET_SYMBOLS_TEXT);
  const [timeframe, setTimeframe] = useState("1h");
  const [limit, setLimit] = useState(200);
  const [isLoading, setIsLoading] = useState(false);
  const [message, setMessage] = useState<string | null>(null);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setIsLoading(true);
    setMessage(null);
    try {
      const result = await evaluateAlerts({
        symbols: symbols.split(",").map((symbol) => symbol.trim()).filter(Boolean),
        timeframe,
        limit,
        send_notifications: false
      });
      setMessage(
        `Evaluation completed. ${result.generated_alerts} new alerts, ${result.deduplicated_alerts} deduplicated.`
      );
      onEvaluated?.(result);
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "Alert evaluation failed.");
    } finally {
      setIsLoading(false);
    }
  }

  return (
    <form className="grid gap-3 md:grid-cols-[1fr_120px_120px_auto]" onSubmit={handleSubmit}>
      <Input
        aria-label="Symbols"
        onChange={(event) => setSymbols(event.target.value)}
        value={symbols}
      />
      <Select
        aria-label="Timeframe"
        onChange={(event) => setTimeframe(event.target.value)}
        value={timeframe}
      >
        <option value="1h">1h</option>
        <option value="4h">4h</option>
        <option value="1d">1d</option>
      </Select>
      <Input
        aria-label="Limit"
        min={2}
        onChange={(event) => setLimit(Number(event.target.value))}
        type="number"
        value={limit}
      />
      <Button disabled={isLoading} type="submit">
        {isLoading ? "Evaluating" : "Evaluate Alerts"}
      </Button>
      {message ? (
        <p className="md:col-span-4 text-sm text-muted-foreground">{message}</p>
      ) : null}
    </form>
  );
}
