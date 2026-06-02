# Cost Control

V1 is designed to run on a single VPS and avoid recurring vendor costs beyond
hosting and optional AI usage.

## Cost Levers

- Use free public market data through CCXT.
- Keep DeepSeek disabled by default and enable explanations only when needed.
- Prefer stored OHLCV data for backtests, paper fills, and signal generation.
- Run APScheduler at modest intervals, such as every 5-15 minutes.
- Keep Prometheus/Grafana optional on the smallest VPS sizes.
- Avoid heavyweight queues until user volume requires them.

## Suggested Defaults

```env
ENABLE_AI_SIGNAL_EXPLANATION=false
ENABLE_AI_ALERT_EXPLANATION=false
ENABLE_AI_BACKTEST_EXPLANATION=false
ENABLE_AI_PAPER_TRADING_EXPLANATION=false
ENABLE_ALERT_SCHEDULER=false
ALERT_EVALUATION_INTERVAL_SECONDS=300
MARKET_DATA_LIMIT=200
SIGNAL_DEFAULT_LIMIT=200
```

## AI Usage

DeepSeek calls are on-demand. Deterministic platform features continue to work
without AI enabled. Use the AI cache service for repeated explanation payloads
if you wire additional explanation flows.

## Database Growth

Start with a limited symbol list and timeframes. For small beta usage, hourly
OHLCV for a handful of symbols is cheap to store. Add retention policies before
expanding to many symbols or low timeframes.

## When To Upgrade

Upgrade the VPS when you see sustained high CPU during backtests, memory
pressure during frontend builds, or database I/O saturation. The next step is
usually moving PostgreSQL to managed storage before splitting the app.
