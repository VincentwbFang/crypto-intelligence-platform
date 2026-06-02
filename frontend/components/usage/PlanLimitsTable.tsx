import type { PlanLimits } from "@/lib/api/types";

export function PlanLimitsTable({ limits }: { limits: PlanLimits }) {
  return (
    <div className="overflow-hidden rounded-lg border">
      <table className="w-full text-sm">
        <thead className="bg-muted text-left">
          <tr>
            <th className="p-3">Limit</th>
            <th className="p-3">Value</th>
          </tr>
        </thead>
        <tbody>
          {Object.entries(limits.limits).map(([key, value]) => (
            <tr className="border-t" key={key}>
              <td className="p-3">{key}</td>
              <td className="p-3">{String(value)}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
