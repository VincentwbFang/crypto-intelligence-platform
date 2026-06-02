import Link from "next/link";

import { RegisterForm } from "@/components/auth/RegisterForm";
import { PageHeader } from "@/components/layout/PageHeader";

export default function RegisterPage() {
  return (
    <div className="mx-auto max-w-md">
      <PageHeader
        title="Create account"
        description="Create a workspace for market intelligence, alerts, backtests, and simulated paper activity."
      />
      <section className="rounded-lg border bg-card p-5">
        <RegisterForm />
      </section>
      <p className="mt-4 text-sm text-muted-foreground">
        Already registered? <Link className="text-primary" href="/auth/login">Sign in</Link>
      </p>
    </div>
  );
}
