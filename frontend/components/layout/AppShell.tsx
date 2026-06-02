import type { ReactNode } from "react";

import { AuthGuard } from "@/components/auth/AuthGuard";
import { Sidebar } from "@/components/layout/Sidebar";
import { TopNav } from "@/components/layout/TopNav";

export function AppShell({ children }: { children: ReactNode }) {
  return (
    <div className="min-h-screen bg-background">
      <div className="flex min-h-screen">
        <Sidebar />
        <div className="flex min-w-0 flex-1 flex-col">
          <TopNav />
          <main className="flex-1 px-4 py-6 lg:px-8">
            <AuthGuard>{children}</AuthGuard>
          </main>
          <footer className="border-t px-4 py-4 text-xs text-muted-foreground lg:px-8">
            This dashboard provides data-driven market intelligence for educational
            and research purposes only. It is not personalized financial advice.
          </footer>
        </div>
      </div>
    </div>
  );
}
