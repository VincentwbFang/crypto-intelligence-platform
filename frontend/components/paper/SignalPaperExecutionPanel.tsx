"use client";

import { useState } from "react";

import { ErrorState } from "@/components/common/ErrorState";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { runSignalPaperExecution } from "@/lib/api/paper";
import type { SignalPaperExecutionResult } from "@/lib/api/types";

export function SignalPaperExecutionPanel({ accountId }: { accountId: string }) {
  const [symbol, setSymbol] = useState("BTC/USDT");
  const [timeframe, setTimeframe] = useState("1h");
  const [result, setResult] = useState<SignalPaperExecutionResult | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isRunning, setIsRunning] = useState(false);

  async function runSimulation() {
    setError(null);
    setIsRunning(true);
    try {
      setResult(await runSignalPaperExecution(accountId, { symbol, timeframe, limit: 200 }));
    } catch (runError) {
      setError(runError instanceof Error ? runError.message : "Signal simulation failed.");
    } finally {
      setIsRunning(false);
    }
  }

  return (
    <div className="space-y-4">
      {error ? <ErrorState message={error} /> : null}
      <div className="grid gap-3 md:grid-cols-[1fr_120px_auto]">
        <Input
          aria-label="Signal symbol"
          onChange={(event) => setSymbol(event.target.value)}
          value={symbol}
        />
        <Input
          aria-label="Signal timeframe"
          onChange={(event) => setTimeframe(event.target.value)}
          value={timeframe}
        />
        <Button disabled={isRunning} onClick={() => void runSimulation()} type="button">
          Run research-only signal simulation
        </Button>
      </div>
      {result ? (
        <div className="rounded-md border p-3 text-sm">
          <p className="font-medium">{result.action_taken ?? result.message}</p>
          <p className="mt-1 text-muted-foreground">{result.reason ?? result.disclaimer}</p>
        </div>
      ) : null}
    </div>
  );
}
