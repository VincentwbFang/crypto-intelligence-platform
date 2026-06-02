"use client";

import { useRouter } from "next/navigation";

import { Select } from "@/components/ui/select";
import { formatSymbolForRoute } from "@/lib/format";

type TokenSelectorProps = {
  value: string;
  symbols?: string[];
  basePath?: "tokens" | "signals";
};

export function TokenSelector({
  value,
  symbols = ["BTC/USDT", "ETH/USDT", "SOL/USDT"],
  basePath = "tokens"
}: TokenSelectorProps) {
  const router = useRouter();
  return (
    <Select
      aria-label="Select symbol"
      value={value}
      onChange={(event) =>
        router.push(`/${basePath}/${formatSymbolForRoute(event.target.value)}`)
      }
    >
      {symbols.map((symbol) => (
        <option key={symbol} value={symbol}>
          {symbol}
        </option>
      ))}
    </Select>
  );
}
