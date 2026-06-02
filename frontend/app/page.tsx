import Link from "next/link";
import { ArrowRight } from "lucide-react";

import { Button } from "@/components/ui/button";

export default function HomePage() {
  return (
    <div className="mx-auto flex max-w-3xl flex-col gap-6 py-16">
      <div>
        <p className="text-sm font-medium text-primary">Market intelligence</p>
        <h1 className="mt-3 text-4xl font-semibold tracking-normal">
          Crypto Market Intelligence Platform
        </h1>
        <p className="mt-4 text-muted-foreground">
          View deterministic signals, market snapshots, risk alerts, and
          research-only AI explanations from one operational dashboard.
        </p>
      </div>
      <Button asChild className="w-fit">
        <Link href="/dashboard">
          Open Dashboard
          <ArrowRight className="h-4 w-4" />
        </Link>
      </Button>
    </div>
  );
}
