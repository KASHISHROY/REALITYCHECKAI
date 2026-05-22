# Testing Checklist

## Backend Compile Check

From the repository root:

```bash
python -c "import pathlib; files=list(pathlib.Path('backend/app').rglob('*.py')); [compile(p.read_text(encoding='utf-8'), str(p), 'exec') for p in files]; print(f'compiled {len(files)} files')"
```

## Backend Startup

```bash
cd backend
uvicorn app.main:app --reload
```

## Health Endpoint

```bash
curl http://localhost:8000/health
```

Expected:

```json
{
  "status": "ok"
}
```

## Frontend Install and Build

```bash
cd frontend
npm install
npm run build
```

## Frontend Dev Server

```bash
cd frontend
npm run dev
```

Open:

```text
http://localhost:5173
```

## Demo Repo Scan Test

```bash
curl -X POST http://localhost:8000/projects/demo/scan
```

Expected:

```text
repo_name = realitycheck-demo-app
total_gaps = 39
reality_score = 0
```

## GitHub Repo Scan Test

```bash
curl -X POST http://localhost:8000/projects \
  -H "Content-Type: application/json" \
  -d '{"repo_url":"https://github.com/octocat/Hello-World"}'
```

Then scan the returned project ID:

```bash
curl -X POST http://localhost:8000/projects/1/scan
```

## Export Report Test

```bash
curl http://localhost:8000/projects/1/scans/1/report
```

Expected:

```text
# RealityCheck AI Report
```

## UI Checklist

- API offline state is readable.
- Invalid GitHub URL shows a clean error.
- Scan progress steps animate while request is running.
- Try Demo Repo runs successfully.
- Reality Score appears at the top of the dashboard.
- Category filters work.
- Severity filters work.
- Gap detail panel updates when selecting a gap.
- No-gaps state shows a clean success message.
- Export Report downloads markdown.

## Demo Video Recording Steps

1. Start backend with `uvicorn app.main:app --reload`.
2. Start frontend with `npm run dev`.
3. Open `http://localhost:5173`.
4. Show the landing screen and explain the problem.
5. Click `Try Demo Repo`.
6. Narrate the scan progress steps.
7. Show Reality Score and severity counts.
8. Filter to API gaps and open one gap detail.
9. Show auth/dependency/deployment examples.
10. Show architecture graph.
11. Click `Export Report`.
12. Close with deterministic scanners plus optional GenAI reasoning.
