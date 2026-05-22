# RealityCheck AI

Detect when your code, docs, APIs, configs, and deployment reality no longer match.

RealityCheck AI is a production-minded repository intelligence platform for full-stack teams. It scans a GitHub repository and compares what the documentation claims against what the implementation actually exposes, calls, imports, configures, and deploys.

## Problem

Modern software systems drift quietly:

- README says the backend runs on `8000`, but Docker exposes `5000`.
- Frontend calls `/api/users`, but the backend exposes `/api/v1/users`.
- Docs say JWT auth, but the app uses sessions and cookies.
- Docs say MongoDB, but dependencies and config point to PostgreSQL.
- Code reads `REDIS_URL`, but `.env.example` does not include it.

These gaps waste onboarding time, break deployments, and make engineering handoffs unreliable.

## Why This Is Unique

RealityCheck AI is not a chatbot and not a generic RAG wrapper. It uses deterministic scanners for exact repository evidence, then optional GenAI reasoning for natural-language claims, explanations, severity rationale, and fix recommendations.

```text
Deterministic extraction
  + docs claim extraction
  + route/API/env/dependency/deployment scanners
  + exact mismatch detection
  + optional LLM reasoning
  = repository reality intelligence
```

The app works without API keys. If `GROQ_API_KEY` or `OPENAI_API_KEY` is configured, explanations become LLM-assisted. Otherwise, deterministic fallback explanations are used.

## Features

- GitHub project creation and repository cloning
- File tree and important-file scanner
- README/docs claim extraction
- FastAPI and Express backend route extraction
- Frontend `fetch`, `axios`, `api.get`, and `api.post` call extraction
- API route, version, and method mismatch detection
- Environment variable usage vs `.env.example`
- Dockerfile, docker-compose, Render, Vercel, Vite, and package script detection
- Dependency reality detection for PostgreSQL, MongoDB, Redis, RabbitMQ, JWT, sessions, FastAPI, and Express
- Auth mechanism detection for JWT, sessions, cookies, and bearer tokens
- Gap model with category, severity, source, affected file, explanation, and suggested fix
- Reality Score with high, medium, and low penalties
- Premium dark-mode dashboard with filters, gap details, architecture graph, and report export
- Built-in demo repo with 39 intentional gaps

## Screenshots

Screenshots can be added after recording the final demo.

### Landing Page

```text
docs/screenshots/landing-page.png
```

### Dashboard

```text
docs/screenshots/dashboard.png
```

### Gap Details

```text
docs/screenshots/gap-details.png
```

### Export Report

```text
docs/screenshots/export-report.png
```

## Architecture

```text
React + TypeScript + Vite + Tailwind
        |
        v
FastAPI API
        |
        v
Repository clone/fetch
        |
        v
Deterministic scanners
        |
        v
Gap detection + severity scoring
        |
        v
Optional GenAI explanations
        |
        v
SQLite now, PostgreSQL-ready later
```

See [docs/architecture.md](docs/architecture.md) for the full system design.

## Tech Stack

Frontend:

- React
- TypeScript
- Vite
- Tailwind CSS
- Lucide icons

Backend:

- FastAPI
- SQLAlchemy
- Pydantic
- SQLite initially
- PostgreSQL-ready structure
- GitPython

AI:

- Groq/OpenAI-compatible chat completion APIs
- Deterministic fallback explanations when no key exists

## Setup

### Backend

```bash
cd backend
python -m venv .venv
```

Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

macOS/Linux:

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

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Open:

```text
http://localhost:5173
```

## Environment Variables

Backend:

```text
DATABASE_URL=sqlite:///./realitycheck.db
FRONTEND_URL=http://localhost:5173
CORS_ORIGINS=http://localhost:5173,http://127.0.0.1:5173
LLM_PROVIDER=auto
GROQ_API_KEY=
OPENAI_API_KEY=
APP_ENV=development
```

Frontend:

```text
VITE_API_URL=http://localhost:8000
```

## API Endpoints

- `GET /health`
- `POST /projects`
- `POST /projects/{project_id}/scan`
- `POST /projects/demo/scan`
- `GET /projects/{project_id}/scans/{scan_id}/report`

See [docs/api.md](docs/api.md) for request and response examples.

## Demo Repo

`realitycheck-demo-app/` is intentionally broken and includes:

- `frontend/`
- `backend/`
- `README.md`
- `.env.example`
- `Dockerfile`
- `docker-compose.yml`

It contains 39 intentional gaps across API contracts, ports, auth, dependencies, env vars, and deployment reality. In the UI, click `Try Demo Repo` to analyze it instantly.

## Demo Video

Demo video link placeholder:

```text
https://your-demo-video-link.example
```

Suggested recording script is included in [docs/testing.md](docs/testing.md).

## Resume Bullets

See [docs/resume-bullets.md](docs/resume-bullets.md).

## Additional Docs

- [Architecture](docs/architecture.md)
- [API](docs/api.md)
- [Deployment](docs/deployment.md)
- [Testing](docs/testing.md)
- [Roadmap](docs/roadmap.md)
- [LinkedIn launch draft](docs/linkedin-post.md)

## Future Improvements

- Deeper AST parsing
- Repository memory with vector search
- LangGraph multi-agent orchestration
- GitHub App and PR comments
- Historical scan comparison
- CI/CD integration
- Slack/Jira export
- Team workspace support
