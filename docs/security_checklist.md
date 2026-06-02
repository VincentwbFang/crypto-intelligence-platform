# Security Checklist

## Secrets

- Set `JWT_SECRET_KEY` from a secret manager in production.
- Never commit API keys, JWT secrets, webhook secrets, passwords, or tokens.
- Store refresh token hashes only.
- Do not log authorization headers or cookies.

## Authentication

- Keep `ENABLE_AUTH=true` in production.
- Use HTTPS at the load balancer or edge.
- Move browser sessions to secure HttpOnly cookies in a future hardening phase.

## API Controls

- Keep rate limiting enabled.
- Keep security headers enabled.
- Restrict CORS to trusted frontend origins.
- Keep metrics internal or protected.

## Tenant Isolation

- Workspace-owned resources must be filtered by `workspace_id`.
- Add tenant isolation tests for new user-owned resources.
- Viewer role must stay read-only.

## Dependency Security

- Run backend and frontend CI on every PR.
- Run dependency audits and secret scans.
- Rebuild container images after base image security updates.

## Backups

- Run scheduled database backups.
- Test restore procedures regularly.
- Store backups outside the primary database host.

