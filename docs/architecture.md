# RealityCheck AI Architecture

## System Overview

RealityCheck AI is a repository intelligence system that detects drift between documentation claims and implementation reality.

```text
User submits repo URL
        |
        v
FastAPI creates project
        |
        v
GitPython clones/fetches repository
        |
        v
File tree scanner + specialized deterministic scanners
        |
        v
Gap detector compares claims vs reality
        |
        v
Optional GenAI explanation/fix recommendation
        |
        v
SQLite persistence + React dashboard + Markdown export
```

## Backend Flow

1. `POST /projects` validates a GitHub URL and creates or returns a project record.
2. `POST /projects/{id}/scan` clones or fetches the repository.
3. `scan_repository_tree` records basic repository signals.
4. `analyze_repository` runs specialized scanners:
   - documentation claims
   - backend routes
   - frontend API calls
   - environment variables
   - deployment config
   - dependency reality
   - auth mechanisms
5. Gap detection compares extracted claims and implementation signals.
6. Severity is assigned and the Reality Score is calculated.
7. Gaps are stored in SQLite through SQLAlchemy.
8. The frontend receives a scan summary with gaps, counts, score, and analysis metadata.

## Frontend Flow

1. User enters a GitHub URL or clicks `Try Demo Repo`.
2. The UI shows simulated scan progress:
   - Creating project
   - Cloning repository
   - Scanning files
   - Extracting claims
   - Detecting gaps
   - Calculating Reality Score
3. The dashboard renders:
   - Reality Score
   - total/high/medium/low gaps
   - detected repo surfaces
   - architecture reality graph
   - filters
   - gap detail panel
   - markdown export action

## Scanner Pipeline

The scanner pipeline is intentionally deterministic for exact evidence:

- FastAPI decorators are parsed for backend routes.
- Express route calls are parsed from JS/TS files.
- Frontend API calls are extracted from `fetch`, `axios`, and client helpers.
- Env usage is extracted from `process.env`, `import.meta.env`, `os.getenv`, and `os.environ`.
- Deployment ports and commands are extracted from Dockerfile, Compose, Render, Vercel, Vite, and package scripts.
- Dependency signals are extracted from `package.json`, `requirements.txt`, and `pyproject.toml`.
- Auth signals are extracted from dependency names and code tokens such as JWT, sessions, cookies, and bearer auth.

Large text files above 1 MB are skipped to keep scans predictable and safe.

## GenAI Explanation Flow

RealityCheck AI can run without GenAI keys. When `GROQ_API_KEY` or `OPENAI_API_KEY` is configured:

1. Documentation excerpts are sent to the LLM for natural-language claim extraction.
2. Detected gaps are sent to the LLM for concise explanations and suggested fixes.
3. If the LLM call fails, deterministic fallback templates are used.

This keeps the core system reliable while still using GenAI where it adds judgment and clarity.

## Deterministic Extraction + GenAI Reasoning

RealityCheck AI avoids LLM-only scanning. Exact repository facts come from deterministic scanners. GenAI is used for:

- natural-language documentation claims
- engineering explanations
- impact descriptions
- recommended fixes

This hybrid design gives the product both precision and useful human-readable reasoning.

## Demo Repo Testing Strategy

`realitycheck-demo-app/` is a stable local fixture with intentional mismatches. It allows demos and regression checks without depending on GitHub network access.

Expected demo behavior:

- Reality Score: `0/100`
- Total gaps: `39`
- Categories: API, Env, Deployment, Dependencies, Auth

Use:

```bash
curl -X POST http://localhost:8000/projects/demo/scan
```
