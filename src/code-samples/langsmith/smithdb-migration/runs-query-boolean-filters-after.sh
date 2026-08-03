#!/usr/bin/env bash
set -euo pipefail

# :snippet-start: runs-query-boolean-filters-after-sh
PROJECT_ID=$(curl -s "https://api.smith.langchain.com/api/v1/sessions?name=default&limit=1" \
  -H "x-api-key: $LANGSMITH_API_KEY" | jq -r '.[0].id')
# :remove-start:
[ -n "$PROJECT_ID" ] && [ "$PROJECT_ID" != "null" ] || { echo "error: could not resolve project id for \"default\"" >&2; exit 1; }
# :remove-end:

FILTER='and(gt(start_time, "2023-07-15T12:34:56Z"), or(neq(status, "error"), and(eq(feedback_key, "Correctness"), eq(feedback_score, 0.0))))'

curl -X POST "https://api.smith.langchain.com/v2/runs/query" \
  -H "x-api-key: $LANGSMITH_API_KEY" \
  -H "Content-Type: application/json" \
  -d "$(jq -n --arg pid "$PROJECT_ID" --arg f "$FILTER" '{"project_ids": [$pid], "filter": $f}')"
# :snippet-end:
