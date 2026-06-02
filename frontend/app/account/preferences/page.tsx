"use client";

import { useEffect, useState } from "react";

import { PageHeader } from "@/components/layout/PageHeader";
import { getUserPreferences } from "@/lib/api/users";
import type { UserPreference } from "@/lib/api/types";

export default function PreferencesPage() {
  const [preferences, setPreferences] = useState<UserPreference | null>(null);
  useEffect(() => {
    getUserPreferences().then(setPreferences).catch(() => setPreferences(null));
  }, []);
  return (
    <div>
      <PageHeader title="Preferences" description="Read-only view of default dashboard preferences for now." />
      <section className="rounded-lg border bg-card p-5 text-sm">
        <pre className="overflow-auto">{JSON.stringify(preferences ?? {}, null, 2)}</pre>
      </section>
    </div>
  );
}
