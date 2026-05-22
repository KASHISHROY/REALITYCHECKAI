import {
  AlertCircle,
  CheckCircle2,
  Github,
  Loader2,
  Play,
  Search,
  ShieldCheck,
} from "lucide-react";
import type { FormEvent } from "react";
import { useEffect, useState } from "react";

import {
  createProject,
  scanDemoProject,
  scanProject,
  type ScanSummary,
} from "@/api/client";
import { HealthBadge } from "@/components/HealthBadge";
import { ScanDashboard } from "@/components/ScanDashboard";
import { useApiHealth } from "@/hooks/useApiHealth";

type AnalyzeStage = "idle" | "creating" | "scanning" | "complete";

const stageLabel: Record<AnalyzeStage, string> = {
  idle: "Ready to analyze",
  creating: "Validating repository",
  scanning: "Analyzing repository reality",
  complete: "Scan complete",
};

const scanProgressSteps = [
  "Creating project",
  "Cloning repository",
  "Scanning files",
  "Extracting claims",
  "Detecting gaps",
  "Calculating Reality Score",
];

const minimumVisibleScanMs = 9000;

export function HomePage() {
  const health = useApiHealth();
  const [repoUrl, setRepoUrl] = useState("");
  const [stage, setStage] = useState<AnalyzeStage>("idle");
  const [error, setError] = useState<string | null>(null);
  const [scan, setScan] = useState<ScanSummary | null>(null);
  const [activeProgressIndex, setActiveProgressIndex] = useState(0);

  const isLoading = stage === "creating" || stage === "scanning";

  useEffect(() => {
    if (!isLoading) {
      setActiveProgressIndex(0);
      return;
    }

    const timer = window.setInterval(() => {
      setActiveProgressIndex((current) =>
        Math.min(current + 1, scanProgressSteps.length - 1),
      );
    }, 1400);

    return () => window.clearInterval(timer);
  }, [isLoading]);

  async function handleAnalyze(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();

    const trimmedRepoUrl = repoUrl.trim();
    if (!trimmedRepoUrl) {
      setError("Paste a public GitHub repository URL first.");
      return;
    }

    try {
      setError(null);
      setScan(null);
      setActiveProgressIndex(0);
      setStage("creating");
      const project = await createProject(trimmedRepoUrl);

      setStage("scanning");
      const scanSummary = await keepProgressVisible(scanProject(project.id));
      setScan(scanSummary);
      setStage("complete");
    } catch (caughtError) {
      setStage("idle");
      setError(formatUserError(caughtError, "repository"));
    }
  }

  async function handleDemoScan() {
    try {
      setError(null);
      setScan(null);
      setActiveProgressIndex(0);
      setStage("scanning");
      const scanSummary = await keepProgressVisible(scanDemoProject());
      setScan(scanSummary);
      setStage("complete");
    } catch (caughtError) {
      setStage("idle");
      setError(formatUserError(caughtError, "demo repository"));
    }
  }

  return (
    <section className="mx-auto w-full max-w-7xl px-5 py-10 sm:px-6 md:py-16">
      <div className="grid gap-10 lg:grid-cols-[0.8fr_1.2fr] lg:items-start">
        <div className="space-y-8">
          <HealthBadge status={health.status} />

          <div>
            <p className="text-sm font-medium uppercase text-accent">
              Software reality gap detector
            </p>
            <h1 className="mt-5 max-w-2xl text-5xl font-semibold leading-tight text-foreground md:text-7xl">
              RealityCheck AI
            </h1>
            <p className="mt-6 max-w-xl text-lg leading-8 text-muted-foreground">
              Detect when your code, docs, APIs, configs, and deployment reality
              no longer match.
            </p>
          </div>

          <div className="flex items-center gap-3 border-l border-accent/40 pl-4 text-sm text-muted-foreground">
            <ShieldCheck className="h-4 w-4 text-accent" aria-hidden={true} />
            <span>Deterministic scanners plus optional AI explanations.</span>
          </div>
        </div>

        <div className="rc-panel p-5 md:p-6">
          <div className="flex items-center gap-3">
            <span className="grid h-10 w-10 place-items-center rounded-lg border border-border bg-background/70">
              <Github className="h-5 w-5 text-accent" aria-hidden={true} />
            </span>
            <div>
              <p className="text-sm font-medium">Analyze a public repository</p>
              <p className="text-sm text-muted-foreground">{stageLabel[stage]}</p>
            </div>
          </div>

          {health.status === "offline" ? (
            <div className="mt-5 rounded-lg border border-warning/30 bg-warning/10 px-4 py-3 text-sm leading-6 text-warning">
              Backend API is unavailable. Start the FastAPI server, then run a scan.
            </div>
          ) : null}

          <form className="mt-6 space-y-4" onSubmit={handleAnalyze}>
            <label className="block text-sm text-muted-foreground" htmlFor="repo-url">
              GitHub repository URL
            </label>
            <div className="flex flex-col gap-3 sm:flex-row">
              <input
                className="h-12 min-w-0 flex-1 rounded-lg border border-border bg-background/70 px-4 text-sm text-foreground outline-none transition placeholder:text-muted-foreground focus:border-accent"
                disabled={isLoading}
                id="repo-url"
                onChange={(event) => setRepoUrl(event.target.value)}
                placeholder="https://github.com/owner/repo"
                type="url"
                value={repoUrl}
              />
              <button
                className="inline-flex h-12 items-center justify-center gap-2 rounded-lg bg-accent px-5 text-sm font-semibold text-background transition hover:brightness-110 disabled:cursor-not-allowed disabled:opacity-60"
                disabled={isLoading}
                type="submit"
              >
                {isLoading ? (
                  <Loader2 className="h-4 w-4 animate-spin" aria-hidden={true} />
                ) : (
                  <Search className="h-4 w-4" aria-hidden={true} />
                )}
                Analyze
              </button>
            </div>
          </form>

          <button
            className="mt-4 inline-flex h-11 w-full items-center justify-center gap-2 rounded-lg border border-border bg-background/60 px-4 text-sm font-semibold text-foreground transition hover:border-accent/60 disabled:cursor-not-allowed disabled:opacity-60"
            disabled={isLoading}
            onClick={handleDemoScan}
            type="button"
          >
            {isLoading ? (
              <Loader2 className="h-4 w-4 animate-spin" aria-hidden={true} />
            ) : (
              <Play className="h-4 w-4 text-accent" aria-hidden={true} />
            )}
            Try Demo Repo
          </button>

          {isLoading ? (
            <ScanProgress activeIndex={activeProgressIndex} />
          ) : null}

          {error ? (
            <div className="mt-6 flex gap-3 rounded-lg border border-danger/30 bg-danger/10 p-4 text-sm text-danger">
              <AlertCircle className="h-4 w-4 shrink-0" aria-hidden={true} />
              <p>{error}</p>
            </div>
          ) : null}
        </div>
      </div>

      <div className="mt-10">
        {scan ? (
          <ScanDashboard key={scan.scan_id} scan={scan} />
        ) : (
          <div className="rounded-lg border border-border bg-surface/70 px-5 py-8 text-sm leading-6 text-muted-foreground">
            Paste a GitHub URL or run the demo repo to generate your first RealityCheck analysis. Results will appear here with score, gaps, filters, graph, and report export.
          </div>
        )}
      </div>
    </section>
  );
}

function ScanProgress({ activeIndex }: { activeIndex: number }) {
  const progress = ((activeIndex + 1) / scanProgressSteps.length) * 100;

  return (
    <div className="mt-6 rounded-lg border border-border bg-background/60 p-4">
      <div className="flex items-center justify-between gap-3">
        <p className="text-sm font-medium">Scan pipeline</p>
        <span className="text-xs text-muted-foreground">{Math.round(progress)}%</span>
      </div>
      <div className="mt-3 h-2 overflow-hidden rounded-full bg-muted">
        <div
          className="h-full rounded-full bg-accent transition-all duration-500"
          style={{ width: `${progress}%` }}
        />
      </div>
      <ol className="mt-4 grid gap-2 sm:grid-cols-2">
        {scanProgressSteps.map((step, index) => {
          const isDone = index < activeIndex;
          const isActive = index === activeIndex;
          return (
            <li
              className={`flex items-center gap-2 rounded-lg border px-3 py-2 text-sm ${
                isActive
                  ? "border-accent/50 bg-accent/10 text-accent"
                  : isDone
                    ? "border-border bg-surface text-foreground"
                    : "border-border bg-background/40 text-muted-foreground"
              }`}
              key={step}
            >
              {isDone ? (
                <CheckCircle2 className="h-4 w-4 text-accent" aria-hidden={true} />
              ) : isActive ? (
                <Loader2 className="h-4 w-4 animate-spin" aria-hidden={true} />
              ) : (
                <span className="h-4 w-4 rounded-full border border-border" />
              )}
              <span>{step}</span>
            </li>
          );
        })}
      </ol>
    </div>
  );
}

function formatUserError(caughtError: unknown, target: string) {
  if (!(caughtError instanceof Error)) {
    return `Something went wrong while analyzing this ${target}.`;
  }

  if (caughtError.message.includes("Failed to fetch")) {
    return "RealityCheck API is not reachable. Start the backend server and try again.";
  }

  return caughtError.message;
}

async function keepProgressVisible<T>(work: Promise<T>): Promise<T> {
  const [result] = await Promise.all([
    work,
    new Promise((resolve) => window.setTimeout(resolve, minimumVisibleScanMs)),
  ]);
  return result;
}
