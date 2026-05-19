import { Activity, Loader2, ServerOff } from "lucide-react";

type HealthBadgeProps = {
  status: "checking" | "online" | "offline";
};

export function HealthBadge({ status }: HealthBadgeProps) {
  const label = {
    checking: "Checking API",
    online: "API online",
    offline: "API offline",
  }[status];

  const Icon =
    status === "checking" ? Loader2 : status === "online" ? Activity : ServerOff;

  return (
    <div className="inline-flex h-9 items-center gap-2 rounded-full border border-border bg-surface-strong px-3 text-sm text-muted-foreground">
      <Icon
        className={`h-4 w-4 ${
          status === "checking"
            ? "animate-spin text-warning"
            : status === "online"
              ? "text-accent"
              : "text-danger"
        }`}
        aria-hidden="true"
      />
      <span>{label}</span>
    </div>
  );
}

