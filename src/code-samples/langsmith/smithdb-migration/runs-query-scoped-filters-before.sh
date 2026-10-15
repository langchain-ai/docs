#!/usr/bin/env bash
set -euo pipefail

# :snippet-start: runs-query-scoped-filters-before-sh
PROJECT_ID=$(curl -s "https://api.smith.langchain.com/api/v1/sessions?name=default&limit=1" \
  -H "x-api-key: $LANGSMITH_API_KEY" | jq -r '.[0].id')
# :remove-start:
[ -n "$PROJECT_ID" ] && [ "$PROJECT_ID" != "null" ] || { echo "error: could not resolve project id for \"default\"" >&2; exit 1; }
# :remove-end:

FILTER='eq(name, "RetrieveDocs")'
TRACE_FILTER='and(eq(feedback_key, "user_score"), eq(feedback_score, 1))'
TREE_FILTER='eq(name, "ExpandQuery")'

curl -X POST "https://api.smith.langchain.com/api/v1/runs/query" \
  -H "x-api-key: $LANGSMITH_API_KEY" \
  -H "Content-Type: application/json" \
  -d "$(jq -n \
    --arg pid "$PROJECT_ID" \
    --arg f "$FILTER" \
    --arg tf "$TRACE_FILTER" \
    --arg treef "$TREE_FILTER" \
    '{"session": [$pid], "filter": $f, "trace_filter": $tf, "tree_filter": $treef}')"
# :snippet-end:
