# RealityCheck AI

Detect when your code, docs, APIs, configs, and deployment reality no longer match.

RealityCheck AI is an agentic software reality gap detector. It will analyze repositories and compare what documentation claims against what the code, APIs, environment variables, dependencies, and deployment files actually do.

## Current Feature

Day 1 creates the full foundation pipeline:

- FastAPI backend with `GET /health`
- `POST /projects` for GitHub repo validation and project creation
- `POST /projects/{id}/scan` for clone/fetch plus file-tree scanning
- React, TypeScript, Vite, and Tailwind frontend
- Dark-mode SaaS dashboard
- Shared project structure for future scanners and agents
- Docker-ready backend setup

## Project Structure

```text
backend/
  app/
    main.py
    config.py
    database.py
    routes/
    schemas/
    models/
    services/
    scanners/
    agents/
    workers/
    utils/
  storage/
frontend/
  src/
    api/
    components/
    pages/
    layouts/
    hooks/
    utils/
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

Install dependencies and run the API:

```bash
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Test the health endpoint:

```bash
curl http://localhost:8000/health
```

Expected response:

```json
{
  "status": "ok",
  "service": "RealityCheck AI",
  "version": "0.1.0",
  "environment": "development"
}
```

Create a project from a public GitHub repository:

```powershell
curl.exe -X POST http://localhost:8000/projects `
  -H "Content-Type: application/json" `
  -d "{\"repo_url\":\"https://github.com/octocat/Hello-World\"}"
```

Run a scan for project `1`:

```powershell
curl.exe -X POST http://localhost:8000/projects/1/scan
```

Expected scan fields include:

```json
{
  "project_id": 1,
  "repo_name": "Hello-World",
  "status": "scanned",
  "total_files": 1,
  "total_folders": 0,
  "docs_detected": true,
  "important_files": ["README"]
}
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

The frontend expects the backend at `http://localhost:8000` by default. To override it, copy `frontend/.env.example` to `frontend/.env` and update `VITE_API_BASE_URL`.

Paste a public GitHub repository URL, click Analyze, and the dashboard will show repository counts, detected project areas, configuration signals, and important files.

## Docker

Run the backend with Docker Compose:

```bash
docker compose up --build backend
```

Then visit:

```text
http://localhost:8000/health
```

## Roadmap

Next feature: extract documentation claims from README/docs.
