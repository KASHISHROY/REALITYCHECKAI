export type HealthResponse = {
  status: string;
  service: string;
  version: string;
  environment: string;
};

export type ProjectResponse = {
  id: number;
  repo_url: string;
  repo_owner: string;
  repo_name: string;
  status: string;
  error_message: string | null;
};

export type Gap = {
  id: number;
  category: string;
  severity: "High" | "Medium" | "Low";
  claim_text: string;
  reality_text: string;
  source_file: string | null;
  affected_file: string | null;
  explanation: string;
  suggested_fix: string;
};

export type AnalysisPayload = {
  doc_claims?: Array<Record<string, string>>;
  backend_routes?: Array<Record<string, string>>;
  frontend_calls?: Array<Record<string, string>>;
  environment?: {
    used?: string[];
    example_vars?: string[];
    missing?: string[];
    example_files?: string[];
  };
  deployment?: {
    dockerfiles?: string[];
    compose_files?: string[];
    render_files?: string[];
    vercel_files?: string[];
    backend_ports?: string[];
    frontend_ports?: string[];
    compose_ports?: string[];
  };
  technologies?: Record<string, boolean>;
  auth?: {
    mechanisms?: string[];
  };
};

export type ScanSummary = {
  scan_id: number;
  project_id: number;
  repo_owner: string;
  repo_name: string;
  status: string;
  total_files: number;
  total_folders: number;
  frontend_detected: boolean;
  backend_detected: boolean;
  docs_detected: boolean;
  docker_detected: boolean;
  docker_compose_detected: boolean;
  env_detected: boolean;
  package_json_detected: boolean;
  requirements_detected: boolean;
  config_detected: boolean;
  important_files: string[];
  reality_score: number;
  total_gaps: number;
  high_gaps: number;
  medium_gaps: number;
  low_gaps: number;
  category_counts: Record<string, number>;
  gaps: Gap[];
  analysis: AnalysisPayload;
};

const API_BASE_URL = (
  import.meta.env.VITE_API_URL ||
  import.meta.env.VITE_API_BASE_URL ||
  "http://localhost:8000"
).replace(/\/$/, "");

export async function apiRequest<T>(
  path: string,
  options: RequestInit = {},
  timeoutMs = 45_000,
): Promise<T> {
  const headers = new Headers(options.headers);
  if (!headers.has("Content-Type")) {
    headers.set("Content-Type", "application/json");
  }

  const controller = new AbortController();
  const timeout = window.setTimeout(() => controller.abort(), timeoutMs);
  let response: Response;

  try {
    response = await fetch(`${API_BASE_URL}${path}`, {
      ...options,
      headers,
      signal: controller.signal,
    });
  } catch (error) {
    if (error instanceof DOMException && error.name === "AbortError") {
      throw new Error("Request timed out. The repository scan may be taking too long.");
    }
    throw new Error("RealityCheck API is unavailable. Start the backend server and try again.");
  } finally {
    window.clearTimeout(timeout);
  }

  if (!response.ok) {
    throw new Error(await getApiErrorMessage(response));
  }

  return response.json() as Promise<T>;
}

export function getHealth() {
  return apiRequest<HealthResponse>("/health", {}, 5_000);
}

export function createProject(repoUrl: string) {
  return apiRequest<ProjectResponse>("/projects", {
    method: "POST",
    body: JSON.stringify({ repo_url: repoUrl }),
  }, 20_000);
}

export function scanProject(projectId: number) {
  return apiRequest<ScanSummary>(`/projects/${projectId}/scan`, {
    method: "POST",
  }, 180_000);
}

export function scanDemoProject() {
  return apiRequest<ScanSummary>("/projects/demo/scan", {
    method: "POST",
  }, 120_000);
}

export async function exportScanReport(projectId: number, scanId: number) {
  const controller = new AbortController();
  const timeout = window.setTimeout(() => controller.abort(), 30_000);
  let response: Response;

  try {
    response = await fetch(
      `${API_BASE_URL}/projects/${projectId}/scans/${scanId}/report`,
      { signal: controller.signal },
    );
  } catch {
    throw new Error("Could not reach the API to export the report.");
  } finally {
    window.clearTimeout(timeout);
  }

  if (!response.ok) {
    throw new Error(await getApiErrorMessage(response));
  }

  return response.text();
}

async function getApiErrorMessage(response: Response) {
  try {
    const body = (await response.json()) as { detail?: string };
    if (body.detail) {
      return body.detail;
    }
  } catch {
    // Fall back to the generic status message below.
  }

  return `API request failed with status ${response.status}`;
}
