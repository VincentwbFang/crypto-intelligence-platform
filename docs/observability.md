# Observability

Phase 9 adds structured logs, request IDs, metrics, optional tracing, and
optional Sentry.

## Logs

Backend logs are JSON by default when `ENABLE_JSON_LOGGING=true`.

Included fields:

- timestamp
- level
- service
- environment
- version
- logger
- message
- request_id
- path
- method
- status_code
- duration_ms

Sensitive values are redacted before logging. Request bodies are not logged by
default.

## Request IDs

Every response includes `X-Request-ID`. Incoming safe request IDs are preserved;
missing or unsafe IDs are replaced with a generated UUID.

## Metrics

`GET /metrics` exposes Prometheus text format when `ENABLE_METRICS=true`.

Important metrics:

- `http_requests_total`
- `http_request_duration_seconds`
- `http_requests_in_progress`
- `app_errors_total`
- `ai_requests_total`
- `market_ingestion_total`
- `signal_generation_total`
- `alert_evaluation_total`
- `backtest_runs_total`
- `paper_orders_total`

Labels are intentionally low-cardinality: method, route, status_code, service,
and feature.

## Tracing

OpenTelemetry is disabled by default. Enable with:

```env
ENABLE_OTEL=true
OTEL_EXPORTER_OTLP_ENDPOINT=http://otel-collector:4318/v1/traces
OTEL_SERVICE_NAME=crypto-intelligence-platform-api
```

The app will not require a collector unless tracing is enabled.

## Sentry

Sentry is disabled by default. Enable with:

```env
ENABLE_SENTRY=true
SENTRY_DSN=
SENTRY_ENVIRONMENT=production
SENTRY_TRACES_SAMPLE_RATE=0.1
```

Sensitive data should not be sent. Do not enable PII collection.

