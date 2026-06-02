"use client";

import Link from "next/link";
import { useEffect, useState } from "react";

import { EmptyState } from "@/components/common/EmptyState";
import { SectionCard } from "@/components/common/SectionCard";
import { Button } from "@/components/ui/button";
import { getRelativeStrengthRanking } from "@/lib/api/market-comparison";
import type { RelativeStrengthSnapshot } from "@/lib/api/types";
import { formatScore } from "@/lib/format";

export function RelativeStrengthDashboardCard() {
  const [ranking, setRanking] = useState<RelativeStrengthSnapshot[]>([]);
  const [loaded, setLoaded] = useState(false);

  useEffect(() => {
    let active = true;
    getRelativeStrengthRanking(5)
      .then((response) => {
        if (active) {
          setRanking(response.data);
        }
      })
      .catch(() => {
        if (active) {
          setRanking([]);
        }
      })
      .finally(() => {
        if (active) {
          setLoaded(true);
        }
      });
    return () => {
      active = false;
    };
  }, []);

  return (
    <SectionCard
      title="BTC Relative Strength"
      description="Latest BRSI ranking across tracked major coins."
      action={
        <Button asChild size="sm" variant="outline">
          <Link href="/market-comparison">Open Monitor</Link>
        </Button>
      }
    >
      {loaded && ranking.length === 0 ? (
        <EmptyState message="Run the relative strength scheduler after OHLCV ingestion to populate BRSI rankings." />
      ) : (
        <div className="grid gap-3 md:grid-cols-5">
          {ranking.map((item) => (
            <div className="rounded-md border bg-background p-3" key={item.symbol}>
              <p className="text-sm font-semibold">{item.symbol}</p>
              <p className="mt-2 text-xl font-semibold">{formatScore(item.brsi_score)}</p>
              <p className="mt-1 text-xs text-muted-foreground">{item.status}</p>
            </div>
          ))}
          {!loaded
            ? Array.from({ length: 5 }).map((_, index) => (
                <div className="rounded-md border bg-background p-3" key={index}>
                  <p className="text-sm text-muted-foreground">Loading</p>
                  <p className="mt-2 text-xl font-semibold">...</p>
                </div>
              ))
            : null}
        </div>
      )}
    </SectionCard>
  );
}
