import type { ReactNode } from "react";

import { cn } from "@/lib/utils";

type SectionCardProps = {
  title?: string;
  description?: string;
  children: ReactNode;
  className?: string;
  action?: ReactNode;
};

export function SectionCard({
  title,
  description,
  children,
  className,
  action
}: SectionCardProps) {
  return (
    <section className={cn("rounded-lg border bg-card p-5 shadow-panel", className)}>
      {(title || description || action) && (
        <div className="mb-4 flex items-start justify-between gap-4">
          <div>
            {title ? <h2 className="text-base font-semibold">{title}</h2> : null}
            {description ? (
              <p className="mt-1 text-sm text-muted-foreground">{description}</p>
            ) : null}
          </div>
          {action}
        </div>
      )}
      {children}
    </section>
  );
}
