import {
  ArrowRight,
  Bot,
  Box,
  Code2,
  Database,
  Download,
  FileCode2,
  FileText,
  Filter,
  FolderTree,
  GitBranch,
  KeyRound,
  Network,
  Server,
  Settings2,
  ShieldAlert,
} from "lucide-react";
import { useMemo, useState } from "react";

import {
  exportScanReport,
  type Gap,
  type ScanSummary,
} from "@/api/client";
import { DetectionCard } from "@/components/DetectionCard";
import { RealitySignal } from "@/components/RealitySignal";

type ScanDashboardProps = {
  scan: ScanSummary;
};

const categoryFilters = [
  "All",
  "API",
  "Docs",
  "Env",
  "Auth",
  "Deployment",
  "Dependencies",
];
const severityFilters = ["All", "High", "Medium", "Low"];

export function ScanDashboard({ scan }: ScanDashboardProps) {
  const [categoryFilter, setCategoryFilter] = useState("All");
  const [severityFilter, setSeverityFilter] = useState("All");
  const [selectedGapId, setSelectedGapId] = useState<number | null>(
    scan.gaps[0]?.id ?? null,
  );
  const [exportError, setExportError] = useState<string | null>(null);
  const [isExporting, setIsExporting] = useState(false);

  const filteredGaps = useMemo(
    () =>
      scan.gaps.filter((gap) => {
        const categoryMatches =
          categoryFilter === "All" || gap.category === categoryFilter;
        const severityMatches =
          severityFilter === "All" || gap.severity === severityFilter;
        return categoryMatches && severityMatches;
      }),
    [categoryFilter, scan.gaps, severityFilter],
  );

  const selectedGap =
    filteredGaps.find((gap) => gap.id === selectedGapId) ??
    filteredGaps[0] ??
    scan.gaps[0] ??
    null;

  const detections = [
    {
      detected: scan.frontend_detected,
      icon: Code2,
      label: "Frontend",
      note: `${scan.analysis.frontend_calls?.length ?? 0} API calls detected`,
    },
    {
      detected: scan.backend_detected,
      icon: FileCode2,
      label: "Backend",
      note: `${scan.analysis.backend_routes?.length ?? 0} routes detected`,
    },
    {
      detected: scan.docs_detected,
      icon: FileText,
      label: "Docs",
      note: `${scan.analysis.doc_claims?.length ?? 0} claims extracted`,
    },
    {
      detected: scan.config_detected,
      icon: Settings2,
      label: "Config",
      note: `${scan.analysis.environment?.missing?.length ?? 0} env gaps`,
    },
  ];

  async function handleExport() {
    try {
      setExportError(null);
      setIsExporting(true);
      const markdown = await exportScanReport(scan.project_id, scan.scan_id);
      const blob = new Blob([markdown], { type: "text/markdown" });
      const url = URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = url;
      link.download = `${scan.repo_name}-realitycheck-report.md`;
      link.click();
      URL.revokeObjectURL(url);
    } catch (caughtError) {
      setExportError(
        caughtError instanceof Error
          ? caughtError.message
          : "Could not export the report.",
      );
    } finally {
      setIsExporting(false);
    }
  }

  return (
    <section className="space-y-6">
      <div className="flex flex-col justify-between gap-4 border-y border-border py-6 md:flex-row md:items-center">
        <div>
          <div className="flex items-center gap-2 text-sm text-muted-foreground">
            <GitBranch className="h-4 w-4 text-accent" aria-hidden={true} />
            <span>
              {scan.repo_owner}/{scan.repo_name}
            </span>
          </div>
          <h2 className="mt-2 text-2xl font-semibold">Reality scan</h2>
        </div>
        <button
          className="inline-flex h-10 w-fit items-center justify-center gap-2 rounded-lg border border-accent/40 bg-accent/10 px-4 text-sm font-semibold text-accent transition hover:border-accent disabled:cursor-not-allowed disabled:opacity-60"
          disabled={isExporting}
          onClick={handleExport}
          type="button"
        >
          <Download className="h-4 w-4" aria-hidden={true} />
          {isExporting ? "Exporting" : "Export Report"}
        </button>
      </div>

      {exportError ? (
        <p className="rounded-lg border border-danger/30 bg-danger/10 px-4 py-3 text-sm text-danger">
          {exportError}
        </p>
      ) : null}

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-5">
        <RealitySignal
          label="Reality Score"
          value={`${scan.reality_score}/100`}
          tone={scoreTone(scan.reality_score)}
        />
        <RealitySignal label="Total Gaps" value={`${scan.total_gaps}`} tone="warning" />
        <RealitySignal label="High" value={`${scan.high_gaps}`} tone="danger" />
        <RealitySignal label="Medium" value={`${scan.medium_gaps}`} tone="warning" />
        <RealitySignal label="Low" value={`${scan.low_gaps}`} tone="accent" />
      </div>

      <div className="grid gap-4 md:grid-cols-4">
        {detections.map((item) => (
          <DetectionCard key={item.label} {...item} />
        ))}
      </div>

      <ArchitectureGraph scan={scan} />

      <div className="grid gap-6 lg:grid-cols-[0.95fr_1.05fr]">
        <div className="space-y-4">
          <div className="flex flex-col gap-3 rounded-lg border border-border bg-surface-strong/60 p-4">
            <div className="flex items-center gap-2 text-sm font-medium">
              <Filter className="h-4 w-4 text-accent" aria-hidden={true} />
              Filters
            </div>
            <div className="flex flex-wrap gap-2">
              {categoryFilters.map((category) => (
                <FilterButton
                  active={categoryFilter === category}
                  key={category}
                  label={
                    category === "All"
                      ? `All (${scan.total_gaps})`
                      : `${category} (${scan.category_counts[category] ?? 0})`
                  }
                  onClick={() => setCategoryFilter(category)}
                />
              ))}
            </div>
            <div className="flex flex-wrap gap-2">
              {severityFilters.map((severity) => (
                <FilterButton
                  active={severityFilter === severity}
                  key={severity}
                  label={
                    severity === "All"
                      ? "All severities"
                      : `${severity} (${severityCount(scan, severity)})`
                  }
                  onClick={() => setSeverityFilter(severity)}
                />
              ))}
            </div>
          </div>

          <div className="max-h-[560px] overflow-auto rounded-lg border border-border bg-background/40">
            {filteredGaps.length > 0 ? (
              <ul className="divide-y divide-border">
                {filteredGaps.map((gap) => (
                  <li key={gap.id}>
                    <button
                      className={`w-full px-4 py-4 text-left transition hover:bg-surface ${
                        selectedGap?.id === gap.id ? "bg-surface" : ""
                      }`}
                      onClick={() => setSelectedGapId(gap.id)}
                      type="button"
                    >
                      <div className="flex items-start justify-between gap-3">
                        <div className="min-w-0">
                          <div className="flex flex-wrap items-center gap-2">
                            <SeverityPill severity={gap.severity} />
                            <span className="rounded-full border border-border px-2 py-0.5 text-xs text-muted-foreground">
                              {gap.category}
                            </span>
                          </div>
                          <p className="mt-3 line-clamp-2 text-sm font-medium leading-6">
                            {gap.claim_text}
                          </p>
                          <p className="mt-1 line-clamp-2 text-sm leading-6 text-muted-foreground">
                            {gap.reality_text}
                          </p>
                        </div>
                        <ArrowRight
                          className="mt-1 h-4 w-4 shrink-0 text-muted-foreground"
                          aria-hidden={true}
                        />
                      </div>
                    </button>
                  </li>
                ))}
              </ul>
            ) : (
              <p className="px-4 py-6 text-sm text-muted-foreground">
                No gaps match the selected filters.
              </p>
            )}
          </div>
        </div>

        <GapDetail gap={selectedGap} />
      </div>

      <ExtractionOverview scan={scan} />
    </section>
  );
}

function ArchitectureGraph({ scan }: ScanDashboardProps) {
  const technologies = scan.analysis.technologies ?? {};
  const deployment = scan.analysis.deployment ?? {};
  const auth = scan.analysis.auth?.mechanisms ?? [];
  const databaseLabel = technologies.postgresql
    ? "PostgreSQL"
    : technologies.mongodb
      ? "MongoDB"
      : technologies.mysql
        ? "MySQL"
        : technologies.sqlite
          ? "SQLite"
          : "Database";

  return (
    <div className="rounded-lg border border-border bg-surface-strong/60 p-5">
      <div className="flex items-center gap-3">
        <Network className="h-4 w-4 text-accent" aria-hidden={true} />
        <p className="text-sm font-medium">Architecture reality graph</p>
      </div>
      <div className="mt-5 grid gap-3 lg:grid-cols-[1fr_auto_1fr_auto_1fr] lg:items-center">
        <GraphNode
          detail={`${scan.analysis.frontend_calls?.length ?? 0} calls`}
          detected={scan.frontend_detected}
          icon={Code2}
          label="Frontend"
        />
        <GraphArrow />
        <GraphNode
          detail={`${scan.analysis.backend_routes?.length ?? 0} routes`}
          detected={scan.backend_detected}
          icon={Server}
          label="Backend"
        />
        <GraphArrow />
        <GraphNode
          detail={databaseLabel}
          detected={
            Boolean(technologies.postgresql) ||
            Boolean(technologies.mongodb) ||
            Boolean(technologies.mysql) ||
            Boolean(technologies.sqlite)
          }
          icon={Database}
          label="Data layer"
        />
      </div>
      <div className="mt-4 grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
        <MiniSignal
          label="Redis"
          value={technologies.redis ? "detected" : "not detected"}
          active={Boolean(technologies.redis)}
        />
        <MiniSignal
          label="Auth"
          value={auth.length > 0 ? auth.join(", ") : "not detected"}
          active={auth.length > 0}
        />
        <MiniSignal
          label="Docker"
          value={scan.docker_detected ? "Dockerfile" : "missing"}
          active={scan.docker_detected}
        />
        <MiniSignal
          label="Deploy"
          value={
            deployment.render_files?.length
              ? "Render"
              : deployment.vercel_files?.length
                ? "Vercel"
                : scan.docker_compose_detected
                  ? "Compose"
                  : "not detected"
          }
          active={
            Boolean(deployment.render_files?.length) ||
            Boolean(deployment.vercel_files?.length) ||
            scan.docker_compose_detected
          }
        />
      </div>
    </div>
  );
}

type GraphNodeProps = {
  detected: boolean;
  icon: typeof Code2;
  label: string;
  detail: string;
};

function GraphNode({ detected, icon: Icon, label, detail }: GraphNodeProps) {
  return (
    <div className="rounded-lg border border-border bg-background/50 p-4">
      <div className="flex items-center gap-3">
        <span className="grid h-9 w-9 place-items-center rounded-lg border border-border bg-surface">
          <Icon className="h-4 w-4 text-accent" aria-hidden={true} />
        </span>
        <div className="min-w-0">
          <p className="text-sm font-medium">{label}</p>
          <p className="truncate text-sm text-muted-foreground">{detail}</p>
        </div>
      </div>
      <div
        className={`mt-4 h-1 rounded-full ${
          detected ? "bg-accent" : "bg-muted"
        }`}
      />
    </div>
  );
}

function GraphArrow() {
  return (
    <div className="hidden justify-center text-muted-foreground lg:flex">
      <ArrowRight className="h-5 w-5" aria-hidden={true} />
    </div>
  );
}

type MiniSignalProps = {
  label: string;
  value: string;
  active: boolean;
};

function MiniSignal({ label, value, active }: MiniSignalProps) {
  return (
    <div className="rounded-lg border border-border bg-background/50 p-3">
      <p className="text-xs uppercase text-muted-foreground">{label}</p>
      <p className={`mt-1 text-sm ${active ? "text-accent" : "text-muted-foreground"}`}>
        {value}
      </p>
    </div>
  );
}

type GapDetailProps = {
  gap: Gap | null;
};

function GapDetail({ gap }: GapDetailProps) {
  if (!gap) {
    return (
      <div className="rounded-lg border border-border bg-surface-strong/60 p-5 text-sm text-muted-foreground">
        No gap selected.
      </div>
    );
  }

  return (
    <div className="rounded-lg border border-border bg-surface-strong/60 p-5">
      <div className="flex flex-wrap items-center gap-2">
        <SeverityPill severity={gap.severity} />
        <span className="rounded-full border border-border px-2 py-0.5 text-xs text-muted-foreground">
          {gap.category}
        </span>
      </div>

      <div className="mt-5 grid gap-4">
        <DetailBlock icon={FileText} label="Claim" value={gap.claim_text} />
        <DetailBlock icon={ShieldAlert} label="Reality" value={gap.reality_text} />
        <DetailBlock icon={Bot} label="Explanation" value={gap.explanation} />
        <DetailBlock icon={KeyRound} label="Suggested fix" value={gap.suggested_fix} />
      </div>

      <div className="mt-5 grid gap-3 sm:grid-cols-2">
        <FileMeta label="Source file" value={gap.source_file} />
        <FileMeta label="Affected file" value={gap.affected_file} />
      </div>
    </div>
  );
}

type DetailBlockProps = {
  icon: typeof FileText;
  label: string;
  value: string;
};

function DetailBlock({ icon: Icon, label, value }: DetailBlockProps) {
  return (
    <div className="rounded-lg border border-border bg-background/50 p-4">
      <div className="flex items-center gap-2 text-sm font-medium">
        <Icon className="h-4 w-4 text-accent" aria-hidden={true} />
        {label}
      </div>
      <p className="mt-2 text-sm leading-6 text-muted-foreground">{value}</p>
    </div>
  );
}

type FileMetaProps = {
  label: string;
  value: string | null;
};

function FileMeta({ label, value }: FileMetaProps) {
  return (
    <div className="rounded-lg border border-border bg-background/50 p-3">
      <p className="text-xs uppercase text-muted-foreground">{label}</p>
      <p className="mt-1 break-words text-sm">{value ?? "Unknown"}</p>
    </div>
  );
}

function ExtractionOverview({ scan }: ScanDashboardProps) {
  return (
    <div className="grid gap-4 lg:grid-cols-[0.8fr_1.2fr]">
      <div className="rounded-lg border border-border bg-surface-strong/60 p-5">
        <div className="flex items-center gap-3">
          <Box className="h-4 w-4 text-accent" aria-hidden={true} />
          <p className="text-sm font-medium">Configuration signals</p>
        </div>
        <div className="mt-5 space-y-3 text-sm text-muted-foreground">
          <Signal label="Dockerfile" value={scan.docker_detected} />
          <Signal label="docker-compose" value={scan.docker_compose_detected} />
          <Signal label=".env example" value={scan.env_detected} />
          <Signal label="package.json" value={scan.package_json_detected} />
          <Signal label="requirements.txt" value={scan.requirements_detected} />
        </div>
      </div>

      <div className="rounded-lg border border-border bg-surface-strong/60 p-5">
        <div className="flex items-center gap-3">
          <FolderTree className="h-4 w-4 text-accent" aria-hidden={true} />
          <p className="text-sm font-medium">Important files</p>
        </div>
        <div className="mt-4 max-h-72 overflow-auto rounded-lg border border-border bg-background/60">
          {scan.important_files.length > 0 ? (
            <ul className="divide-y divide-border">
              {scan.important_files.map((file) => (
                <li className="px-4 py-3 text-sm text-muted-foreground" key={file}>
                  {file}
                </li>
              ))}
            </ul>
          ) : (
            <p className="px-4 py-3 text-sm text-muted-foreground">
              No important files found.
            </p>
          )}
        </div>
      </div>
    </div>
  );
}

type FilterButtonProps = {
  active: boolean;
  label: string;
  onClick: () => void;
};

function FilterButton({ active, label, onClick }: FilterButtonProps) {
  return (
    <button
      className={`h-9 rounded-lg border px-3 text-sm transition ${
        active
          ? "border-accent/60 bg-accent/10 text-accent"
          : "border-border bg-background/50 text-muted-foreground hover:border-accent/40 hover:text-foreground"
      }`}
      onClick={onClick}
      type="button"
    >
      {label}
    </button>
  );
}

function SeverityPill({ severity }: { severity: Gap["severity"] }) {
  const classes = {
    High: "border-danger/40 bg-danger/10 text-danger",
    Medium: "border-warning/40 bg-warning/10 text-warning",
    Low: "border-accent/40 bg-accent/10 text-accent",
  }[severity];

  return (
    <span className={`rounded-full border px-2 py-0.5 text-xs ${classes}`}>
      {severity}
    </span>
  );
}

function Signal({ label, value }: { label: string; value: boolean }) {
  return (
    <div className="flex items-center justify-between gap-3">
      <span>{label}</span>
      <span className={value ? "text-accent" : "text-muted-foreground"}>
        {value ? "detected" : "missing"}
      </span>
    </div>
  );
}

function severityCount(scan: ScanSummary, severity: string) {
  if (severity === "High") return scan.high_gaps;
  if (severity === "Medium") return scan.medium_gaps;
  if (severity === "Low") return scan.low_gaps;
  return scan.total_gaps;
}

function scoreTone(score: number): "accent" | "warning" | "danger" {
  if (score >= 80) return "accent";
  if (score >= 50) return "warning";
  return "danger";
}
