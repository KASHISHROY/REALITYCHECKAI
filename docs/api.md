# RealityCheck AI API

Base URL for local development:

```text
http://localhost:8000
```

## GET /health

Returns API status.

```bash
curl http://localhost:8000/health
```

Example response:

```json
{
  "status": "ok",
  "service": "RealityCheck AI",
  "version": "0.1.0",
  "environment": "development"
}
```

## POST /projects

Creates or returns a project for a public GitHub repository.

```bash
curl -X POST http://localhost:8000/projects \
  -H "Content-Type: application/json" \
  -d '{"repo_url":"https://github.com/octocat/Hello-World"}'
```

Example response:

```json
{
  "id": 1,
  "repo_url": "https://github.com/octocat/Hello-World",
  "repo_owner": "octocat",
  "repo_name": "Hello-World",
  "status": "created",
  "error_message": null
}
```

Validation errors return a clean `422` response with a `detail` message.

## POST /projects/{id}/scan

Clones or fetches the repository, runs scanners, stores gaps, and returns a scan summary.

```bash
curl -X POST http://localhost:8000/projects/1/scan
```

Example response shape:

```json
{
  "scan_id": 1,
  "project_id": 1,
  "repo_owner": "octocat",
  "repo_name": "Hello-World",
  "status": "scanned",
  "total_files": 8,
  "total_folders": 2,
  "reality_score": 92,
  "total_gaps": 1,
  "high_gaps": 0,
  "medium_gaps": 0,
  "low_gaps": 1,
  "category_counts": {
    "Docs": 1
  },
  "gaps": [],
  "analysis": {}
}
```

Clone failures return `400` with a user-safe error message.

## POST /projects/demo/scan

Runs the built-in local demo repo scan.

```bash
curl -X POST http://localhost:8000/projects/demo/scan
```

Expected response values:

```json
{
  "repo_owner": "local",
  "repo_name": "realitycheck-demo-app",
  "reality_score": 0,
  "total_gaps": 39
}
```

## GET /projects/{project_id}/scans/{scan_id}/report

Exports a markdown report for a scan.

```bash
curl http://localhost:8000/projects/1/scans/1/report
```

Response:

```text
# RealityCheck AI Report: owner/repo

- Reality Score: **...**
- Total Gaps: **...**
```
