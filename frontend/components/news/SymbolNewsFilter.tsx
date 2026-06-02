"use client";

import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";

const symbols = ["ALL", "BTC", "ETH", "SOL", "XRP", "BNB", "STABLECOIN", "EXCHANGE", "POLICY"];

export function SymbolNewsFilter({
  value,
  onChange
}: {
  value: string;
  onChange: (symbol: string) => void;
}) {
  return (
    <div className="flex flex-wrap gap-2">
      {symbols.map((symbol) => (
        <Button
          className={cn(value === symbol && "border-primary text-primary")}
          key={symbol}
          onClick={() => onChange(symbol)}
          size="sm"
          type="button"
          variant="outline"
        >
          {symbol}
        </Button>
      ))}
    </div>
  );
}
