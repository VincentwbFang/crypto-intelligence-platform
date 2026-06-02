"use client";

import { useEffect, useState } from "react";

import { PageHeader } from "@/components/layout/PageHeader";
import { Button } from "@/components/ui/button";
import { getCurrentUser } from "@/lib/api/users";
import { clearSession } from "@/lib/auth/session";
import type { AuthUser } from "@/lib/api/types";

export default function AccountPage() {
  const [user, setUser] = useState<AuthUser | null>(null);

  useEffect(() => {
    getCurrentUser().then(setUser).catch(() => setUser(null));
  }, []);

  function logout() {
    clearSession();
    window.location.href = "/auth/login";
  }

  return (
    <div>
      <PageHeader title="Account" description="Review your local prototype session and profile." />
      <section className="rounded-lg border bg-card p-5">
        <dl className="grid gap-3 text-sm md:grid-cols-2">
          <div>
            <dt className="text-muted-foreground">Email</dt>
            <dd className="font-medium">{user?.email ?? "Loading..."}</dd>
          </div>
          <div>
            <dt className="text-muted-foreground">Name</dt>
            <dd className="font-medium">{user?.full_name ?? "Not set"}</dd>
          </div>
        </dl>
        <Button className="mt-4" onClick={logout} variant="outline">Sign out</Button>
      </section>
      <p className="mt-6 text-sm text-muted-foreground">
        LocalStorage token storage is suitable for this local MVP only; production should use hardened cookie sessions.
      </p>
    </div>
  );
}
