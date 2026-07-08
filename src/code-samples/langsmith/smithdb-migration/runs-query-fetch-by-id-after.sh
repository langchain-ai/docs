#!/usr/bin/env bash
set -euo pipefail

# :snippet-start: runs-query-fetch-by-id-after-sh
PROJECT_ID=$(curl -s "https://api.smith.langchain.com/api/v1/sessions?name=default&limit=1" \
  -H "x-api-key: $LANGSMITH_API_KEY" | jq -r '.[0].id')
# :remove-start:
[ -n "$PROJECT_ID" ] && [ "$PROJECT_ID" != "null" ] || { echo "error: could not resolve project id for \"default\"" >&2; exit 1; }
# :remove-end:

RUN_ID_1="<run-id-1>"
RUN_ID_2="<run-id-2>"
# :remove-start:
FOUND=$(curl -s -X POST "https://api.smith.langchain.com/v2/runs/query" \
  -H "x-api-key: $LANGSMITH_API_KEY" \
  -H "Content-Type: application/json" \
  -d "$(jq -n --arg pid "$PROJECT_ID" '{"project_ids": [$pid], "page_size": 2}')")
RUN_ID_1=$(echo "$FOUND" | jq -r '.items[0].id')
RUN_ID_2=$(echo "$FOUND" | jq -r '.items[1].id')
[ -n "$RUN_ID_1" ] && [ "$RUN_ID_1" != "null" ] || { echo "error: could not resolve a run id" >&2; exit 1; }
[ -n "$RUN_ID_2" ] && [ "$RUN_ID_2" != "null" ] || { echo "error: could not resolve a run id" >&2; exit 1; }
# :remove-end:

curl -X POST "https://api.smith.langchain.com/v2/runs/query" \
  -H "x-api-key: $LANGSMITH_API_KEY" \
  -H "Content-Type: application/json" \
  -d "$(jq -n --arg pid "$PROJECT_ID" --arg r1 "$RUN_ID_1" --arg r2 "$RUN_ID_2" '{"project_ids": [$pid], "ids": [$r1, $r2]}')"
# :snippet-end:
