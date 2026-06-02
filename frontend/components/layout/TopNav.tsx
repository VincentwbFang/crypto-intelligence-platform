import Link from "next/link";
import { Activity } from "lucide-react";

import { WorkspaceSwitcher } from "@/components/workspace/WorkspaceSwitcher";

export function TopNav() {
  return (
    <header className="sticky top-0 z-20 border-b bg-background/95 backdrop-blur">
      <div className="flex h-16 items-center justify-between px-4 lg:px-6">
        <Link className="flex items-center gap-2 font-semibold lg:hidden" href="/dashboard">
          <Activity className="h-5 w-5 text-primary" />
          Crypto Intelligence
        </Link>
        <div className="hidden text-sm text-muted-foreground lg:block">
          Data-driven market intelligence and risk monitoring
        </div>
        <WorkspaceSwitcher />
      </div>
    </header>
  );
}
