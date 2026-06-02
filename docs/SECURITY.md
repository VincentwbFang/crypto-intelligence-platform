# V1 Security Notes

## Secrets

- `JWT_SECRET_KEY` must come from the environment.
- DeepSeek keys must come from the environment.
- Do not commit `.env`, tokens, passwords, or provider credentials.
- Refresh tokens are stored as hashes only.
- Passwords are stored as hashes only.

## Authentication And Tenancy

- Product routes are protected when `ENABLE_AUTH=true`.
- Workspaces scope user-owned resources.
- Alerts, backtests, paper accounts, watchlists, and usage events are
  workspace-scoped.
- Viewers can read; members can create research resources; admins and owners can
  manage workspace settings according to the permission layer.

## API Hardening

- Request IDs are attached to responses.
- Structured error responses include the request ID.
- Security headers are enabled by default.
- Rate limiting is enabled by default.
- Logs redact sensitive keys, cookies, tokens, passwords, and authorization
  values.

## Compliance Boundary

The platform provides data-driven market intelligence only. It does not request
private exchange credentials, connect wallets, execute real orders, or implement
payment flows in V1.

## Production Checklist

- Set a strong `JWT_SECRET_KEY`.
- Set production CORS origins.
- Enable TLS at the reverse proxy or load balancer.
- Keep database and Redis ports private.
- Run migrations before serving traffic.
- Configure backups and test restore.
- Keep dependency scans in CI.
- Review logs after enabling any new integration.
