# Architecture

## Components

- FastAPI backend exposes HTTP APIs.
- Next.js frontend renders the dashboard and calls the backend through a rewrite
  proxy at `/api/backend/*`.
- PostgreSQL stores normalized market, signal, alert, and simulated trade data.
- Alembic manages database migrations.
- Redis is reserved for cache and queue use in later phases.
- Docker Compose provides local backend, database, and Redis services.
- CCXT fetches public market data for OHLCV ingestion.
- DeepSeek is accessed through the OpenAI Python SDK using its OpenAI-compatible
  API and is used only for optional data-driven signal and alert explanations.
- Compliance guardrails sanitize AI output before API responses are returned.
- pandas/numpy calculate deterministic indicators and scores before any AI
  explanation is requested.
- The alert engine evaluates deterministic signals, classifies severity,
  deduplicates repeated alerts, persists alert records, and can send configured
  notifications.
- APScheduler provides an optional local periodic alert evaluator. It is disabled
  by default.
- FastAPI CORS allows configured frontend origins through `FRONTEND_ORIGINS`.

## Backend Layout

- `app/api`: API route modules.
- `app/core`: configuration and runtime utilities.
- `app/db`: SQLAlchemy base, models, and session management.
- `app/data`: future ingestion adapters.
- `app/data/exchanges`: public exchange clients.
- `app/data/ingestion`: data persistence workflows.
- `app/services`: application service layer.
- `app/schemas`: Pydantic API schemas.
- `app/indicators`: deterministic technical indicator calculations.
- `app/signals`: scoring, risk, relative strength, and signal generation.
- `app/alerts`: alert rules, severity, deduplication, evaluation, notification,
  and scheduler components.
- `app/backtesting`: future research-only backtesting.
- `app/paper_trading`: future simulated trading workflows.

## Frontend Layout

- `frontend/app`: Next.js App Router pages.
- `frontend/components/layout`: application shell, navigation, and page headers.
- `frontend/components/market`: snapshots, selectors, candle stats, and OHLCV
  charts.
- `frontend/components/signals`: score cards, badges, ranking tables, indicator
  tables, relative strength, and AI explanation panels.
- `frontend/components/alerts`: alert tables, badges, details, manual
  evaluation, and AI alert explanation panels.
- `frontend/components/common`: loading, error, empty, section, and stat cards.
- `frontend/lib/api`: typed API client modules.
- `frontend/lib/format.ts`: display formatting and symbol route helpers.

The browser calls `/api/backend/*`; Next.js rewrites those requests to
`BACKEND_INTERNAL_URL`, using `http://backend:8000` in Docker Compose.

## Data Model

The schema includes tables for tokens, OHLCV bars, generated signals, alerts,
and paper trades. Phase 3 writes deterministic signal payloads to the `signals`
table. Phase 4 writes structured alert payloads to the `alerts` table.

OHLCV rows are protected by a unique constraint across exchange, symbol,
timeframe, and timestamp.

Signal rows are protected by a unique constraint across symbol, timeframe,
timestamp, and signal type.

Alert rows intentionally do not make `dedup_key` permanently unique. Duplicate
prevention is time-window based so recurring alerts can be valid after the
configured deduplication window expires.

## Alert Flow

1. `SignalService` generates and stores deterministic signals.
2. `AlertRuleEngine` evaluates rules against the signal and optional previous
   signal.
3. `AlertDeduplicator` filters repeated candidates within the configured window.
4. `AlertService` persists new alerts.
5. API calls or the optional scheduler may pass persisted alerts to
   `NotificationService`.
6. `AIAlertExplanationService` can explain a stored alert only when explicitly
   enabled and configured.

No alert component places orders or connects to private trading APIs.
