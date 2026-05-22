# Architecture

The backend exposes `GET /api/health` and `POST /api/invoices`.

The data layer is MongoDB. PostgreSQL is not required.

All clients authenticate with JWT bearer tokens and refresh tokens.

Production runs on Render with backend port 8000 and Vercel frontend port 3000.
