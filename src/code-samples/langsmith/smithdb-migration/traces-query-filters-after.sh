#!/usr/bin/env bash
set -euo pipefail

# :snippet-start: traces-query-filters-after-sh
PROJECT_ID=$(curl -s "https://api.smith.langchain.com/api/v1/sessions?name=default&limit=1" \
  -H "x-api-key: $LANGSMITH_API_KEY" | jq -r '.[0].id')
# :remove-start:
[ -n "$PROJECT_ID" ] && [ "$PROJECT_ID" != "null" ] || { echo "error: could not resolve project id for \"default\"" >&2; exit 1; }
# :remove-end:

# trace_filter is implicitly root-run-only — no is_root needed.
curl -s -X POST "https://api.smith.langchain.com/v2/traces/query" \
  -H "x-api-key: $LANGSMITH_API_KEY" \
  -H "Content-Type: application/json" \
  -d "$(jq -n --arg pid "$PROJECT_ID" '{
    "project_id": $pid,
    "min_start_time": "2026-07-01T00:00:00Z",
    "max_start_time": "2026-07-31T23:59:59Z",
    "page_size": 5,
    "trace_filter": "eq(status, \"error\")"
  }')" | jq '.items | map(.root_run.trace_id)'

# trace_ids is a fast-path when you already know which traces you want.
TRACE_ID="<trace-id>"
# :remove-start:
TRACE_ID=$(curl -s -X POST "https://api.smith.langchain.com/v2/traces/query" \
  -H "x-api-key: $LANGSMITH_API_KEY" \
  -H "Content-Type: application/json" \
  -d "$(jq -n --arg pid "$PROJECT_ID" '{"project_id": $pid, "min_start_time": "2026-07-01T00:00:00Z", "max_start_time": "2026-07-31T23:59:59Z", "page_size": 1}')" \
  | jq -r '.items[0].root_run.trace_id')
# :remove-end:
curl -s -X POST "https://api.smith.langchain.com/v2/traces/query" \
  -H "x-api-key: $LANGSMITH_API_KEY" \
  -H "Content-Type: application/json" \
  -d "$(jq -n --arg pid "$PROJECT_ID" --arg tid "$TRACE_ID" '{
    "project_id": $pid,
    "min_start_time": "2026-07-01T00:00:00Z",
    "max_start_time": "2026-07-31T23:59:59Z",
    "trace_ids": [$tid]
  }')" | jq '.items | map(.root_run.trace_id)'
# :snippet-end:
