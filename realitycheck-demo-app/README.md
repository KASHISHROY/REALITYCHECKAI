# Acme Ops Portal

This intentionally inconsistent repository is a demo target for RealityCheck AI.

## Runtime

- Backend runs on port 8000 at `http://localhost:8000`.
- Frontend runs on port 3000 at `http://localhost:3000`.
- Start the backend with `uvicorn backend.main:app --host 0.0.0.0 --port 8000`.
- Start the frontend with `npm run dev -- --port 3000`.

## Architecture Claims

- The API uses MongoDB through `MONGODB_URI`.
- Authentication uses JWT bearer tokens.
- Redis is required for background jobs.
- RabbitMQ is required for event processing.
- Docker Compose exposes backend port 8000 and frontend port 3000.

## API Contract

- `GET /api/users`
- `POST /api/login`
- `GET /api/products`
- `POST /api/orders`
- `GET /api/reports`
- `GET /api/profile`
- `DELETE /api/users/{id}`

## Required Environment Variables

- `MONGODB_URI`
- `JWT_SECRET`
- `REDIS_URL`
- `RABBITMQ_URL`
- `VITE_API_URL`

The real implementation is intentionally different so RealityCheck AI can find the drift.
