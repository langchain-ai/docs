#!/usr/bin/env bash
set -euo pipefail

# :snippet-start: runs-retrieve-by-id-before-sh
RUN_ID="<run-id>"
# :remove-start:
PROJECT_ID=$(curl -s "https://api.smith.langchain.com/api/v1/sessions?name=default&limit=1" \
  -H "x-api-key: $LANGSMITH_API_KEY" | jq -r '.[0].id')
[ -n "$PROJECT_ID" ] && [ "$PROJECT_ID" != "null" ] || { echo "error: could not resolve project id for \"default\"" >&2; exit 1; }
FOUND=$(curl -s -X POST "https://api.smith.langchain.com/api/v1/runs/query" \
  -H "x-api-key: $LANGSMITH_API_KEY" \
  -H "Content-Type: application/json" \
  -d "$(jq -n --arg pid "$PROJECT_ID" '{"session": [$pid], "limit": 1}')")
RUN_ID=$(echo "$FOUND" | jq -r '.runs[0].id')
[ -n "$RUN_ID" ] && [ "$RUN_ID" != "null" ] || { echo "error: could not resolve a run id" >&2; exit 1; }
# :remove-end:

curl "https://api.smith.langchain.com/api/v1/runs/$RUN_ID" \
  -H "x-api-key: $LANGSMITH_API_KEY"
# :snippet-end:
