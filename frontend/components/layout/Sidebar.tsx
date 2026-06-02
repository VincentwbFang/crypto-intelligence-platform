"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  Activity,
  Bell,
  BarChart3,
  Building2,
  Gauge,
  History,
  LineChart,
  ListChecks,
  ServerCog,
  UserCircle,
  Settings,
  ShieldCheck,
  WalletCards
} from "lucide-react";

import { cn } from "@/lib/utils";

const items = [
  { href: "/dashboard", label: "Dashboard", icon: Gauge },
  { href: "/markets", label: "Markets", icon: LineChart },
  { href: "/market-comparison", label: "BTC RS Monitor", icon: Activity },
  { href: "/signals", label: "Signals", icon: BarChart3 },
  { href: "/alerts", label: "Alerts", icon: Bell },
  { href: "/backtests", label: "Backtests", icon: History },
  { href: "/paper", label: "Paper Trading", icon: WalletCards },
  { href: "/workspaces", label: "Workspaces", icon: Building2 },
  { href: "/watchlists", label: "Watchlists", icon: ListChecks },
  { href: "/usage", label: "Usage", icon: ShieldCheck },
  { href: "/system", label: "System", icon: ServerCog },
  { href: "/account", label: "Account", icon: UserCircle },
  { href: "/settings", label: "Settings", icon: Settings }
];

export function Sidebar() {
  const pathname = usePathname();
  return (
    <aside className="hidden w-64 border-r bg-card lg:block">
      <div className="flex h-16 items-center gap-2 border-b px-5">
        <Activity className="h-5 w-5 text-primary" />
        <span className="font-semibold">Crypto Intelligence</span>
      </div>
      <nav className="space-y-1 p-3">
        {items.map((item) => {
          const Icon = item.icon;
          const active = pathname === item.href || pathname.startsWith(`${item.href}/`);
          return (
            <Link
              className={cn(
                "flex items-center gap-3 rounded-md px-3 py-2 text-sm text-muted-foreground hover:bg-muted hover:text-foreground",
                active && "bg-muted text-foreground"
              )}
              href={item.href}
              key={item.href}
            >
              <Icon className="h-4 w-4" />
              {item.label}
            </Link>
          );
        })}
      </nav>
    </aside>
  );
}
