type RealitySignalProps = {
  label: string;
  value: string;
  tone: "accent" | "warning" | "danger";
};

export function RealitySignal({ label, value, tone }: RealitySignalProps) {
  const toneClass = {
    accent: "text-accent",
    warning: "text-warning",
    danger: "text-danger",
  }[tone];

  return (
    <div className="rc-subtle-panel p-4">
      <p className="text-sm text-muted-foreground">{label}</p>
      <p className={`mt-2 text-2xl font-semibold ${toneClass}`}>{value}</p>
    </div>
  );
}

