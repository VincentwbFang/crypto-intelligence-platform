# Production Deployment

## Options

- Docker Compose on a single VM for small internal deployments.
- AWS ECS/Fargate with RDS PostgreSQL and ElastiCache Redis.
- Managed container platforms such as Render, Fly.io, or Railway.

## Local Production-Like Compose

```bash
docker compose -f infra/docker-compose.prod.yml up --build
```

Set a stable `JWT_SECRET_KEY` for persistent sessions. The compose file can
generate a temporary local secret when one is missing, but that is not suitable
for production.

## AWS ECS/Fargate

1. Build backend and frontend images.
2. Push images to ECR.
3. Provision RDS PostgreSQL.
4. Provision ElastiCache Redis.
5. Store `DATABASE_URL`, `REDIS_URL`, `JWT_SECRET_KEY`, and provider keys in
   Secrets Manager or SSM Parameter Store.
6. Run migrations with a one-off backend task:

```bash
alembic upgrade head
```

7. Deploy backend ECS service.
8. Deploy frontend ECS service.
9. Configure ALB:
   - `/api/*` to backend.
   - `/` to frontend.
10. Run smoke tests.

## Rollback

Rollback images first. If a migration is not backwards-compatible, restore from
a tested backup only after confirming the data impact.

