# Deployment

## Docker Compose (local full stack)
`docker compose up --build`, then open http://localhost:8080. PostgreSQL 16 + API + nginx (serves the SPA and proxies `/api`).
Migrations and demo seeding run on API start (`SILO_AUTO_MIGRATE`, `SILO_SEED_DEMO_DATA`).
*Not verified in the build environment (no Docker daemon). The same code path was verified natively against PostgreSQL 16.*

## Backend on Render
`render.yaml` defines a Docker web service (`backend/`) and a managed PostgreSQL. `postgres://` URLs are normalized to
`postgresql+psycopg://` automatically. Set `SILO_CORS_ORIGINS` to the frontend origin. Health check: `/api/health`.

## Frontend on Vercel
Project root `frontend/` (`vercel.json` included: SPA rewrites). Set `VITE_API_BASE_URL=https://<your-render-service>.onrender.com`.

## Migrations
```bash
cd backend
SILO_DATABASE_URL=postgresql+psycopg://... alembic upgrade head
alembic revision --autogenerate -m "describe change"   # after model changes
```
Not performed: no public deployment was made from this environment.
