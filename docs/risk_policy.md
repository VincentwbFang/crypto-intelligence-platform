# Risk Policy

## Policy

This platform is for market intelligence, monitoring, and research workflows.
It must not present outputs as financial advice.

## Guardrails

- No live trading.
- No order execution.
- No paper trading behavior beyond schema placeholders.
- No strategy performance claims.
- No hardcoded API keys or secrets.
- AI signal summaries must be data-driven frameworks only.
- AI signal summaries must not include personalized advice, reckless borrowed
  exposure language, certainty claims, reckless concentration language, or
  certainty claims.
- Paper-trade examples, when enabled, must be simulated and research-only.
- Phase 3 deterministic signals are research outputs, not trade instructions.
- AI explanations must not modify deterministic signal scores, direction, or
  setup type.
- Phase 4 alerts are monitoring outputs, not action instructions.
- AI alert explanations must not create alerts, change severity, or override
  deterministic rule outputs.
- Webhook notifications must not expose secrets in logs or payload templates.

## Future Requirements

Before any strategy, backtesting, or simulated trading workflow is added, it
should include explicit limitations, test coverage, and clear separation from
live trading execution.
