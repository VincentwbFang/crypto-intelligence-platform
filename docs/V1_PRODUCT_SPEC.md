# V1 Product Spec

## Goal

V1 is a full-stack crypto market intelligence platform for a low-cost single
VPS. It combines public market data, deterministic technical analytics,
research alerts, backtests, simulated paper trading, and on-demand DeepSeek
explanations in one dashboard.

The platform is designed for:

- Personal crypto research.
- A portfolio-grade engineering project.
- A free beta for a small user group.
- A future SaaS foundation.

## Scope

V1 includes:

- Public OHLCV ingestion through CCXT.
- PostgreSQL persistence and Alembic migrations.
- Deterministic indicators, signal scoring, relative strength, and risk notes.
- Alert rules, deduplication, severity levels, and optional notifications.
- Long-only historical backtesting using stored OHLCV data.
- Simulated paper accounts, market fills, positions, trades, PnL, fees, and
  slippage.
- Authentication, workspaces, watchlists, usage tracking, and plan-ready
  feature gates.
- Next.js dashboard pages for markets, signals, alerts, backtests, paper
  trading, usage, and system health.
- Optional DeepSeek explanations, generated only on demand.
- JSON logs, request IDs, health probes, security headers, rate limits, and
  optional Prometheus metrics.

## Safety Boundary

V1 does not include live order execution, private exchange credentials, wallet
connection, leverage, margin, futures execution, payment processing, or billing.

All explanations and dashboard copy are educational and research-only. The
standard page disclaimer is:

> This platform provides data-driven market intelligence for educational and
> research purposes only. It is not personalized financial advice.

## Low-Cost Deployment Assumptions

- One VPS with Docker Compose.
- PostgreSQL and Redis on the same host.
- Nginx reverse proxy in front of frontend and backend containers.
- Free public exchange market data through CCXT.
- DeepSeek requests are optional and on-demand to control cost.
- Lightweight metrics are optional and can be disabled on smaller machines.

## V1 Non-Goals

- No real trade execution.
- No private exchange key storage.
- No wallet connection.
- No payment checkout.
- No advanced distributed job system.
- No high-frequency data processing.
- No guarantee-oriented performance language.
