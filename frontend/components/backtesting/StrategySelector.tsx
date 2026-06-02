import { Select } from "@/components/ui/select";
import type { BacktestStrategyInfo } from "@/lib/api/types";

export function StrategySelector({
  strategies,
  value,
  onChange
}: {
  strategies: BacktestStrategyInfo[];
  value: string;
  onChange: (value: string) => void;
}) {
  return (
    <Select
      aria-label="Strategy"
      onChange={(event) => onChange(event.target.value)}
      value={value}
    >
      {strategies.map((strategy) => (
        <option key={strategy.name} value={strategy.name}>
          {strategy.name.replaceAll("_", " ")}
        </option>
      ))}
    </Select>
  );
}
