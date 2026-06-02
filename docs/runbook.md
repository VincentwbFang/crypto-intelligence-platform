# V1 Runbook

## Quick Health Check

```bash
curl http://localhost:8000/health
curl http://localhost:8000/system/ready
curl http://localhost:3000
```

## Restart Stack

```bash
docker compose -f infra/docker-compose.yml restart
```

## View Logs

```bash
docker compose -f infra/docker-compose.yml logs -f backend
docker compose -f infra/docker-compose.yml logs -f frontend
docker compose -f infra/docker-compose.yml logs -f nginx
```

Search by `request_id` when debugging API errors.

## Run Migrations

```bash
docker compose -f infra/docker-compose.yml exec backend alembic upgrade head
```

## Backup Database

```bash
DB_BACKUP_DIR=./backups infra/scripts/db_backup.sh
```

## Restore Database

```bash
RESTORE_CONFIRM=yes infra/scripts/db_restore.sh ./backups/<backup-file>.sql
```

## Market Data Is Empty

1. Confirm backend readiness.
2. Register/login in the frontend.
3. Use the Markets page to ingest public OHLCV data.
4. Check backend logs for CCXT rate limit or exchange errors.

## Signal Or Alert Pages Are Empty

1. Ingest OHLCV for the symbol and timeframe.
2. Generate a deterministic signal.
3. Run manual alert evaluation.
4. Confirm the workspace filter matches the current logged-in workspace.

## Backtests Fail

1. Confirm stored OHLCV covers the requested date range.
2. Use at least the configured minimum candle count.
3. Review fees, slippage, and strategy parameters.
4. Check backend logs by request ID.

## Paper Order Rejected

1. Confirm the paper account is active.
2. Confirm latest stored OHLCV exists for the symbol.
3. Review cash balance and max position settings.
4. Remember all paper orders are simulated and long-only in V1.

## DeepSeek Explanation Fails

1. Confirm the relevant AI feature flag is enabled.
2. Confirm `DEEPSEEK_API_KEY` is present in the backend environment.
3. Check provider availability and rate limits.
4. Use deterministic outputs while AI is unavailable.
