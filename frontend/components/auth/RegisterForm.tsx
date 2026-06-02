"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { registerUser } from "@/lib/api/auth";
import { saveSession } from "@/lib/auth/session";

export function RegisterForm() {
  const router = useRouter();
  const [fullName, setFullName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  async function onSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!email || !password) {
      setError("Email and password are required.");
      return;
    }
    setLoading(true);
    setError(null);
    try {
      const response = await registerUser({
        email,
        password,
        full_name: fullName || null
      });
      saveSession(response.access_token, response.refresh_token);
      router.push("/dashboard");
    } catch (error_) {
      setError(error_ instanceof Error ? error_.message : "Registration failed.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <form className="space-y-4" onSubmit={onSubmit}>
      <label className="block text-sm font-medium">
        Full Name
        <Input className="mt-1" onChange={(event) => setFullName(event.target.value)} value={fullName} />
      </label>
      <label className="block text-sm font-medium">
        Email
        <Input
          autoComplete="email"
          className="mt-1"
          onChange={(event) => setEmail(event.target.value)}
          type="email"
          value={email}
        />
      </label>
      <label className="block text-sm font-medium">
        Password
        <Input
          autoComplete="new-password"
          className="mt-1"
          onChange={(event) => setPassword(event.target.value)}
          type="password"
          value={password}
        />
      </label>
      {error ? <p className="text-sm text-destructive">{error}</p> : null}
      <Button disabled={loading} type="submit">
        {loading ? "Creating account..." : "Create account"}
      </Button>
    </form>
  );
}
