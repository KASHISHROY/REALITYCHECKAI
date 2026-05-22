# RealityCheck AI

Detect when your code, docs, APIs, configs, and deployment reality no longer match.

RealityCheck AI is an agentic repository intelligence platform for full-stack teams. It analyzes GitHub repositories and compares documentation claims against actual frontend calls, backend routes, environment variables, dependencies, authentication signals, and deployment configuration.

## Architecture

```text
React + TypeScript + Vite + Tailwind
        |
        v
FastAPI API
        |
        v
Deterministic scanners -> Gap detection -> Optional GenAI reasoning
        |
        v
SQLite now, PostgreSQL-ready later
```

The core architecture is deterministic extraction plus GenAI reasoning. Route extraction, API calls, environment variables, dependencies, auth signals, and deployment config are parsed locally. If `GROQ_API_KEY` or `OPENAI_API_KEY` exists, RealityCheck AI uses an LLM for documentation claim extraction and gap explanations. Without keys, deterministic fallback templates keep the app fully usable.

## Features

- GitHub project creation and repository cloning
- File-tree and important-file scanning
- README/docs claim extraction
- FastAPI and Express route extraction
- Frontend `fetch`, `axios`, and API client call extraction
- API mismatch detection
- Environment variable usage vs `.env.example`
- Docker, Compose, Render, Vercel, Vite, and package script signal extraction
- Dependency reality detection for PostgreSQL, MongoDB, Redis, RabbitMQ, JWT, sessions, FastAPI, and Express
- Auth mechanism detection for JWT, sessions, cookies, and bearer tokens
- Gap storage with severity, explanation, and suggested fix
- Reality Score with high, medium, and low penalties
- Dashboard with filters, detail view, architecture graph, and markdown export
- Built-in intentionally broken demo repository

## Screenshots

```text
screenshots/dashboard-placeholder.png
screenshots/gap-detail-placeholder.png
screenshots/report-export-placeholder.png
```

## Project Structure

```text
backend/
  app/
    agents/
    models/
    routes/
    scanners/
    schemas/
    services/
frontend/
  src/
    api/
    components/
    hooks/
    layouts/
    pages/
realitycheck-demo-app/
```

## Backend Setup

```bash
cd backend
python -m venv .venv
```

Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

macOS or Linux:

```bash
source .venv/bin/activate
```

Install and run:

```bash
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Health check:

```bash
curl http://localhost:8000/health
```

## Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

Open:

```text
http://localhost:5173
```

The frontend uses `http://localhost:8000` by default. To override it, copy `frontend/.env.example` to `frontend/.env` and set `VITE_API_BASE_URL`.

## API Routes

- `GET /health`
- `POST /projects`
- `POST /projects/{project_id}/scan`
- `POST /projects/demo/scan`
- `GET /projects/{project_id}/scans/{scan_id}/report`

Create a project:

```powershell
curl.exe -X POST http://localhost:8000/projects `
  -H "Content-Type: application/json" `
  -d "{\"repo_url\":\"https://github.com/owner/repo\"}"
```

Run a scan:

```powershell
curl.exe -X POST http://localhost:8000/projects/1/scan
```

Run the demo scan:

```powershell
curl.exe -X POST http://localhost:8000/projects/demo/scan
```

Export a report:

```powershell
curl.exe http://localhost:8000/projects/1/scans/1/report
```

## Demo Repository

`realitycheck-demo-app/` is intentionally broken. It includes a frontend, backend, README, `.env.example`, Dockerfile, and docker-compose file with 20+ mismatches:

- Docs say backend port 8000, Docker exposes 5000
- Docs say frontend port 3000, Vite uses 5173
- Docs claim JWT auth, backend uses sessions and cookies
- Docs claim MongoDB, dependencies use PostgreSQL
- Frontend calls `/api/users`, backend exposes `/api/v1/users`
- Frontend calls products/orders/reports endpoints that do not exist
- Code uses env vars missing from `.env.example`
- Docs claim RabbitMQ, dependencies do not include it

Use the dashboard button `Try Demo Repo` to scan it without cloning anything.

## Docker

Run the backend with Docker Compose:

```bash
docker compose up --build backend
```

Then visit:

```text
http://localhost:8000/health
```

## Future Improvements

- Alembic migrations
- PostgreSQL production database
- Background scan jobs with Celery and Redis
- Deeper route prefix resolution across framework files
- React Flow graph view
- Historical scan comparisons
- GitHub App installation and PR comments
- CI checks for documentation drift
