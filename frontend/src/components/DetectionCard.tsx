import { CheckCircle2, CircleDashed, type LucideIcon } from "lucide-react";

type DetectionCardProps = {
  detected: boolean;
  icon: LucideIcon;
  label: string;
  note: string;
};

export function DetectionCard({
  detected,
  icon: Icon,
  label,
  note,
}: DetectionCardProps) {
  const StatusIcon = detected ? CheckCircle2 : CircleDashed;

  return (
    <div className="rc-subtle-panel p-4 transition hover:border-accent/40">
      <div className="flex items-start justify-between gap-3">
        <span className="grid h-9 w-9 place-items-center rounded-lg border border-border bg-background/70">
          <Icon className="h-4 w-4 text-accent" aria-hidden={true} />
        </span>
        <StatusIcon
          className={`h-4 w-4 ${detected ? "text-accent" : "text-muted-foreground"}`}
          aria-hidden={true}
        />
      </div>
      <p className="mt-4 text-sm font-medium">{label}</p>
      <p className="mt-1 text-sm leading-6 text-muted-foreground">{note}</p>
    </div>
  );
}
