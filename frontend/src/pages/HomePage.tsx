import {
  ArrowRight,
  Box,
  Code2,
  FileSearch,
  GitBranch,
  ShieldCheck,
  TerminalSquare,
} from "lucide-react";

import { HealthBadge } from "@/components/HealthBadge";
import { RealitySignal } from "@/components/RealitySignal";
import { useApiHealth } from "@/hooks/useApiHealth";

const signals = [
  { label: "Docs claims", value: "README, docs", tone: "accent" as const },
  { label: "Code reality", value: "API, env, config", tone: "warning" as const },
  { label: "Gap reports", value: "Risk-scored", tone: "danger" as const },
];

const stackItems = [
  { icon: FileSearch, label: "Repository scanning" },
  { icon: Code2, label: "API contract analysis" },
  { icon: TerminalSquare, label: "Config validation" },
  { icon: Box, label: "Deployment checks" },
];

export function HomePage() {
  const health = useApiHealth();

  return (
    <>
      <section className="mx-auto flex min-h-[calc(100vh-4rem)] w-full max-w-7xl flex-col justify-center px-6 py-14">
        <div className="max-w-3xl">
          <HealthBadge status={health.status} />
          <p className="mt-8 text-sm font-medium uppercase text-accent">
            Software reality gap detector
          </p>
          <h1 className="mt-5 text-5xl font-semibold leading-tight text-foreground md:text-7xl">
            RealityCheck AI
          </h1>
          <p className="mt-6 max-w-2xl text-lg leading-8 text-muted-foreground">
            Detect when your code, docs, APIs, configs, and deployment reality
            no longer match.
          </p>
        </div>

        <div className="mt-12 grid gap-4 md:grid-cols-3" id="signals">
          {signals.map((signal) => (
            <RealitySignal key={signal.label} {...signal} />
          ))}
        </div>

        <div className="mt-6 grid gap-6 lg:grid-cols-[1.2fr_0.8fr]">
          <section className="rc-panel p-5">
            <div className="flex items-center justify-between border-b border-border pb-4">
              <div className="flex items-center gap-3">
                <GitBranch className="h-5 w-5 text-accent" aria-hidden="true" />
                <div>
                  <p className="text-sm font-medium">repository audit</p>
                  <p className="text-sm text-muted-foreground">
                    feature-1/project-skeleton
                  </p>
                </div>
              </div>
              <ShieldCheck className="h-5 w-5 text-accent" aria-hidden="true" />
            </div>

            <div className="divide-y divide-border pt-1">
              <div className="py-4">
                <div className="flex flex-wrap items-center justify-between gap-3">
                  <span className="text-sm text-muted-foreground">
                    README says API is healthy
                  </span>
                  <span className="rounded-full border border-accent/40 px-3 py-1 text-xs text-accent">
                    verified by /health
                  </span>
                </div>
              </div>
              <div className="py-4">
                <div className="flex flex-wrap items-center justify-between gap-3">
                  <span className="text-sm text-muted-foreground">
                    Frontend knows where backend lives
                  </span>
                  <span className="rounded-full border border-warning/40 px-3 py-1 text-xs text-warning">
                    via VITE_API_BASE_URL
                  </span>
                </div>
              </div>
              <div className="py-4">
                <div className="flex flex-wrap items-center justify-between gap-3">
                  <span className="text-sm text-muted-foreground">
                    Scanner and agent folders are ready
                  </span>
                  <span className="rounded-full border border-border px-3 py-1 text-xs text-muted-foreground">
                    next features
                  </span>
                </div>
              </div>
            </div>
          </section>

          <section className="rc-panel p-5" id="stack">
            <p className="text-sm font-medium">Core analysis surfaces</p>
            <div className="mt-5 divide-y divide-border">
              {stackItems.map((item) => (
                <div
                  className="flex items-center justify-between py-3"
                  key={item.label}
                >
                  <div className="flex items-center gap-3">
                    <item.icon className="h-4 w-4 text-accent" aria-hidden="true" />
                    <span className="text-sm text-muted-foreground">
                      {item.label}
                    </span>
                  </div>
                  <ArrowRight
                    className="h-4 w-4 text-muted-foreground"
                    aria-hidden="true"
                  />
                </div>
              ))}
            </div>
          </section>
        </div>
      </section>
    </>
  );
}
