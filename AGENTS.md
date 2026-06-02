# Agent Guidelines

- Write typed, modular, testable Python code.
- Write TypeScript in strict mode for frontend code.
- Keep application code small and focused.
- Keep frontend components modular, accessible, and reusable.
- Do not hardcode secrets, credentials, tokens, or API keys.
- Never hardcode JWT secrets.
- Never log passwords, raw tokens, refresh tokens, or authorization headers.
- Never log API keys, webhook secrets, cookies, or provider credentials.
- Store password hashes only.
- Store refresh token hashes only.
- Use environment variables and Pydantic Settings for runtime configuration.
- Keep V1 deployable on a single low-cost VPS with Docker Compose unless the
  user explicitly asks for managed infrastructure.
- Prefer free public market data sources and optional/on-demand AI usage.
- Add tests for new modules and behavior.
- Add tests for reusable frontend components and API helpers.
- Avoid financial-advice language in product copy, logs, and API responses.
- Do not implement live trading unless explicitly requested.
- Do not add trading execution UI.
- Do not add wallet connection.
- Do not add private API key forms.
- Do not add real billing or payment processing without explicit instruction.
- Do not display unsafe raw AI output; show sanitized output and compliance
  warnings only.
- Backtest logic must be deterministic, modular, and covered by tests.
- Backtest engine code must not call external APIs, database sessions, or AI
  services.
- Avoid look-ahead bias; signals should execute on a later available candle.
- Include fees and slippage in backtest simulation.
- Do not present backtest results as certain future performance.
- Paper trading must never place real orders.
- Do not add real exchange API key input.
- Use virtual capital only for paper trading.
- Clearly label all paper orders as simulated.
- Enforce no leverage by default.
- Enforce no shorting by default.
- Include fees and slippage in paper trading fills.
- Do not present simulated results as certain future performance.
- All user-owned resources must be workspace-scoped.
- Add tenant isolation tests for every new user-owned resource.
- Enforce workspace permissions before mutating workspace-owned data.
- Keep account, workspace, and finance-related copy compliance-safe.
- Every production route should preserve request ID support.
- Add tests for new middleware and operational routes.
- Keep metrics labels low-cardinality.
- Do not expose sensitive config through health, system, metrics, or frontend
  pages.
- Use non-root Docker containers.
- Deployment manifests must use placeholders, never real cloud ARNs or secrets.
- Production docs must include rollback and backup notes.
- Avoid print statements in application code; use configured logging instead.
- Summarize files changed after each task.
