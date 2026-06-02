"use client";

import { useState } from "react";
import type { FormEvent } from "react";
import { useRouter } from "next/navigation";

import { ErrorState } from "@/components/common/ErrorState";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { createPaperAccount } from "@/lib/api/paper";

export function PaperAccountForm() {
  const router = useRouter();
  const [name, setName] = useState("Main Paper Account");
  const [initialBalance, setInitialBalance] = useState("10000");
  const [error, setError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  async function submitAccount(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError(null);
    const balance = Number(initialBalance);
    if (!name.trim() || !Number.isFinite(balance) || balance <= 0) {
      setError("Enter an account name and a positive virtual balance.");
      return;
    }
    setIsSubmitting(true);
    try {
      const account = await createPaperAccount({
        name: name.trim(),
        initial_balance: balance
      });
      router.push(`/paper/accounts/${account.account_id}`);
    } catch (createError) {
      setError(createError instanceof Error ? createError.message : "Account creation failed.");
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <form className="space-y-4" onSubmit={(event) => void submitAccount(event)}>
      {error ? <ErrorState message={error} /> : null}
      <label className="block text-sm font-medium">
        Account Name
        <Input
          className="mt-1"
          onChange={(event) => setName(event.target.value)}
          value={name}
        />
      </label>
      <label className="block text-sm font-medium">
        Initial Virtual Balance
        <Input
          className="mt-1"
          min="1"
          onChange={(event) => setInitialBalance(event.target.value)}
          type="number"
          value={initialBalance}
        />
      </label>
      <Button disabled={isSubmitting} type="submit">
        Create Virtual Account
      </Button>
    </form>
  );
}
