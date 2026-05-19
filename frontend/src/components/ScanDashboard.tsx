import {
  Box,
  Code2,
  FileCode2,
  FileText,
  FolderTree,
  GitBranch,
  Settings2,
} from "lucide-react";

import type { ScanSummary } from "@/api/client";
import { DetectionCard } from "@/components/DetectionCard";

type ScanDashboardProps = {
  scan: ScanSummary;
};

export function ScanDashboard({ scan }: ScanDashboardProps) {
  const detections = [
    {
      detected: scan.frontend_detected,
      icon: Code2,
      label: "Frontend",
      note: scan.package_json_detected ? "package.json found" : "No frontend signal found",
    },
    {
      detected: scan.backend_detected,
      icon: FileCode2,
      label: "Backend",
      note: scan.requirements_detected
        ? "requirements.txt found"
        : "No backend signal found",
    },
    {
      detected: scan.docs_detected,
      icon: FileText,
      label: "Docs",
      note: "README or markdown documentation",
    },
    {
      detected: scan.config_detected,
      icon: Settings2,
      label: "Config",
      note: "Env, Docker, or dependency config",
    },
  ];

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
          <h2 className="mt-2 text-2xl font-semibold">Scan summary</h2>
        </div>
        <span className="w-fit rounded-full border border-accent/40 bg-accent/10 px-3 py-1 text-sm text-accent">
          {scan.status}
        </span>
      </div>

      <div className="grid gap-4 sm:grid-cols-2">
        <div className="rc-subtle-panel p-5">
          <div className="flex items-center gap-3 text-muted-foreground">
            <FileText className="h-4 w-4 text-accent" aria-hidden={true} />
            <span className="text-sm">Total files</span>
          </div>
          <p className="mt-3 text-3xl font-semibold">{scan.total_files}</p>
        </div>
        <div className="rc-subtle-panel p-5">
          <div className="flex items-center gap-3 text-muted-foreground">
            <FolderTree className="h-4 w-4 text-accent" aria-hidden={true} />
            <span className="text-sm">Total folders</span>
          </div>
          <p className="mt-3 text-3xl font-semibold">{scan.total_folders}</p>
        </div>
      </div>

      <div className="grid gap-4 md:grid-cols-4">
        {detections.map((item) => (
          <DetectionCard key={item.label} {...item} />
        ))}
      </div>

      <div className="grid gap-4 lg:grid-cols-[0.8fr_1.2fr]">
        <div className="rc-subtle-panel p-5">
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

        <div className="rc-subtle-panel p-5">
          <p className="text-sm font-medium">Important files</p>
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
                No important files found by the Day 1 scanner.
              </p>
            )}
          </div>
        </div>
      </div>
    </section>
  );
}

type SignalProps = {
  label: string;
  value: boolean;
};

function Signal({ label, value }: SignalProps) {
  return (
    <div className="flex items-center justify-between gap-3">
      <span>{label}</span>
      <span className={value ? "text-accent" : "text-muted-foreground"}>
        {value ? "detected" : "missing"}
      </span>
    </div>
  );
}
