type EmptyStateProps = {
  title?: string;
  message?: string;
};

export function EmptyState({
  title = "No data yet",
  message = "Ingest market data or adjust filters to populate this view."
}: EmptyStateProps) {
  return (
    <div className="rounded-lg border border-dashed bg-card p-8 text-center">
      <p className="font-medium">{title}</p>
      <p className="mt-2 text-sm text-muted-foreground">{message}</p>
    </div>
  );
}
