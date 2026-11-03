#!/usr/bin/env bash
set -euo pipefail

# :snippet-start: traces-query-totals-before-sh
PROJECT_ID=$(curl -s "https://api.smith.langchain.com/api/v1/sessions?name=default&limit=1" \
  -H "x-api-key: $LANGSMITH_API_KEY" | jq -r '.[0].id')
# :remove-start:
[ -n "$PROJECT_ID" ] && [ "$PROJECT_ID" != "null" ] || { echo "error: could not resolve project id for \"default\"" >&2; exit 1; }
# :remove-end:

START_TIME=$(date -u -d '-1 month' +%Y-%m-%dT%H:%M:%SZ 2>/dev/null || date -u -v-1m +%Y-%m-%dT%H:%M:%SZ)
RESP=$(curl -s -X POST "https://api.smith.langchain.com/api/v1/runs/query" \
  -H "x-api-key: $LANGSMITH_API_KEY" \
  -H "Content-Type: application/json" \
  -d "$(jq -n --arg pid "$PROJECT_ID" --arg start "$START_TIME" '{"session": [$pid], "is_root": true, "limit": 5, "start_time": $start}')")
# :remove-start:
echo "$RESP" | jq -e . >/dev/null 2>&1 || { echo "error: non-JSON runs/query response: $RESP" >&2; exit 1; }
# :remove-end:
echo "$RESP" | jq '(.runs // [])[] | {trace_id, total_tokens, total_cost}'
# :snippet-end:
