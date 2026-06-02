# ECS/Fargate Deployment Notes

These manifests are placeholders for an AWS ECS/Fargate deployment. Replace all
`<...>` values with account-specific resources.

Recommended AWS services:

- ECR for backend and frontend container images.
- RDS PostgreSQL for the application database.
- ElastiCache Redis for cache and scheduler coordination.
- Secrets Manager or SSM Parameter Store for `DATABASE_URL`, `REDIS_URL`,
  `JWT_SECRET_KEY`, and provider API keys.
- ALB routing `/api/*` to the backend target group and `/` to the frontend.
- CloudWatch Logs for container logs.

Deployment order:

1. Build and push images to ECR.
2. Provision RDS and ElastiCache.
3. Store secrets in Secrets Manager or SSM.
4. Run `alembic upgrade head` as a one-off backend task.
5. Deploy backend service.
6. Deploy frontend service.
7. Configure ALB listener rules.
8. Run `infra/scripts/smoke_test.sh`.

TLS termination should be configured at the ALB or a managed edge layer.

