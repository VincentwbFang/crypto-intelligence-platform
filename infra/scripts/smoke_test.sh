#!/usr/bin/env sh
set -eu

API_BASE_URL="${API_BASE_URL:-http://localhost:8000}"
FRONTEND_URL="${FRONTEND_URL:-http://localhost:3000}"

check_url() {
  name="$1"
  url="$2"
  if ! curl -fsS "$url" >/dev/null; then
    echo "Smoke check failed: $name ($url)" >&2
    exit 1
  fi
  echo "ok: $name"
}

check_url "api health" "$API_BASE_URL/system/health"
check_url "api liveness" "$API_BASE_URL/system/live"
check_url "api readiness" "$API_BASE_URL/system/ready"
check_url "frontend" "$FRONTEND_URL"

if curl -fsS "$API_BASE_URL/metrics" >/dev/null 2>&1; then
  echo "ok: metrics"
else
  echo "metrics disabled or unavailable"
fi

if [ "${SMOKE_AUTH:-false}" = "true" ]; then
  email="smoke+$(date -u +%s)@example.com"
  payload="{\"email\":\"$email\",\"password\":\"Password123\",\"full_name\":\"Smoke Test\"}"
  register_response="$(curl -fsS -X POST "$API_BASE_URL/auth/register" -H "Content-Type: application/json" -d "$payload")"
  access_token="$(printf '%s' "$register_response" | python -c 'import json,sys; print(json.load(sys.stdin)["access_token"])')"
  curl -fsS "$API_BASE_URL/auth/me" -H "Authorization: Bearer $access_token" >/dev/null
  echo "ok: auth register/me"
fi

