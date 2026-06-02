import type { WatchlistSymbol } from "@/lib/api/types";

export function WatchlistSymbolTable({
  symbols,
  onRemove
}: {
  symbols: WatchlistSymbol[];
  onRemove?: (symbol: string) => void;
}) {
  if (!symbols.length) {
    return <div className="rounded-lg border bg-card p-6 text-sm text-muted-foreground">No symbols in this watchlist.</div>;
  }
  return (
    <div className="overflow-hidden rounded-lg border">
      <table className="w-full text-sm">
        <tbody>
          {symbols.map((symbol) => (
            <tr className="border-t first:border-t-0" key={symbol.symbol}>
              <td className="p-3 font-medium">{symbol.symbol}</td>
              <td className="p-3 text-right">
                {onRemove ? (
                  <button className="text-sm text-muted-foreground hover:text-foreground" onClick={() => onRemove(symbol.symbol)} type="button">
                    Remove
                  </button>
                ) : null}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
