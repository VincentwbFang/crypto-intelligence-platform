# Product Spec

## Overview

Crypto Market Intelligence Platform is intended to monitor crypto markets,
generate research signals, and surface risk alerts for analysis workflows.

## Phase 1 Scope

- Backend application foundation.
- PostgreSQL schema and Alembic migrations.
- Redis placeholder for future cache and queue usage.
- Local Docker Compose environment.
- Health check API.
- Initial documentation and coding rules.

## Phase 2 Scope

- Public OHLCV ingestion through CCXT.
- Duplicate-safe OHLCV persistence.
- Market OHLCV and latest snapshot APIs.
- Optional AI-assisted signal summaries using stored OHLCV data.
- DeepSeek `deepseek-v4-pro` support through OpenAI-compatible API settings.
- Compliance guardrails for AI signal output.
- Mocked tests for external exchange and AI dependencies.

## Phase 3 Scope

- Deterministic technical indicators.
- Trend, momentum, volume, volatility risk, and relative strength scores.
- Signal direction, setup type, risk level, and risk notes.
- Signal persistence and ranking APIs.
- Optional DeepSeek explanation of deterministic signal JSON.
- Compliance guardrails for AI explanations.

## Phase 4 Scope

- Deterministic alert rule engine.
- Alert severity classification.
- Time-window alert deduplication.
- Alert persistence and status management APIs.
- Manual alert evaluation endpoint.
- Optional scheduler for repeated local alert evaluation.
- Log and webhook notification framework.
- Optional DeepSeek explanation of stored alert JSON.
- Compliance guardrails for AI alert explanations.

## Phase 5 Scope

- Next.js App Router frontend.
- Dashboard, markets, token detail, signal ranking, signal detail, alert center,
  alert detail, and settings pages.
- Typed TypeScript API client for market, signal, and alert endpoints.
- Candlestick chart for stored OHLCV candles.
- Score, risk, setup, severity, status, table, loading, empty, and error UI
  components.
- Manual market ingestion and alert evaluation UI.
- Optional AI/DeepSeek explanation display with compliance warning handling.
- Frontend Dockerfile and Docker Compose integration.

## Out of Scope

- Private exchange account integrations.
- Streaming market data pipelines.
- Trading execution.
- Backtesting logic.
- Paper trading logic.
- Financial advice or portfolio recommendations.
- Live trading API integrations.
- Profit guarantees or certainty claims.

## Future Capabilities

- Exchange and on-chain data ingestion.
- Research-only backtesting.
- Simulated paper trading.
- Frontend dashboards.
