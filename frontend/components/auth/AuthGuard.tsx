"use client";

import type { ReactNode } from "react";
import { useEffect, useState } from "react";
import { usePathname, useRouter } from "next/navigation";

import { isPublicAuthPath } from "@/lib/auth/guards";
import { hasSession } from "@/lib/auth/session";

export function AuthGuard({ children }: { children: ReactNode }) {
  const pathname = usePathname();
  const router = useRouter();
  const [ready, setReady] = useState(false);

  useEffect(() => {
    if (!isPublicAuthPath(pathname) && !hasSession()) {
      router.replace("/auth/login");
      return;
    }
    setReady(true);
  }, [pathname, router]);

  if (isPublicAuthPath(pathname)) {
    return <>{children}</>;
  }

  if (!ready) {
    return <div className="rounded-lg border bg-card p-6 text-sm text-muted-foreground">Checking session...</div>;
  }

  return <>{children}</>;
}
