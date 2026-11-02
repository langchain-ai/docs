#!/usr/bin/env bash
set -euo pipefail

# :snippet-start: runs-query-fetch-by-id-before-sh
RUN_ID_1="<run-id-1>"
RUN_ID_2="<run-id-2>"
# :remove-start:
PROJECT_ID=$(curl -s "https://api.smith.langchain.com/api/v1/sessions?name=default&limit=1" \
  -H "x-api-key: $LANGSMITH_API_KEY" | jq -r '.[0].id')
[ -n "$PROJECT_ID" ] && [ "$PROJECT_ID" != "null" ] || { echo "error: could not resolve project id for \"default\"" >&2; exit 1; }
MAX_START=$(date -u +%Y-%m-%dT%H:%M:%SZ)
MIN_START=$(date -u -d '-1 month' +%Y-%m-%dT%H:%M:%SZ 2>/dev/null || date -u -v-1m +%Y-%m-%dT%H:%M:%SZ)
FOUND=$(curl -s -X POST "https://api.smith.langchain.com/api/v2/runs/query" \
  -H "x-api-key: $LANGSMITH_API_KEY" \
  -H "Content-Type: application/json" \
  -d "$(jq -n --arg pid "$PROJECT_ID" --arg min "$MIN_START" --arg max "$MAX_START" '{"project_ids": [$pid], "min_start_time": $min, "max_start_time": $max, "page_size": 2}')")
RUN_ID_1=$(echo "$FOUND" | jq -r '.items[0].id // empty')
RUN_ID_2=$(echo "$FOUND" | jq -r '.items[1].id // empty')
[ -n "$RUN_ID_1" ] || { echo "error: could not resolve a run id: $FOUND" >&2; exit 1; }
[ -n "$RUN_ID_2" ] || { echo "error: could not resolve a second run id: $FOUND" >&2; exit 1; }
# :remove-end:

curl -X POST "https://api.smith.langchain.com/api/v1/runs/query" \
  -H "x-api-key: $LANGSMITH_API_KEY" \
  -H "Content-Type: application/json" \
  -d "$(jq -n --arg r1 "$RUN_ID_1" --arg r2 "$RUN_ID_2" '{"id": [$r1, $r2]}')"
# :snippet-end:
