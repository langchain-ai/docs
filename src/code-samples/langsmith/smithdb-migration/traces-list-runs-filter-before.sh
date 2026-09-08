#!/usr/bin/env bash
set -euo pipefail

# :snippet-start: traces-list-runs-filter-before-sh
PROJECT_ID=$(curl -s "https://api.smith.langchain.com/api/v1/sessions?name=default&limit=1" \
  -H "x-api-key: $LANGSMITH_API_KEY" | jq -r '.[0].id')
# :remove-start:
[ -n "$PROJECT_ID" ] && [ "$PROJECT_ID" != "null" ] || { echo "error: could not resolve project id for \"default\"" >&2; exit 1; }
# :remove-end:
TRACE_ID="<trace-id>"
# :remove-start:
TRACE_ID=$(curl -s -X POST "https://api.smith.langchain.com/api/v1/runs/query" \
  -H "x-api-key: $LANGSMITH_API_KEY" \
  -H "Content-Type: application/json" \
  -d "$(jq -n --arg pid "$PROJECT_ID" '{"session": [$pid], "is_root": true, "limit": 1}')" \
  | jq -r '(.runs // [])[0].trace_id')
# :remove-end:

curl -s -X POST "https://api.smith.langchain.com/api/v1/runs/query" \
  -H "x-api-key: $LANGSMITH_API_KEY" \
  -H "Content-Type: application/json" \
  -d "$(jq -n --arg pid "$PROJECT_ID" --arg tid "$TRACE_ID" '{"session": [$pid], "trace": $tid, "filter": "eq(run_type, \"llm\")"}')" \
  | jq '.runs // []'
# :snippet-end:
