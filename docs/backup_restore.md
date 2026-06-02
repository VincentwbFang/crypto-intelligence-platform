# Backup and Restore

## Backup

```bash
cd crypto-intelligence-platform
DATABASE_URL=postgresql://user:password@host:5432/crypto_intelligence \
DB_BACKUP_DIR=/secure/backups \
infra/scripts/db_backup.sh
```

The script uses `pg_dump --format=custom` and writes a timestamped file.

## Restore

```bash
cd crypto-intelligence-platform
RESTORE_CONFIRM=yes \
DATABASE_URL=postgresql://user:password@host:5432/crypto_intelligence \
infra/scripts/db_restore.sh /secure/backups/crypto_intelligence_YYYYMMDDTHHMMSSZ.dump
```

The restore script refuses to run unless `RESTORE_CONFIRM=yes` is set.

## Testing Restores

Restore into a disposable local database at least monthly. Verify:

- `alembic current` reports the expected head.
- `/system/ready` reports database `ok`.
- A sample login and workspace query succeeds.

## Retention

Suggested baseline:

- Hourly backups for 24 hours.
- Daily backups for 30 days.
- Monthly backups for 12 months.

