import Link from "next/link";

import { PageHeader } from "@/components/layout/PageHeader";
import { PaperAccountsTable } from "@/components/paper/PaperAccountsTable";
import { Button } from "@/components/ui/button";

export default function PaperAccountsPage() {
  return (
    <div>
      <PageHeader
        title="Virtual Accounts"
        description="Review paper trading accounts that use simulated balances only."
        action={
          <Button asChild>
            <Link href="/paper/accounts/new">New Virtual Account</Link>
          </Button>
        }
      />
      <PaperAccountsTable />
      <p className="mt-6 text-sm text-muted-foreground">
        Paper trading results are hypothetical and based on simulated execution. They do not
        guarantee future live trading performance.
      </p>
    </div>
  );
}
