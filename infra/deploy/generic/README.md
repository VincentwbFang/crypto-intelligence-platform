# Generic Container Deployment

This app can run on any container platform that supports a backend container, a
frontend container, PostgreSQL, and Redis.

Minimum runtime requirements:

- Backend container on port `8000`.
- Frontend container on port `3000`.
- PostgreSQL 16+ reachable through `DATABASE_URL`.
- Redis 7+ reachable through `REDIS_URL`.
- Stable `JWT_SECRET_KEY` from a secret manager.
- `FRONTEND_ORIGINS` and `CORS_ALLOWED_ORIGINS` set to the public frontend URL.

Run migrations before routing production traffic:

```bash
cd backend
alembic upgrade head
```

Run smoke tests after deployment:

```bash
API_BASE_URL=https://api.example.com FRONTEND_URL=https://app.example.com infra/scripts/smoke_test.sh
```
