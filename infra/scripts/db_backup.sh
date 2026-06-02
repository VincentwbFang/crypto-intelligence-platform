#!/usr/bin/env sh
set -eu

BACKUP_DIR="${DB_BACKUP_DIR:-./backups}"
DATABASE_URL_VALUE="${DATABASE_URL:-}"

if [ -z "$DATABASE_URL_VALUE" ]; then
  echo "DATABASE_URL is required" >&2
  exit 1
fi

mkdir -p "$BACKUP_DIR"
timestamp="$(date -u +%Y%m%dT%H%M%SZ)"
backup_file="$BACKUP_DIR/crypto_intelligence_$timestamp.dump"

pg_dump "$DATABASE_URL_VALUE" --format=custom --file="$backup_file"
echo "Backup written to $backup_file"

