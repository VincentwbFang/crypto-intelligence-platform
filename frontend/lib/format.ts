export function formatPrice(value: number | null | undefined) {
  if (value === null || value === undefined || Number.isNaN(value)) {
    return "N/A";
  }
  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "USD",
    maximumFractionDigits: value >= 100 ? 2 : 4
  }).format(value);
}

export function formatPercent(value: number | null | undefined) {
  if (value === null || value === undefined || Number.isNaN(value)) {
    return "N/A";
  }
  return `${value >= 0 ? "+" : ""}${value.toFixed(2)}%`;
}

export function formatScore(value: number | null | undefined) {
  if (value === null || value === undefined || Number.isNaN(value)) {
    return "N/A";
  }
  const clamped = Math.min(Math.max(value, 0), 100);
  return clamped.toFixed(1);
}

export function formatDateTime(value: string | null | undefined) {
  if (!value) {
    return "N/A";
  }
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) {
    return "N/A";
  }
  return new Intl.DateTimeFormat("en-US", {
    dateStyle: "medium",
    timeStyle: "short"
  }).format(date);
}

export function formatSymbolForRoute(symbol: string) {
  return symbol.replace("/", "-");
}

export function parseSymbolFromRoute(routeSymbol: string) {
  return routeSymbol.replace("-", "/").toUpperCase();
}

export function riskLevelLabel(level: string | null | undefined) {
  const labels: Record<string, string> = {
    low: "Low Risk",
    medium: "Medium Risk",
    high: "High Risk",
    extreme: "Extreme Risk"
  };
  return labels[String(level || "").toLowerCase()] ?? "Unknown Risk";
}

export function severityLabel(severity: string | null | undefined) {
  const labels: Record<string, string> = {
    info: "Info",
    low: "Low",
    medium: "Medium",
    high: "High",
    critical: "Critical"
  };
  return labels[String(severity || "").toLowerCase()] ?? "Unknown";
}

export function setupTypeLabel(setupType: string | null | undefined) {
  const labels: Record<string, string> = {
    trend_continuation: "Trend Continuation",
    breakout_watch: "Breakout Watch",
    mean_reversion_risk: "Mean Reversion Risk",
    breakdown_risk: "Breakdown Risk",
    range_bound: "Range Bound",
    insufficient_data: "Insufficient Data"
  };
  return labels[String(setupType || "").toLowerCase()] ?? "Unknown Setup";
}
