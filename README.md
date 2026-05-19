# RealityCheck AI

Detect when your code, docs, APIs, configs, and deployment reality no longer match.

RealityCheck AI is an agentic software reality gap detector. It will analyze repositories and compare what documentation claims against what the code, APIs, environment variables, dependencies, and deployment files actually do.

## Current Feature

Feature 1 creates the production-ready full-stack skeleton:

- FastAPI backend with `GET /health`
- React, TypeScript, Vite, and Tailwind frontend
- Dark-mode SaaS landing page
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

Next feature: add GitHub repository URL input and a project creation API.

