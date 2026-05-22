# Deployment Notes

## Render Backend

1. Create a new Render Web Service.
2. Connect the GitHub repository.
3. Set root directory to `backend`.
4. Use build command:

```bash
pip install -r requirements.txt
```

5. Use start command:

```bash
uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

6. Add environment variables:

```text
APP_ENV=production
DATABASE_URL=postgresql://...
FRONTEND_URL=https://your-vercel-app.vercel.app
CORS_ORIGINS=https://your-vercel-app.vercel.app
GROQ_API_KEY=
OPENAI_API_KEY=
LLM_PROVIDER=auto
```

## Vercel Frontend

1. Create a new Vercel project.
2. Set root directory to `frontend`.
3. Build command:

```bash
npm run build
```

4. Output directory:

```text
dist
```

5. Add environment variable:

```text
VITE_API_URL=https://your-render-api.onrender.com
```

## Supabase/PostgreSQL

SQLite is suitable for local development. For production, provision a PostgreSQL database through Supabase, Render, Neon, or another managed provider and set `DATABASE_URL`.

The current project uses `Base.metadata.create_all` for MVP setup. A production migration layer with Alembic should be added before serious multi-user use.

## CORS Setup

Set `CORS_ORIGINS` on the backend to the exact frontend URL:

```text
CORS_ORIGINS=https://your-vercel-app.vercel.app
```

For multiple origins:

```text
CORS_ORIGINS=http://localhost:5173,https://your-vercel-app.vercel.app
```

## Common Deployment Errors

- Frontend cannot reach API: verify `VITE_API_URL` and redeploy Vercel.
- CORS blocked: add the exact Vercel domain to `CORS_ORIGINS`.
- Database connection fails: verify `DATABASE_URL` and SSL requirements for the provider.
- Clone fails: confirm Render has outbound network access and the target GitHub repo is public.
- LLM explanations missing: add `GROQ_API_KEY` or `OPENAI_API_KEY`; fallback explanations still work without keys.
- Slow scans: move scans to a background worker in Phase 2.
