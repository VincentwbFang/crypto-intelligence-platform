"use client";

import { Button } from "@/components/ui/button";

export default function ErrorPage({
  reset
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  return (
    <main className="mx-auto flex min-h-screen max-w-xl flex-col items-center justify-center gap-4 p-6 text-center">
      <h1 className="text-2xl font-semibold">Something went wrong</h1>
      <p className="text-sm text-muted-foreground">
        The dashboard could not complete this request. Try again or check system status.
      </p>
      <Button onClick={reset}>Try again</Button>
    </main>
  );
}

