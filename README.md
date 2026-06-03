# Crypto Market Intelligence Platform

Full-stack V1 crypto market intelligence platform for low-cost single-VPS
deployment. It collects public crypto market data, calculates deterministic
technical signals, generates risk alerts, supports research backtesting,
supports simulated paper trading, and presents everything in a clean Next.js
dashboard.

V1 is optimized for Docker Compose on one VPS, free public market data through
CCXT, and DeepSeek explanations only on demand. It preserves the research-only
product boundary: no live trading, no wallet connection, no private exchange
credentials, no leverage, no payment system, and no personalized financial
advice.

Every major product page should carry this disclaimer:

> This platform provides data-driven market intelligence for educational and
> research purposes only. It is not personalized financial advice.

## V1 Docs

- [V1 product spec](docs/V1_PRODUCT_SPEC.md)
- [Single-VPS deployment](docs/DEPLOYMENT_VPS.md)
- [Cost control](docs/COST_CONTROL.md)
- [Security notes](docs/SECURITY.md)
- [V1 runbook](docs/runbook.md)
- [Production deployment](docs/production_deployment.md)
- [Backup and restore](docs/backup_restore.md)
- [Observability](docs/observability.md)

## Tech Stack

- Python 3.11+
- FastAPI
- Next.js App Router
- TypeScript
- Tailwind CSS
- SQLAlchemy 2.x
- Alembic
- PostgreSQL
- Redis
- CCXT
- pandas and numpy
- OpenAI Python SDK for DeepSeek's OpenAI-compatible API
- tenacity
- APScheduler
- httpx
- structured JSON logging
- Prometheus-compatible metrics
- optional OpenTelemetry tracing
- optional Sentry error reporting
- pytest
- Pydantic Settings
- Docker Compose
- Vitest and React Testing Library

## Local Setup

```bash
cd crypto-intelligence-platform/backend
python3.11 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
cp .env.example .env
```

Important backend settings:

```env
SIGNAL_MIN_CANDLES=60
SIGNAL_DEFAULT_LIMIT=200
SIGNAL_REFERENCE_SYMBOL=BTC/USDT
ENABLE_AI_SIGNAL_EXPLANATION=false
MARKET_TOP_N=30
MARKET_BACKFILL_YEARS=3
MARKET_BACKFILL_TIMEFRAME=1h
MARKET_BACKFILL_BATCH_LIMIT=300
MARKET_BACKFILL_QUOTE=USDT
ENABLE_MARKET_DATA_SCHEDULER=true
MARKET_DATA_UPDATE_INTERVAL_SECONDS=3600
MARKET_DATA_UPDATE_LIMIT=300
MARKET_DATA_UPDATE_TIMEFRAME=1h
MARKET_DATA_UPDATE_TOP_N=30
MARKET_DATA_UPDATE_USE_TOP_MARKET_CAP=true
MARKET_DATA_UPDATE_ON_STARTUP=true
ENABLE_ALERT_ENGINE=true
ENABLE_ALERT_SCHEDULER=false
ALERT_EVALUATION_INTERVAL_SECONDS=300
ALERT_DEFAULT_SYMBOLS=BTC/USDT,ETH/USDT,BNB/USDT,SOL/USDT,XRP/USDT,DOGE/USDT,ADA/USDT,TRX/USDT,TON/USDT,LINK/USDT,AVAX/USDT,SUI/USDT,XLM/USDT,BCH/USDT,HBAR/USDT,LTC/USDT,DOT/USDT,UNI/USDT,APT/USDT,NEAR/USDT,ICP/USDT,ETC/USDT,ARB/USDT,OP/USDT,FIL/USDT,ATOM/USDT,INJ/USDT,SEI/USDT,HYPE/USDT,PEPE/USDT
ALERT_DEFAULT_TIMEFRAME=1h
ALERT_SIGNAL_SCORE_THRESHOLD=70
ALERT_HIGH_RISK_THRESHOLD=75
ALERT_DEDUP_WINDOW_MINUTES=60
ENABLE_AI_ALERT_EXPLANATION=false
ENABLE_WEBHOOK_NOTIFICATIONS=false
ALERT_WEBHOOK_URL=
ENABLE_EMAIL_NOTIFICATIONS=false
RELATIVE_STRENGTH_BASE_SYMBOL=BTC/USDT
RELATIVE_STRENGTH_SYMBOLS=ETH/USDT,BNB/USDT,SOL/USDT,XRP/USDT,DOGE/USDT,ADA/USDT,TRX/USDT,TON/USDT,LINK/USDT,AVAX/USDT,SUI/USDT,XLM/USDT,BCH/USDT,HBAR/USDT,LTC/USDT,DOT/USDT,UNI/USDT,APT/USDT,NEAR/USDT,ICP/USDT,ETC/USDT,ARB/USDT,OP/USDT,FIL/USDT,ATOM/USDT,INJ/USDT,SEI/USDT,HYPE/USDT,PEPE/USDT
RELATIVE_STRENGTH_TIMEFRAME=1h
RELATIVE_STRENGTH_LOOKBACK_LIMIT=750
ENABLE_RELATIVE_STRENGTH_SCHEDULER=true
RELATIVE_STRENGTH_INTERVAL_SECONDS=900
ENABLE_AI_RELATIVE_STRENGTH_ALERT_EXPLANATION=false
ENABLE_NEWS_SCHEDULER=true
NEWS_FETCH_INTERVAL_MINUTES=10
NEWS_ANALYZE_INTERVAL_MINUTES=10
NEWS_BRIEFING_INTERVAL_MINUTES=30
NEWS_MORNING_BRIEFING_TIME=08:30
NEWS_TIMEZONE=America/New_York
NEWS_MAX_ITEMS_PER_FETCH=50
NEWS_DEDUPE_TITLE_SIMILARITY=0.88
NEWS_LLM_ENABLED=true
NEWS_LLM_MAX_ITEMS_PER_BATCH=10
NEWS_ALERT_ENABLED=true
NEWSAPI_API_KEY=
CRYPTOPANIC_API_KEY=
GDELT_ENABLED=true
RSS_NEWS_ENABLED=true
FRONTEND_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
BACKTEST_DEFAULT_INITIAL_CAPITAL=10000
BACKTEST_DEFAULT_FEE_BPS=10
BACKTEST_DEFAULT_SLIPPAGE_BPS=5
BACKTEST_DEFAULT_MAX_POSITION_PCT=1.0
BACKTEST_DEFAULT_TIMEFRAME=1h
BACKTEST_MIN_CANDLES=100
ENABLE_AI_BACKTEST_EXPLANATION=false
PAPER_DEFAULT_INITIAL_BALANCE=10000
PAPER_DEFAULT_FEE_BPS=10
PAPER_DEFAULT_SLIPPAGE_BPS=5
PAPER_MAX_POSITION_PCT=0.25
PAPER_MAX_DAILY_LOSS_PCT=0.05
PAPER_MAX_OPEN_POSITIONS=5
PAPER_ALLOW_SHORTING=false
PAPER_ALLOW_LEVERAGE=false
ENABLE_AI_PAPER_TRADING_EXPLANATION=false
ENABLE_SIGNAL_TO_PAPER_TRADE=false
JWT_SECRET_KEY=
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=30
AUTH_COOKIE_SECURE=false
AUTH_COOKIE_SAMESITE=lax
ENABLE_AUTH=true
ENABLE_MULTI_WORKSPACE=true
DEFAULT_PLAN=free
ENABLE_USAGE_LIMITS=true
FREE_PLAN_MAX_WATCHLIST_SYMBOLS=10
FREE_PLAN_MAX_BACKTESTS_PER_MONTH=20
FREE_PLAN_MAX_AI_EXPLANATIONS_PER_MONTH=50
FREE_PLAN_MAX_PAPER_ACCOUNTS=1
PRO_PLAN_MAX_WATCHLIST_SYMBOLS=50
PRO_PLAN_MAX_BACKTESTS_PER_MONTH=500
PRO_PLAN_MAX_AI_EXPLANATIONS_PER_MONTH=1000
PRO_PLAN_MAX_PAPER_ACCOUNTS=5
PREMIUM_PLAN_MAX_WATCHLIST_SYMBOLS=200
PREMIUM_PLAN_MAX_BACKTESTS_PER_MONTH=5000
PREMIUM_PLAN_MAX_AI_EXPLANATIONS_PER_MONTH=10000
PREMIUM_PLAN_MAX_PAPER_ACCOUNTS=20
APP_VERSION=0.1.0
DEPLOYMENT_ENV=local
SERVICE_NAME=crypto-intelligence-platform
ENABLE_JSON_LOGGING=true
ENABLE_REQUEST_LOGGING=true
ENABLE_METRICS=true
ENABLE_OTEL=false
OTEL_EXPORTER_OTLP_ENDPOINT=
OTEL_SERVICE_NAME=crypto-intelligence-platform-api
ENABLE_SENTRY=false
SENTRY_DSN=
SENTRY_ENVIRONMENT=local
SENTRY_TRACES_SAMPLE_RATE=0.1
ENABLE_RATE_LIMITING=true
RATE_LIMIT_DEFAULT=100/minute
RATE_LIMIT_AUTH=20/minute
RATE_LIMIT_AI=30/minute
RATE_LIMIT_BACKTEST=10/minute
RATE_LIMIT_PAPER_ORDER=30/minute
ENABLE_SECURITY_HEADERS=true
TRUSTED_HOSTS=localhost,127.0.0.1
CORS_ALLOWED_ORIGINS=http://localhost:3000
DATABASE_POOL_SIZE=10
DATABASE_MAX_OVERFLOW=20
DATABASE_POOL_TIMEOUT=30
DATABASE_POOL_RECYCLE=1800
DB_BACKUP_DIR=/backups
LOG_REDACTION_ENABLED=true
LLM_PROVIDER=deepseek
DEEPSEEK_API_KEY=
DEEPSEEK_BASE_URL=https://api.deepseek.com
DEEPSEEK_MODEL=deepseek-v4-pro
```

`JWT_SECRET_KEY` and `DEEPSEEK_API_KEY` must only be provided through the
environment. Never commit API keys, JWT secrets, passwords, or tokens.
Docker Compose generates a temporary runtime JWT secret when this variable is
empty so local auth endpoints can be exercised; production deployments should
set a stable secret explicitly.

Frontend settings:

```env
NEXT_PUBLIC_API_BASE_URL=
BACKEND_INTERNAL_URL=http://localhost:8000
NEXT_PUBLIC_APP_VERSION=
NEXT_PUBLIC_DEPLOYMENT_ENV=local
NEXT_PUBLIC_SENTRY_DSN=
NEXT_PUBLIC_ENABLE_SENTRY=false
```

The frontend calls `/api/backend/*` in the browser. Next.js rewrites those
requests to `BACKEND_INTERNAL_URL`, which avoids Docker browser networking
surprises. Browser-side auth headers are only attached to same-origin proxy
requests, so use the rewrite path for authenticated local frontend sessions.

## Run With Docker Compose

```bash
docker compose -f infra/docker-compose.yml up --build
```

In another shell, run migrations if the database is new:

```bash
cd backend
DATABASE_URL=postgresql+psycopg://postgres:postgres@localhost:5432/crypto_intelligence alembic upgrade head
```

Health check:

```bash
curl http://localhost:8000/health
```

Frontend is available directly at `http://localhost:3000/dashboard`. The same
stack also starts Nginx at `http://localhost:8080`, proxying frontend traffic
and `/api/backend/*` backend requests for a VPS-like layout.

## Local Production Compose

```bash
docker compose -f infra/docker-compose.prod.yml up --build
```

The production-like compose file adds an nginx reverse proxy and optional
Prometheus/Grafana services behind the `observability` profile:

```bash
docker compose -f infra/docker-compose.prod.yml --profile observability up --build
```

Set a stable `JWT_SECRET_KEY` for persistent sessions. Compose can generate a
temporary runtime secret for local testing, but that is not suitable for
production.

## Run Locally

Backend:

```bash
cd crypto-intelligence-platform/backend
python3.11 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
alembic upgrade head
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Frontend:

```bash
cd crypto-intelligence-platform/frontend
npm install
cp .env.local.example .env.local
npm run dev
```

Then open `http://localhost:3000/dashboard`.

## Production Observability

Phase 9 adds:

- JSON logs with request IDs, service, environment, version, route, status, and
  duration fields.
- Redaction for authorization headers, cookies, tokens, passwords, API keys,
  and secrets.
- `X-Request-ID` propagation.
- Centralized structured error responses.
- `/system/health`, `/system/live`, `/system/ready`, `/system/version`.
- `/metrics` in Prometheus text format when `ENABLE_METRICS=true`.
- Optional OpenTelemetry tracing with `ENABLE_OTEL=true`.
- Optional Sentry with `ENABLE_SENTRY=true`.
- Security headers and in-memory API rate limits.

System endpoints:

```bash
curl http://localhost:8000/system/health
curl http://localhost:8000/system/live
curl http://localhost:8000/system/ready
curl http://localhost:8000/system/version
curl http://localhost:8000/metrics
```

Enable OpenTelemetry:

```env
ENABLE_OTEL=true
OTEL_EXPORTER_OTLP_ENDPOINT=http://otel-collector:4318/v1/traces
```

Enable Sentry:

```env
ENABLE_SENTRY=true
SENTRY_DSN=your-environment-provided-dsn
```

The frontend `/system` page displays health, readiness, version, frontend
environment, and API base URL without exposing sensitive settings.

## CI/CD and Deployment

GitHub Actions workflows:

- `.github/workflows/backend-ci.yml`
- `.github/workflows/frontend-ci.yml`
- `.github/workflows/docker-build.yml`
- `.github/workflows/security-scan.yml`

Deployment assets:

- `infra/docker-compose.prod.yml`
- `infra/nginx/nginx.conf`
- `infra/prometheus/prometheus.yml`
- `infra/grafana/dashboards/api-overview.json`
- `infra/deploy/ecs/*`
- `infra/deploy/generic/README.md`

See:

- `docs/production_deployment.md`
- `docs/observability.md`
- `docs/security_checklist.md`
- `docs/runbook.md`
- `docs/incident_response.md`

## Backup and Restore

Backup:

```bash
DATABASE_URL=postgresql://user:password@host:5432/crypto_intelligence \
DB_BACKUP_DIR=/secure/backups \
infra/scripts/db_backup.sh
```

Restore:

```bash
RESTORE_CONFIRM=yes \
DATABASE_URL=postgresql://user:password@host:5432/crypto_intelligence \
infra/scripts/db_restore.sh /secure/backups/crypto_intelligence_YYYYMMDDTHHMMSSZ.dump
```

Smoke test:

```bash
API_BASE_URL=http://localhost:8000 FRONTEND_URL=http://localhost:3000 infra/scripts/smoke_test.sh
```

## Authentication

Phase 8 enables JWT authentication by default with `ENABLE_AUTH=true`.
Production and shared environments must set `JWT_SECRET_KEY` before starting
the API. The backend will not issue access tokens if `JWT_SECRET_KEY` is empty.
Local tests explicitly inject a test secret and disable product-route auth where
older endpoint tests need unauthenticated access.

Register a user:

```bash
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"Password123","full_name":"User Name"}'
```

Login:

```bash
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"Password123"}'
```

Authenticated requests should include:

```bash
Authorization: Bearer ACCESS_TOKEN
```

Refresh and logout:

```bash
curl -X POST http://localhost:8000/auth/refresh \
  -H "Content-Type: application/json" \
  -d '{"refresh_token":"REFRESH_TOKEN"}'

curl -X POST http://localhost:8000/auth/logout \
  -H "Content-Type: application/json" \
  -d '{"refresh_token":"REFRESH_TOKEN"}'
```

Passwords are stored as hashes. Refresh tokens are stored as hashes and can be
revoked. The MVP frontend stores tokens in local storage for local development;
production hardening should move sessions to secure, HttpOnly cookies and add
CSRF protections where needed.

## Workspaces and Roles

Registration creates a default workspace, owner membership, default
preferences, and a starter watchlist with `BTC/USDT`, `ETH/USDT`, and
`SOL/USDT`.

Workspace roles:

- `owner`: full workspace control, including plan and close operations.
- `admin`: read/write access and member management.
- `member`: read/write access to workspace resources.
- `viewer`: read-only access.

Workspace APIs:

```bash
curl -H "Authorization: Bearer ACCESS_TOKEN" http://localhost:8000/workspaces

curl -X POST http://localhost:8000/workspaces \
  -H "Authorization: Bearer ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name":"Research Desk"}'

curl -X POST http://localhost:8000/auth/switch-workspace \
  -H "Authorization: Bearer ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"workspace_id":"WORKSPACE_ID"}'
```

Switching workspaces returns a new access token scoped to the selected
workspace.

## Tenant Isolation

OHLCV market data and token metadata are shared platform data. User-created
resources are workspace-scoped:

- alerts
- backtest runs and trades
- paper accounts, orders, positions, trades, and equity snapshots
- watchlists
- user preferences
- usage events

Services and API routes filter workspace-owned resources by `workspace_id` when
auth is enabled. A user in workspace A cannot read or mutate workspace B
alerts, backtests, paper accounts, or watchlists.

## Watchlists

Watchlists are workspace-owned and enforce plan limits.

```bash
curl -H "Authorization: Bearer ACCESS_TOKEN" http://localhost:8000/watchlists

curl -X POST http://localhost:8000/watchlists \
  -H "Authorization: Bearer ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name":"Layer 1 Watchlist"}'

curl -X POST http://localhost:8000/watchlists/WATCHLIST_ID/symbols \
  -H "Authorization: Bearer ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"symbol":"AVAX/USDT"}'
```

If a workspace reaches its watchlist symbol limit, the API returns a clear plan
limit error. The frontend watchlist editor displays the same limit message.

## Plans and Usage

Plans are internal feature-gate records in Phase 8. Real payment processing,
checkout, customer portals, invoices, and paid subscription charging are not
implemented.

Available internal plans:

- `free`
- `pro`
- `premium`

Feature gates currently cover watchlist symbols, monthly backtests, monthly AI
explanations, paper account limits, alert scheduler access, and webhook
notification access. Plan values are configured with environment variables and
can be changed manually in the database until a later billing/admin phase.

Usage events are recorded for:

- `ai_explanation`
- `backtest_run`
- `paper_order`
- `alert_evaluation`
- `watchlist_symbol_added`

Usage APIs:

```bash
curl -H "Authorization: Bearer ACCESS_TOKEN" http://localhost:8000/usage/summary
curl -H "Authorization: Bearer ACCESS_TOKEN" http://localhost:8000/usage/limits
```

## Ingest Market Data

```bash
curl -X POST http://localhost:8000/market/ingest \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"exchange":"okx","symbols":["BTC/USDT","ETH/USDT","SOL/USDT"],"timeframe":"1h","limit":200}'
```

The ingestion service uses public CCXT market data only. It does not connect to
private trading APIs and does not place orders.

In the frontend, open `/markets` and use **Ingest Market Data** before expecting
charts, snapshots, rankings, or alerts to be populated.

## Backfill Three Years For Top 30 Coins

The platform can build a major-coin universe from CoinGecko market-cap ranking,
filter it to symbols listed on the configured exchange, and backfill stored
OHLCV candles through public CCXT data. Stablecoins and wrapped assets are
excluded by default. If CoinGecko is unavailable, the backend falls back to the
configured `MARKET_TOP_SYMBOLS` list.

Preview the current exchange-supported universe:

```bash
curl -H "Authorization: Bearer $ACCESS_TOKEN" \
  "http://localhost:8000/market/universe?exchange=okx&top_n=30"
```

Run a short smoke backfill first:

```bash
curl -X POST http://localhost:8000/market/backfill \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "exchange": "okx",
    "use_top_market_cap": true,
    "top_n": 30,
    "timeframe": "1h",
    "years": 3,
    "batch_limit": 300,
    "max_batches_per_symbol": 1
  }'
```

Run the full three-year 1h backfill by omitting `max_batches_per_symbol`:

```bash
curl -X POST http://localhost:8000/market/backfill \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "exchange": "okx",
    "use_top_market_cap": true,
    "top_n": 30,
    "timeframe": "1h",
    "years": 3,
    "batch_limit": 300
  }'
```

Three years of 1h candles is roughly 26,000 rows per symbol and around 790,000
rows for 30 symbols before duplicates. Run it during a quiet period on a small
VPS. Existing rows are skipped by `exchange + symbol + timeframe + timestamp`,
so repeated backfills are safe and only insert missing candles.

## Automatic Hourly Market Updates

The backend starts an APScheduler job when `ENABLE_MARKET_DATA_SCHEDULER=true`.
By default it runs every hour, resolves the current top 30 USDT pairs, and
fetches the latest 300 one-hour candles per symbol:

```env
ENABLE_MARKET_DATA_SCHEDULER=true
MARKET_DATA_UPDATE_INTERVAL_SECONDS=3600
MARKET_DATA_UPDATE_LIMIT=300
MARKET_DATA_UPDATE_TIMEFRAME=1h
MARKET_DATA_UPDATE_TOP_N=30
MARKET_DATA_UPDATE_USE_TOP_MARKET_CAP=true
MARKET_DATA_UPDATE_ON_STARTUP=true
```

The job uses public CCXT market data only. It does not require exchange API
keys, does not connect to private trading APIs, and does not place orders. Each
symbol is handled independently, so an unavailable pair is logged and skipped
without stopping the rest of the update. Duplicate candles are ignored through
the OHLCV unique key.

## Query Market Data

```bash
curl "http://localhost:8000/market/ohlcv?symbol=BTC/USDT&timeframe=1h&limit=50"
curl "http://localhost:8000/market/snapshot?symbol=BTC/USDT&timeframe=1h"
```

## News Broadcast

The News Broadcast module fetches crypto news from free sources by default:
RSS feeds and GDELT. NewsAPI and CryptoPanic are enabled automatically only
when `NEWSAPI_API_KEY` or `CRYPTOPANIC_API_KEY` is present. DeepSeek summaries
are on-demand and batched for cost control.

Useful endpoints:

```bash
curl -H "Authorization: Bearer $ACCESS_TOKEN" "http://localhost:8000/api/news/latest?limit=20"
curl -H "Authorization: Bearer $ACCESS_TOKEN" "http://localhost:8000/api/news/briefing?type=latest"
curl -H "Authorization: Bearer $ACCESS_TOKEN" "http://localhost:8000/api/news/alerts"
curl -H "Authorization: Bearer $ACCESS_TOKEN" "http://localhost:8000/api/news/sources"
curl -X POST -H "Authorization: Bearer $ACCESS_TOKEN" "http://localhost:8000/api/news/refresh"
curl -X POST -H "Authorization: Bearer $ACCESS_TOKEN" "http://localhost:8000/api/news/analyze"
```

When `ENABLE_AUTH=true`, register or log in first and pass the returned access
token. For local experiments you can set `ENABLE_AUTH=false`, but production
deployments should keep auth enabled.

Scheduler jobs:

- Fetch RSS/GDELT/enhanced news every 10 minutes.
- Analyze unprocessed news every 10 minutes.
- Generate intraday briefing every 30 minutes.
- Generate morning briefing daily at `NEWS_MORNING_BRIEFING_TIME`.
- Check critical breaking news every 5 minutes.

Cost controls:

- RSS and GDELT work without API keys.
- NewsAPI and CryptoPanic are optional.
- Low-impact news uses rule-based analysis and does not call DeepSeek.
- DeepSeek receives only top high-impact items in batches.
- Duplicate URLs are never summarized repeatedly.
- If LLM generation fails, rule-based analysis remains available.

The Dashboard shows the News Broadcast panel with latest news, Chinese
briefings, symbol filters, and major-news warnings. News analysis is
research-only and does not provide trading instructions.

## Deterministic Signals

Generate a signal without storing it:

```bash
curl "http://localhost:8000/signals/SOL/USDT?timeframe=1h&limit=200"
```

Generate and store the latest signal:

```bash
curl -X POST "http://localhost:8000/signals/SOL/USDT/generate?timeframe=1h&limit=200"
```

Fetch the latest stored signal:

```bash
curl "http://localhost:8000/signals/SOL/USDT/latest?timeframe=1h"
```

Rank symbols by deterministic overall score:

```bash
curl "http://localhost:8000/signals/rank?symbols=BTC/USDT,ETH/USDT,SOL/USDT&timeframe=1h&limit=200"
```

## Signal Logic

The deterministic engine calculates:

- EMA 20, EMA 50, EMA 200
- RSI 14
- MACD, MACD signal, MACD histogram
- ATR 14
- Volume z-score
- Realized volatility
- Rolling high and low

It then produces:

- trend score
- momentum score
- volume score
- volatility risk score
- relative strength score versus `SIGNAL_REFERENCE_SYMBOL`
- overall signal score
- signal direction: `bullish`, `bearish`, `neutral`, or `mixed`
- setup type: `trend_continuation`, `breakout_watch`, `mean_reversion_risk`,
  `breakdown_risk`, `range_bound`, or `insufficient_data`
- risk level: `low`, `medium`, `high`, or `extreme`

## DeepSeek AI Explanation

AI explanations are disabled by default. The deterministic signal is always
returned even when AI is disabled.

```env
ENABLE_AI_SIGNAL_EXPLANATION=true
DEEPSEEK_API_KEY=your-environment-provided-key
DEEPSEEK_MODEL=deepseek-v4-pro
```

Then call:

```bash
curl "http://localhost:8000/signals/SOL/USDT?timeframe=1h&limit=200&include_ai_explanation=true"
```

DeepSeek does not generate the signal directly. It receives the deterministic
signal JSON and explains the system-generated scores, risks, and limitations.
It must not invent news, fundamentals, external catalysts, specific future
levels, or trading instructions.

## Compliance Guardrail

AI explanations are passed through `ComplianceGuardrail` before returning to the
API client. Unsafe trading-advice phrases are removed and compliance warnings
are attached. The deterministic signal itself is produced without AI.

## Alert Engine

Phase 4 evaluates deterministic signal outputs and creates structured alerts.
The evaluator does not call AI and does not send notifications directly.

Manual evaluation:

```bash
curl -X POST http://localhost:8000/alerts/evaluate \
  -H "Content-Type: application/json" \
  -d '{"symbols":["BTC/USDT","ETH/USDT","SOL/USDT"],"timeframe":"1h","limit":200,"send_notifications":false}'
```

List and manage alerts:

```bash
curl "http://localhost:8000/alerts?symbol=SOL/USDT&status=open&limit=50"
curl "http://localhost:8000/alerts/1"
curl -X PATCH http://localhost:8000/alerts/1/status \
  -H "Content-Type: application/json" \
  -d '{"status":"acknowledged"}'
curl -X POST http://localhost:8000/alerts/1/resolve
```

Implemented deterministic rules:

- High signal score.
- Elevated risk.
- Relative strength improvement.
- Breakout confirmation risk.
- Trend damage warning.
- Insufficient data.
- Signal state change.

Severity levels are `info`, `low`, `medium`, `high`, and `critical`. Severity is
based on risk and importance; a high bullish score does not automatically become
critical, while extreme risk usually does.

Deduplication prevents repeated alert spam by checking `dedup_key` within
`ALERT_DEDUP_WINDOW_MINUTES`. Older matching alerts remain in the database and a
new alert can be created after the window expires.

Alert statuses are `open`, `acknowledged`, `resolved`, and `dismissed`.

## Alert Notifications

Console/log notification is available by default. Webhook delivery is disabled
unless explicitly enabled:

```env
ENABLE_WEBHOOK_NOTIFICATIONS=true
ALERT_WEBHOOK_URL=https://your-webhook-endpoint.example/alerts
```

Webhook payloads use:

```json
{
  "event": "crypto_alert",
  "alert": {}
}
```

Webhook failures are logged and returned as delivery failures without crashing
the API. Email notifications are a placeholder for a later phase.

Test notification configuration:

```bash
curl -X POST http://localhost:8000/alerts/test-notification \
  -H "Content-Type: application/json" \
  -d '{"channel":"webhook"}'
```

## Alert Scheduler

The APScheduler-based evaluator is disabled by default. To enable local periodic
evaluation:

```env
ENABLE_ALERT_SCHEDULER=true
ALERT_EVALUATION_INTERVAL_SECONDS=300
ALERT_DEFAULT_SYMBOLS=BTC/USDT,ETH/USDT,BNB/USDT,SOL/USDT,XRP/USDT,DOGE/USDT,ADA/USDT,TRX/USDT,TON/USDT,LINK/USDT,AVAX/USDT,SUI/USDT,XLM/USDT,BCH/USDT,HBAR/USDT,LTC/USDT,DOT/USDT,UNI/USDT,APT/USDT,NEAR/USDT,ICP/USDT,ETC/USDT,ARB/USDT,OP/USDT,FIL/USDT,ATOM/USDT,INJ/USDT,SEI/USDT,HYPE/USDT,PEPE/USDT
ALERT_DEFAULT_TIMEFRAME=1h
```

When enabled, the scheduler evaluates configured symbols and sends notifications
only through enabled channels. It is intentionally simple and does not introduce
Celery or heavy queue infrastructure in Phase 4.

## DeepSeek Alert Explanation

AI alert explanations are disabled by default:

```env
ENABLE_AI_ALERT_EXPLANATION=true
DEEPSEEK_API_KEY=your-environment-provided-key
DEEPSEEK_MODEL=deepseek-v4-pro
```

Then call:

```bash
curl "http://localhost:8000/alerts/1/explain"
```

DeepSeek receives only the already-created alert JSON and explains why the
deterministic rule triggered. It must not create alerts, change severity,
invent news, create specific future levels, or provide trading instructions. The
explanation is passed through the same compliance guardrail before returning.

## Research Backtesting

Phase 6 runs deterministic, long-only research backtests against OHLCV candles
already stored in PostgreSQL. Backtesting never calls exchange APIs directly,
never places orders, and never connects to private exchange endpoints.

Built-in strategies:

- `ema_crossover`: long exposure when fast EMA is above slow EMA.
- `rsi_mean_reversion`: long exposure after oversold RSI until RSI recovery.
- `breakout`: long exposure after a prior rolling-high breakout with volume
  confirmation.
- `relative_strength`: long exposure when the target outperforms a reference
  symbol over a lookback window.

Backtest assumptions:

- Long-only positioning.
- No margin, futures, or execution workflows.
- Position size is capped by `max_position_pct`.
- Fees are applied on entry and exit with `fee_bps`.
- Slippage worsens execution price with `slippage_bps`.
- Signals execute on the next available candle to avoid same-candle look-ahead.
- Results are hypothetical and based on historical data. They do not guarantee
  future performance.

Metrics include final equity, total return, max drawdown, Sharpe ratio, win
rate, profit factor, trade count, average trade return, average holding period,
and exposure time.

List strategies:

```bash
curl http://localhost:8000/backtests/strategies
```

Run a backtest through the API:

```bash
curl -X POST http://localhost:8000/backtests/run \
  -H "Content-Type: application/json" \
  -d '{
    "symbol":"BTC/USDT",
    "timeframe":"1h",
    "strategy_name":"ema_crossover",
    "start_date":"2025-01-01T00:00:00Z",
    "end_date":"2025-03-01T00:00:00Z",
    "initial_capital":10000,
    "fee_bps":10,
    "slippage_bps":5,
    "max_position_pct":1.0,
    "parameters":{"fast_ema":20,"slow_ema":50}
  }'
```

Inspect stored runs:

```bash
curl http://localhost:8000/backtests
curl http://localhost:8000/backtests/{run_id}
curl http://localhost:8000/backtests/{run_id}/trades
curl http://localhost:8000/backtests/{run_id}/equity-curve
```

Open `/backtests` in the frontend to list runs, `/backtests/new` to run a
research backtest, and `/backtests/{runId}` to view metrics, equity curve,
drawdown, trades, parameters, and optional AI explanation.

AI backtest explanations are disabled by default:

```env
ENABLE_AI_BACKTEST_EXPLANATION=true
DEEPSEEK_API_KEY=your-environment-provided-key
DEEPSEEK_MODEL=deepseek-v4-pro
```

Then call:

```bash
curl "http://localhost:8000/backtests/{run_id}/explain"
```

DeepSeek receives only the completed backtest JSON and explains performance,
risk, behavior, limitations, and next validation steps. It must not invent
trades, external catalysts, or future certainty. Output is sanitized by the
compliance guardrail before returning.

## Paper Trading

Phase 7 adds simulated paper trading with virtual capital. It does not connect
to private exchange APIs, request exchange credentials, connect wallets, or
place real orders.

Paper trading features:

- Virtual paper accounts with cash, equity, realized PnL, unrealized PnL, and
  total fees.
- Simulated market orders only.
- Simulated fills from the latest stored OHLCV close.
- Fee and slippage assumptions configured with `PAPER_DEFAULT_FEE_BPS` and
  `PAPER_DEFAULT_SLIPPAGE_BPS`.
- Risk controls for maximum position size, available cash, maximum open
  positions, daily simulated loss, no leverage, and no shorting by default.
- Virtual positions, simulated trade history, equity snapshots, portfolio
  summary, and performance metrics.
- Optional deterministic signal-to-paper-trade simulation, disabled by default.
- Optional DeepSeek paper trading explanations, disabled by default and passed
  through the compliance guardrail.

Create a paper account:

```bash
curl -X POST http://localhost:8000/paper/accounts \
  -H "Content-Type: application/json" \
  -d '{"name":"Main Paper Account","initial_balance":10000}'
```

Submit a simulated market order:

```bash
curl -X POST http://localhost:8000/paper/orders \
  -H "Content-Type: application/json" \
  -d '{
    "account_id":"ACCOUNT_ID",
    "symbol":"BTC/USDT",
    "timeframe":"1h",
    "side":"buy",
    "order_type":"market",
    "notional":500,
    "reason":"Manual research-only simulated order"
  }'
```

Inspect the simulated portfolio:

```bash
curl http://localhost:8000/paper/accounts/ACCOUNT_ID/positions
curl http://localhost:8000/paper/accounts/ACCOUNT_ID/trades
curl http://localhost:8000/paper/accounts/ACCOUNT_ID/portfolio
curl http://localhost:8000/paper/accounts/ACCOUNT_ID/performance
```

Signal-to-paper-trade simulation stays disabled unless explicitly enabled:

```env
ENABLE_SIGNAL_TO_PAPER_TRADE=true
```

Then call:

```bash
curl -X POST http://localhost:8000/paper/accounts/ACCOUNT_ID/signal-execution \
  -H "Content-Type: application/json" \
  -d '{"symbol":"BTC/USDT","timeframe":"1h","limit":200}'
```

DeepSeek paper trading explanations are also disabled by default:

```env
ENABLE_AI_PAPER_TRADING_EXPLANATION=true
DEEPSEEK_API_KEY=your-environment-provided-key
DEEPSEEK_MODEL=deepseek-v4-pro
```

Then call:

```bash
curl http://localhost:8000/paper/accounts/ACCOUNT_ID/explain
curl http://localhost:8000/paper/orders/ORDER_ID/explain
```

Open `/paper` in the frontend for the paper trading overview,
`/paper/accounts` for virtual accounts, `/paper/accounts/new` to create an
account, `/paper/accounts/{accountId}` for portfolio detail, and
`/paper/orders` to inspect simulated order history.

## Frontend Dashboard

Frontend routes:

- `/auth/login`: login form.
- `/auth/register`: registration form and default workspace creation.
- `/dashboard`: market status, tracked symbols, signal ranking, recent alerts,
  News Broadcast, and system status cards.
- `/markets`: symbol/timeframe controls, manual OHLCV ingestion, snapshot,
  candle stats, and candlestick chart.
- `/market-comparison`: BTC Relative Strength Monitor with BRSI ranking,
  relative movement alerts, and per-symbol history charts.
- `/tokens/BTC-USDT`: token detail page with market chart, latest signal, risk
  notes, and optional AI explanation.
- `/signals`: signal ranking and comparison table.
- `/signals/BTC-USDT`: full deterministic signal detail, indicators, relative
  strength, data quality, and optional AI explanation.
- `/alerts`: alert center with filters, manual evaluation, and status actions.
- `/alerts/1`: alert detail, raw payload viewer, status actions, and optional AI
  alert explanation.
- `/backtests`: stored research backtest runs.
- `/backtests/new`: run a new deterministic backtest.
- `/backtests/{runId}`: backtest metrics, equity curve, drawdown, trades,
  parameters, and optional AI explanation.
- `/paper`: paper trading overview with virtual accounts and recent simulated
  orders.
- `/paper/accounts`: list virtual paper accounts.
- `/paper/accounts/new`: create a virtual paper account.
- `/paper/accounts/{accountId}`: virtual portfolio, simulated order form,
  positions, trades, performance, and optional AI explanation.
- `/paper/orders`: simulated order explorer.
- `/watchlists`: workspace watchlist editor.
- `/usage`: current plan, monthly usage, and limits.
- `/system`: operational health, readiness, version, and runtime environment.
- `/workspaces`: workspace list.
- `/workspaces/new`: create a workspace.
- `/workspaces/{workspaceId}`: workspace summary.
- `/workspaces/{workspaceId}/members`: member and role management.
- `/workspaces/{workspaceId}/settings`: workspace settings.
- `/account`: current user profile.
- `/account/preferences`: default symbol, timeframe, theme, and layout.
- `/settings`: read-only operational guide and environment examples.

AI explanations may be disabled by default. The dashboard still shows
deterministic market data, signal scores, and alerts when AI is disabled.

The dashboard copy is intentionally research-oriented. It does not include live
trading controls, wallet connection, private exchange credentials, or real
execution workflows.

Protected frontend routes use `AuthGuard` and redirect to `/auth/login` when no
local session is available. The workspace switcher calls `/auth/switch-workspace`
and stores the returned scoped access token.

## Tests

```bash
cd crypto-intelligence-platform/backend
pytest

cd ../frontend
npm test
npm run build
```

Tests use synthetic OHLCV fixtures and mocked DeepSeek-compatible responses.
They do not call live exchanges or live LLM APIs.

## Phase 9 Scope

Implemented:

- Technical indicator engine using pandas/numpy.
- Deterministic scoring and risk engines.
- Relative strength versus BTC by default.
- BTC Relative Strength Monitor with BRSI scoring, ranking, alerting, and a
  15-minute scheduler.
- News Broadcast with RSS/GDELT ingestion, optional NewsAPI/CryptoPanic
  sources, rule-based impact scoring, batched DeepSeek Chinese summaries,
  major-news alerts, and Dashboard display.
- Signal persistence and ranking APIs.
- Optional DeepSeek explanation of deterministic signals.
- Alert rule engine and severity classification.
- Alert deduplication and persistence.
- Alert management APIs.
- Optional DeepSeek explanation of deterministic alerts.
- Notification framework with log and webhook channels.
- Optional local scheduler for repeated alert evaluation.
- Compliance guardrail integration.
- Next.js dashboard with market, token, signal, alert, and settings routes.
- Typed TypeScript API client.
- Reusable score, risk, alert, chart, table, empty, loading, and error
  components.
- Frontend Dockerfile and Compose integration.
- Frontend unit tests with mocked API behavior.
- Research-only backtesting data loader.
- Long-only strategy registry.
- Fee and slippage model.
- No-look-ahead portfolio simulator.
- Backtest metrics, trade log, and equity curve generation.
- Backtest persistence and API endpoints.
- Optional DeepSeek explanation of completed backtests.
- Backtesting frontend list, form, and detail pages.
- Paper account, order, position, trade, equity snapshot, portfolio, and
  performance modules.
- Simulated market order API endpoints.
- Paper trading risk controls with no leverage and no shorting by default.
- Signal-to-paper-trade simulation behind a feature flag.
- Optional DeepSeek paper trading explanation.
- Paper trading frontend overview, account, detail, order, form, and table
  components.
- User registration, login, refresh, logout, and workspace switching.
- Password hashing and refresh-token hashing.
- JWT access-token validation.
- Workspace creation, membership, roles, and permissions.
- Workspace-scoped alerts, backtests, paper accounts, watchlists, preferences,
  and usage events.
- Watchlist CRUD with plan-limit enforcement.
- Internal free/pro/premium plan definitions and feature gates.
- Monthly usage tracking for AI explanations, backtests, paper orders, alert
  evaluations, and watchlist symbol additions.
- Frontend auth pages, auth guard, token-aware API client, workspace switcher,
  account pages, workspace pages, watchlist editor, and usage page.
- Structured JSON logging and log redaction.
- Request ID and request logging middleware.
- Centralized structured exception handling.
- Health, liveness, readiness, version, and metrics endpoints.
- Optional OpenTelemetry and Sentry setup.
- Security headers and API rate limiting.
- Database pool hardening.
- Non-root production Dockerfiles.
- Production-like Compose, nginx, Prometheus, and Grafana assets.
- GitHub Actions workflows for backend, frontend, Docker builds, and security
  scans.
- Backup, restore, and smoke test scripts.
- ECS/Fargate and generic container deployment templates.
- System frontend page and error boundaries.
- Production deployment, observability, security, backup, runbook, and incident
  response docs.

Not implemented:

- Live trading.
- Private exchange trading APIs.
- Wallet integration.
- Real order execution or portfolio advice.
- Real payment processing, checkout, invoices, or subscription charging.
- Production HttpOnly-cookie session hardening.
- Email invitation delivery.
- Real billing, checkout, or payment processing.
- Wallet connection.
- Private exchange API key forms.

## Next Phases

- Phase 10: Admin operations, audit logs, secure cookie sessions, invitation
  email delivery, and billing integration design.
