#!/usr/bin/env bash
set -euo pipefail

# :snippet-start: runs-retrieve-by-id-after-sh
PROJECT_ID=$(curl -s "https://api.smith.langchain.com/api/v1/sessions?name=default&limit=1" \
  -H "x-api-key: $LANGSMITH_API_KEY" | jq -r '.[0].id')
# :remove-start:
[ -n "$PROJECT_ID" ] && [ "$PROJECT_ID" != "null" ] || { echo "error: could not resolve project id for \"default\"" >&2; exit 1; }
# :remove-end:

RUN_ID="<run-id>"
START_TIME="2025-01-01T12:00:00Z" # Optional, but speeds up retrieval
# :remove-start:
MAX_START=$(date -u +%Y-%m-%dT%H:%M:%SZ)
MIN_START=$(date -u -d '-1 month' +%Y-%m-%dT%H:%M:%SZ 2>/dev/null || date -u -v-1m +%Y-%m-%dT%H:%M:%SZ)
FOUND=$(curl -s -X POST "https://api.smith.langchain.com/v2/runs/query" \
  -H "x-api-key: $LANGSMITH_API_KEY" \
  -H "Content-Type: application/json" \
  -d "$(jq -n --arg pid "$PROJECT_ID" --arg min "$MIN_START" --arg max "$MAX_START" '{"project_ids": [$pid], "min_start_time": $min, "max_start_time": $max, "selects": ["ID", "START_TIME"], "page_size": 1}')")
RUN_ID=$(echo "$FOUND" | jq -r '.items[0].id')
START_TIME=$(echo "$FOUND" | jq -r '.items[0].start_time')
[ -n "$RUN_ID" ] && [ "$RUN_ID" != "null" ] || { echo "error: could not resolve a run id" >&2; exit 1; }
# :remove-end:

curl "https://api.smith.langchain.com/v2/runs/$RUN_ID?project_id=$PROJECT_ID&start_time=$START_TIME" \
  -H "x-api-key: $LANGSMITH_API_KEY"
# :snippet-end:
