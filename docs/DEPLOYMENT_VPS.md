# Single-VPS Deployment

This guide targets a small VPS in the $30-$50/month range. A practical starting
point is 2 vCPU, 4 GB RAM, 60+ GB SSD, Docker, and Docker Compose.

## 1. Prepare The Server

```bash
sudo apt-get update
sudo apt-get install -y docker.io docker-compose-plugin git
sudo usermod -aG docker "$USER"
```

Log out and back in after adding the user to the Docker group.

## 2. Clone And Configure

```bash
git clone <your-repo-url> crypto-intelligence-platform
cd crypto-intelligence-platform
cp backend/.env.example backend/.env
cp frontend/.env.local.example frontend/.env.local
```

Set at least:

```env
JWT_SECRET_KEY=<generate-a-long-random-secret>
DEPLOYMENT_ENV=production
CORS_ALLOWED_ORIGINS=https://your-domain.example
FRONTEND_ORIGINS=https://your-domain.example
DEEPSEEK_API_KEY=
ENABLE_METRICS=true
ENABLE_OTEL=false
ENABLE_SENTRY=false
```

DeepSeek is optional. Leave the key empty until you want on-demand explanations.

## 3. Start Containers

```bash
docker compose -f infra/docker-compose.yml up --build -d
```

The default development compose exposes:

- Nginx reverse proxy: `http://your-server:8080`
- Frontend direct port: `http://your-server:3000`
- Backend direct port: `http://your-server:8000`

For a production-like local stack with restart policies and optional monitoring:

```bash
docker compose -f infra/docker-compose.prod.yml up --build -d
```

## 4. Run Migrations

```bash
docker compose -f infra/docker-compose.yml exec backend alembic upgrade head
```

## 5. Smoke Test

```bash
API_BASE_URL=http://localhost:8000 FRONTEND_URL=http://localhost:3000 infra/scripts/smoke_test.sh
```

Check:

```bash
curl http://localhost:8000/health
curl http://localhost:8000/system/ready
```

## 6. First Login

Open the frontend, register a user, and use the generated default workspace and
watchlist.

## 7. Recommended VPS Hardening

- Put Nginx behind TLS using Caddy, Traefik, Certbot, or a cloud load balancer.
- Keep PostgreSQL and Redis ports private when deploying beyond local testing.
- Configure firewall rules for SSH, HTTP, and HTTPS only.
- Run database backups daily.
- Rotate `JWT_SECRET_KEY` only with a planned logout window.
- Keep DeepSeek and webhook secrets in environment files excluded from git.
