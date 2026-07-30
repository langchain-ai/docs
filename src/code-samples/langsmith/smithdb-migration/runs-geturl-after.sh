#!/usr/bin/env bash
set -euo pipefail

# :snippet-start: runs-geturl-after-sh
RUN_ID="<run-id>"
# :remove-start:
PROJECT_ID=$(curl -s "https://api.smith.langchain.com/api/v1/sessions?name=default&limit=1" \
  -H "x-api-key: $LANGSMITH_API_KEY" | jq -r '.[0].id')
[ -n "$PROJECT_ID" ] && [ "$PROJECT_ID" != "null" ] || { echo "error: could not resolve project id for \"default\"" >&2; exit 1; }
MIN_START=$(date -u -d '-1 month' +%Y-%m-%dT%H:%M:%SZ 2>/dev/null || date -u -v-1m +%Y-%m-%dT%H:%M:%SZ)
FOUND=$(curl -s -X POST "https://api.smith.langchain.com/v2/runs/query" \
  -H "x-api-key: $LANGSMITH_API_KEY" \
  -H "Content-Type: application/json" \
  -d "$(jq -n --arg pid "$PROJECT_ID" --arg min "$MIN_START" '{"project_ids": [$pid], "min_start_time": $min, "page_size": 1}')")
RUN_ID=$(echo "$FOUND" | jq -r '.items[0].id')
[ -n "$RUN_ID" ] && [ "$RUN_ID" != "null" ] || { echo "error: could not resolve a run id" >&2; exit 1; }
# :remove-end:

RUN=$(curl -s "https://api.smith.langchain.com/api/v1/runs/$RUN_ID" \
  -H "x-api-key: $LANGSMITH_API_KEY")
PROJECT_ID=$(echo "$RUN" | jq -r '.session_id')
TRACE_ID=$(echo "$RUN" | jq -r '.trace_id')
START_TIME=$(echo "$RUN" | jq -r '.start_time') # Optional, but speeds up retrieval

curl "https://api.smith.langchain.com/v2/runs/$RUN_ID/url?project_id=$PROJECT_ID&trace_id=$TRACE_ID&start_time=$START_TIME" \
  -H "x-api-key: $LANGSMITH_API_KEY"
# :snippet-end:
