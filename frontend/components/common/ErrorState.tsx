type ErrorStateProps = {
  title?: string;
  message?: string;
};

export function ErrorState({
  title = "Data unavailable",
  message = "The dashboard could not load this section."
}: ErrorStateProps) {
  return (
    <div role="alert" className="rounded-lg border border-red-200 bg-red-50 p-5">
      <p className="font-medium text-red-800">{title}</p>
      <p className="mt-1 text-sm text-red-700">{message}</p>
    </div>
  );
}
