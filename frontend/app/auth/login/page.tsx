import Link from "next/link";

import { LoginForm } from "@/components/auth/LoginForm";
import { PageHeader } from "@/components/layout/PageHeader";

export default function LoginPage() {
  return (
    <div className="mx-auto max-w-md">
      <PageHeader
        title="Sign in"
        description="Access your research workspace and saved market intelligence views."
      />
      <section className="rounded-lg border bg-card p-5">
        <LoginForm />
      </section>
      <p className="mt-4 text-sm text-muted-foreground">
        New here? <Link className="text-primary" href="/auth/register">Create an account</Link>
      </p>
    </div>
  );
}
