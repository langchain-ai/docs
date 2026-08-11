#!/usr/bin/env bash
set -euo pipefail

# :snippet-start: threads-list-traces-selecting-fields-after-sh
PROJECT_ID=$(curl -s "https://api.smith.langchain.com/api/v1/sessions?name=default&limit=1" \
  -H "x-api-key: $LANGSMITH_API_KEY" | jq -r '.[0].id')
# :remove-start:
[ -n "$PROJECT_ID" ] && [ "$PROJECT_ID" != "null" ] || { echo "error: could not resolve project id for \"default\"" >&2; exit 1; }
# :remove-end:
THREAD_ID="<thread-id>"
# :remove-start:
MAX_START=$(date -u +%Y-%m-%dT%H:%M:%SZ)
MIN_START=$(date -u -d '-1 month' +%Y-%m-%dT%H:%M:%SZ 2>/dev/null || date -u -v-1m +%Y-%m-%dT%H:%M:%SZ)
THREAD_ID=$(curl -s -X POST "https://api.smith.langchain.com/api/v2/threads/query" \
  -H "x-api-key: $LANGSMITH_API_KEY" \
  -H "Content-Type: application/json" \
  -d "$(jq -n --arg pid "$PROJECT_ID" --arg min "$MIN_START" --arg max "$MAX_START" '{"project_id": $pid, "min_start_time": $min, "max_start_time": $max, "page_size": 1}')" \
  | jq -r '.items[0].thread_id')
[ -n "$THREAD_ID" ] && [ "$THREAD_ID" != "null" ] || { echo "error: could not resolve a thread id for \"default\"" >&2; exit 1; }
# :remove-end:

curl -G "https://api.smith.langchain.com/api/v2/threads/$THREAD_ID/traces" \
  -H "x-api-key: $LANGSMITH_API_KEY" \
  --data-urlencode "project_id=$PROJECT_ID" \
  --data-urlencode "selects=TRACE_ID" \
  --data-urlencode "selects=TOTAL_TOKENS" \
  --data-urlencode "selects=TOTAL_COST"
# :snippet-end:
