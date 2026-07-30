#!/usr/bin/env bash
set -euo pipefail

# :snippet-start: runs-query-pagination-after-sh
PROJECT_ID=$(curl -s "https://api.smith.langchain.com/api/v1/sessions?name=default&limit=1" \
  -H "x-api-key: $LANGSMITH_API_KEY" | jq -r '.[0].id')
# :remove-start:
[ -n "$PROJECT_ID" ] && [ "$PROJECT_ID" != "null" ] || { echo "error: could not resolve project id for \"default\"" >&2; exit 1; }
# :remove-end:

# Fetch pages, passing the cursor from each response's next_cursor field
# to fetch the next page, until 150 runs are collected or pages run out.
TOTAL=0
CURSOR=""
while :; do
  BODY=$(jq -n --arg pid "$PROJECT_ID" --arg cursor "$CURSOR" \
    'if $cursor == "" then {"project_ids": [$pid]} else {"project_ids": [$pid], "cursor": $cursor} end')
  RESPONSE=$(curl -s -X POST "https://api.smith.langchain.com/v2/runs/query" \
    -H "x-api-key: $LANGSMITH_API_KEY" \
    -H "Content-Type: application/json" \
    -d "$BODY")
  TOTAL=$((TOTAL + $(echo "$RESPONSE" | jq '.items | length')))
  CURSOR=$(echo "$RESPONSE" | jq -r '.next_cursor // empty')
  [ "$TOTAL" -lt 150 ] && [ -n "$CURSOR" ] || break
done
# :snippet-end:
