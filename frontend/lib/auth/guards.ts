"use client";

export function isPublicAuthPath(pathname: string) {
  return pathname.startsWith("/auth/login") || pathname.startsWith("/auth/register");
}
