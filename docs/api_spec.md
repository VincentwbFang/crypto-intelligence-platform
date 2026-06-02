# API Spec

## Health

### `GET /health`

Returns basic service health.

Response:

```json
{
  "status": "ok",
  "service": "crypto-intelligence-platform"
}
```

## Market Data

### `POST /market/ingest`

Ingests public OHLCV candles through CCXT.

```json
{
  "exchange": "okx",
  "symbols": ["BTC/USDT", "ETH/USDT", "SOL/USDT"],
  "timeframe": "1h",
  "limit": 200
}
```

### `GET /market/ohlcv`

Query params:

- `symbol`
- `timeframe`
- `limit`

### `GET /market/snapshot`

Query params:

- `symbol`
- `timeframe`

Returns a latest OHLCV snapshot without technical indicators.

## AI

### `GET /ai/signal-summary`

Query params:

- `symbol`
- `timeframe`
- `limit`

Returns a structured, data-only signal explanation when AI signal summaries are
enabled and `DEEPSEEK_API_KEY` is configured. The endpoint returns a disabled
response when `ENABLE_AI_SIGNAL_SUMMARY=false`.

The response is passed through a compliance guardrail before it is returned.
Unsafe trading-advice phrases are removed and compliance warnings are attached
when needed.

## Signals

### `GET /signals/{symbol}`

Query params:

- `timeframe`
- `limit`
- `include_ai_explanation`

Generates a deterministic signal from stored OHLCV rows. AI explanation is
attached only when requested and enabled.

### `POST /signals/{symbol}/generate`

Generates and stores the latest deterministic signal.

### `GET /signals/{symbol}/latest`

Returns the latest stored signal for a symbol and timeframe.

### `GET /signals/rank`

Query params:

- `symbols`
- `timeframe`
- `limit`

Generates deterministic signals for the provided symbols and returns them sorted
by `overall_signal_score` descending.

## Alerts

### `POST /alerts/evaluate`

Evaluates deterministic signal outputs and persists new non-duplicate alerts.

```json
{
  "symbols": ["BTC/USDT", "ETH/USDT", "SOL/USDT"],
  "timeframe": "1h",
  "limit": 200,
  "send_notifications": false
}
```

### `GET /alerts`

Query params:

- `symbol`
- `timeframe`
- `severity`
- `alert_type`
- `status`
- `limit`

Returns stored alerts ordered by newest first.

### `GET /alerts/{alert_id}`

Returns one stored alert.

### `PATCH /alerts/{alert_id}/status`

Updates alert status. Valid statuses are `open`, `acknowledged`, `resolved`, and
`dismissed`.

```json
{
  "status": "acknowledged"
}
```

### `POST /alerts/{alert_id}/resolve`

Marks an alert as resolved and sets `resolved_at`.

### `GET /alerts/{alert_id}/explain`

Returns an optional DeepSeek explanation for an already-created alert. The
endpoint returns a disabled response when `ENABLE_AI_ALERT_EXPLANATION=false`.
AI does not create alerts, change severity, or override deterministic rules.

### `POST /alerts/test-notification`

Sends a test notification through currently configured channels. Webhooks are
skipped unless `ENABLE_WEBHOOK_NOTIFICATIONS=true`.

```json
{
  "channel": "webhook"
}
```

## Future APIs

Backtesting and paper trading APIs are intentionally not implemented in Phase 5.

## Frontend Routes

The Phase 5 dashboard is a Next.js app. It uses backend APIs through a rewrite
proxy at `/api/backend/*`.

- `GET /dashboard`
- `GET /markets`
- `GET /tokens/BTC-USDT`
- `GET /signals`
- `GET /signals/BTC-USDT`
- `GET /alerts`
- `GET /alerts/{alert_id}`
- `GET /settings`
