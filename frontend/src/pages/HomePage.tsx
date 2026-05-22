import { AlertCircle, Github, Loader2, Play, Search, ShieldCheck } from "lucide-react";
import type { FormEvent } from "react";
import { useState } from "react";

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
  scanning: "Cloning and scanning",
  complete: "Scan complete",
};

export function HomePage() {
  const health = useApiHealth();
  const [repoUrl, setRepoUrl] = useState("");
  const [stage, setStage] = useState<AnalyzeStage>("idle");
  const [error, setError] = useState<string | null>(null);
  const [scan, setScan] = useState<ScanSummary | null>(null);

  const isLoading = stage === "creating" || stage === "scanning";

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
      setStage("creating");
      const project = await createProject(trimmedRepoUrl);

      setStage("scanning");
      const scanSummary = await scanProject(project.id);
      setScan(scanSummary);
      setStage("complete");
    } catch (caughtError) {
      setStage("idle");
      setError(
        caughtError instanceof Error
          ? caughtError.message
          : "Something went wrong while analyzing this repository.",
      );
    }
  }

  async function handleDemoScan() {
    try {
      setError(null);
      setScan(null);
      setStage("scanning");
      const scanSummary = await scanDemoProject();
      setScan(scanSummary);
      setStage("complete");
    } catch (caughtError) {
      setStage("idle");
      setError(
        caughtError instanceof Error
          ? caughtError.message
          : "Something went wrong while analyzing the demo repository.",
      );
    }
  }

  return (
    <section className="mx-auto w-full max-w-7xl px-6 py-12 md:py-16">
      <div className="grid gap-10 lg:grid-cols-[0.8fr_1.2fr] lg:items-start">
        <div className="space-y-8">
          <HealthBadge status={health.status} />

          <div>
            <p className="text-sm font-medium uppercase text-accent">
              Software reality gap detector
            </p>
            <h1 className="mt-5 text-5xl font-semibold leading-tight text-foreground md:text-7xl">
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
            <div className="mt-6 rounded-lg border border-border bg-background/60 p-4">
              <div className="h-2 overflow-hidden rounded-full bg-muted">
                <div className="h-full w-2/3 animate-pulse rounded-full bg-accent" />
              </div>
              <p className="mt-3 text-sm text-muted-foreground">
                {stage === "creating"
                  ? "Checking the GitHub URL and creating the project record."
                  : "Extracting routes, API calls, env vars, docs claims, dependencies, and deployment signals."}
              </p>
            </div>
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
          <div className="border-y border-border py-8 text-sm text-muted-foreground">
            Paste a repository URL or run the demo repo to generate a RealityCheck analysis.
          </div>
        )}
      </div>
    </section>
  );
}
