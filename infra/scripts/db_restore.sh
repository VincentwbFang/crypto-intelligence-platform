#!/usr/bin/env sh
set -eu

if [ "${RESTORE_CONFIRM:-}" != "yes" ]; then
  echo "Set RESTORE_CONFIRM=yes to restore a database backup." >&2
  exit 1
fi

if [ $# -ne 1 ]; then
  echo "Usage: db_restore.sh /path/to/backup.dump" >&2
  exit 1
fi

DATABASE_URL_VALUE="${DATABASE_URL:-}"
if [ -z "$DATABASE_URL_VALUE" ]; then
  echo "DATABASE_URL is required" >&2
  exit 1
fi

backup_file="$1"
if [ ! -f "$backup_file" ]; then
  echo "Backup file not found: $backup_file" >&2
  exit 1
fi

pg_restore --clean --if-exists --no-owner --dbname="$DATABASE_URL_VALUE" "$backup_file"
echo "Restore completed from $backup_file"

