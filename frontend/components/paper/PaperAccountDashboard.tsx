"use client";

import { useEffect, useState } from "react";

import { EmptyState } from "@/components/common/EmptyState";
import { ErrorState } from "@/components/common/ErrorState";
import { LoadingState } from "@/components/common/LoadingState";
import { PaperEquityChart } from "@/components/paper/PaperEquityChart";
import { PaperExplanationCard } from "@/components/paper/PaperExplanationCard";
import { PaperOrderForm } from "@/components/paper/PaperOrderForm";
import { PaperOrderTable } from "@/components/paper/PaperOrderTable";
import { PaperPerformanceGrid } from "@/components/paper/PaperPerformanceGrid";
import { PaperPortfolioSummary } from "@/components/paper/PaperPortfolioSummary";
import { PaperPositionTable } from "@/components/paper/PaperPositionTable";
import { PaperTradeTable } from "@/components/paper/PaperTradeTable";
import { SignalPaperExecutionPanel } from "@/components/paper/SignalPaperExecutionPanel";
import { Button } from "@/components/ui/button";
import {
  activatePaperAccount,
  explainPaperPortfolio,
  getPaperPerformance,
  getPaperPortfolio,
  listPaperOrders,
  listPaperTrades,
  pausePaperAccount,
  refreshPaperPortfolio
} from "@/lib/api/paper";
import type {
  AIPaperTradingExplanation,
  PaperOrder,
  PaperPerformance,
  PaperPortfolio,
  PaperTrade
} from "@/lib/api/types";

export function PaperAccountDashboard({ accountId }: { accountId: string }) {
  const [portfolio, setPortfolio] = useState<PaperPortfolio | null>(null);
  const [performance, setPerformance] = useState<PaperPerformance | null>(null);
  const [orders, setOrders] = useState<PaperOrder[]>([]);
  const [trades, setTrades] = useState<PaperTrade[]>([]);
  const [explanation, setExplanation] = useState<AIPaperTradingExplanation | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  async function load() {
    setError(null);
    try {
      const [portfolioResult, performanceResult, orderResult, tradeResult] =
        await Promise.all([
          getPaperPortfolio(accountId),
          getPaperPerformance(accountId),
          listPaperOrders(accountId, undefined, 20),
          listPaperTrades(accountId, undefined, 20)
        ]);
      setPortfolio(portfolioResult);
      setPerformance(performanceResult);
      setOrders(orderResult.data);
      setTrades(tradeResult.data);
    } catch (loadError) {
      setError(loadError instanceof Error ? loadError.message : "Paper account failed.");
    } finally {
      setIsLoading(false);
    }
  }

  useEffect(() => {
    void load();
  }, [accountId]);

  async function refresh() {
    try {
      setPortfolio(await refreshPaperPortfolio(accountId));
      setPerformance(await getPaperPerformance(accountId));
    } catch (refreshError) {
      setError(refreshError instanceof Error ? refreshError.message : "Refresh failed.");
    }
  }

  async function explain() {
    try {
      setExplanation(await explainPaperPortfolio(accountId));
    } catch (explainError) {
      setError(explainError instanceof Error ? explainError.message : "Explanation failed.");
    }
  }

  if (isLoading) {
    return <LoadingState label="Loading paper portfolio" />;
  }
  if (error) {
    return <ErrorState message={error} />;
  }
  if (!portfolio || !performance) {
    return <EmptyState message="Paper account data is unavailable." />;
  }
  const snapshot = portfolio.equity_snapshot ? [portfolio.equity_snapshot] : [];
  return (
    <div className="space-y-6">
      <div className="flex flex-wrap gap-2">
        <Button onClick={() => void refresh()} type="button" variant="outline">
          Refresh Portfolio
        </Button>
        <Button
          onClick={() =>
            void (portfolio.account.status === "paused"
              ? activatePaperAccount(accountId)
              : pausePaperAccount(accountId)).then(load)
          }
          type="button"
          variant="outline"
        >
          {portfolio.account.status === "paused" ? "Activate Account" : "Pause Account"}
        </Button>
        <Button onClick={() => void explain()} type="button" variant="outline">
          Explain Simulated Portfolio
        </Button>
      </div>
      <PaperPortfolioSummary portfolio={portfolio} />
      <PaperPerformanceGrid performance={performance} />
      <PaperEquityChart snapshots={snapshot} />
      <PaperOrderForm accountId={accountId} onSubmitted={() => void load()} />
      <SignalPaperExecutionPanel accountId={accountId} />
      <PaperPositionTable positions={portfolio.positions} />
      <PaperOrderTable orders={orders} />
      <PaperTradeTable trades={trades} />
      <PaperExplanationCard explanation={explanation} />
      <p className="text-sm text-muted-foreground">
        Paper trading results are hypothetical and based on simulated execution. They do not
        guarantee future live trading performance.
      </p>
    </div>
  );
}
