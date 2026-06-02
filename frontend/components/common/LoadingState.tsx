export function LoadingState({ label = "Loading data" }: { label?: string }) {
  return (
    <div className="rounded-lg border bg-card p-6 text-sm text-muted-foreground">
      {label}...
    </div>
  );
}
