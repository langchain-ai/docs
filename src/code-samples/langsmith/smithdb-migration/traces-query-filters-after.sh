#!/usr/bin/env bash
set -euo pipefail

# :snippet-start: traces-query-filters-after-sh
PROJECT_ID=$(curl -s "https://api.smith.langchain.com/api/v1/sessions?name=default&limit=1" \
  -H "x-api-key: $LANGSMITH_API_KEY" | jq -r '.[0].id')
# :remove-start:
[ -n "$PROJECT_ID" ] && [ "$PROJECT_ID" != "null" ] || { echo "error: could not resolve project id for \"default\"" >&2; exit 1; }
# :remove-end:

MAX_START=$(date -u +%Y-%m-%dT%H:%M:%SZ)
MIN_START=$(date -u -d '-1 month' +%Y-%m-%dT%H:%M:%SZ 2>/dev/null || date -u -v-1m +%Y-%m-%dT%H:%M:%SZ)

# trace_filter is implicitly root-run-only — no is_root needed.
curl -s -X POST "https://api.smith.langchain.com/api/v2/traces/query" \
  -H "x-api-key: $LANGSMITH_API_KEY" \
  -H "Content-Type: application/json" \
  -d "$(jq -n --arg pid "$PROJECT_ID" --arg min "$MIN_START" --arg max "$MAX_START" '{
    "project_id": $pid,
    "min_start_time": $min,
    "max_start_time": $max,
    "page_size": 5,
    "trace_filter": "eq(status, \"error\")"
  }')" | jq '.items | map(.root_run.trace_id)'

# trace_ids is a fast-path when you already know which traces you want.
TRACE_ID="<trace-id>"
# :remove-start:
TRACE_ID=$(curl -s -X POST "https://api.smith.langchain.com/api/v2/traces/query" \
  -H "x-api-key: $LANGSMITH_API_KEY" \
  -H "Content-Type: application/json" \
  -d "$(jq -n --arg pid "$PROJECT_ID" --arg min "$MIN_START" --arg max "$MAX_START" '{"project_id": $pid, "min_start_time": $min, "max_start_time": $max, "page_size": 1}')" \
  | jq -r '.items[0].root_run.trace_id')
# :remove-end:
curl -s -X POST "https://api.smith.langchain.com/api/v2/traces/query" \
  -H "x-api-key: $LANGSMITH_API_KEY" \
  -H "Content-Type: application/json" \
  -d "$(jq -n --arg pid "$PROJECT_ID" --arg min "$MIN_START" --arg max "$MAX_START" --arg tid "$TRACE_ID" '{
    "project_id": $pid,
    "min_start_time": $min,
    "max_start_time": $max,
    "trace_ids": [$tid]
  }')" | jq '.items | map(.root_run.trace_id)'
# :snippet-end:
