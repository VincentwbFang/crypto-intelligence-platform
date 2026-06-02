import Link from "next/link";

import { PageHeader } from "@/components/layout/PageHeader";
import { PaperOverview } from "@/components/paper/PaperOverview";
import { Button } from "@/components/ui/button";

export default function PaperTradingPage() {
  return (
    <div>
      <PageHeader
        title="Paper Trading"
        description="Virtual capital, simulated fills, and research-only portfolio monitoring."
        action={
          <Button asChild>
            <Link href="/paper/accounts/new">Create Virtual Account</Link>
          </Button>
        }
      />
      <PaperOverview />
      <p className="mt-6 text-sm text-muted-foreground">
        Paper trading uses simulated orders and virtual capital. No real order is placed.
      </p>
    </div>
  );
}
