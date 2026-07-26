#!/usr/bin/env bash
set -euo pipefail

# :snippet-start: feedback-create-before-sh
RUN_ID="<run-id>"
# :remove-start:
SESSION_ID=$(curl -s "https://api.smith.langchain.com/api/v1/sessions?name=default&limit=1" \
  -H "x-api-key: $LANGSMITH_API_KEY" | jq -r '.[0].id')
[ -n "$SESSION_ID" ] && [ "$SESSION_ID" != "null" ] || { echo "error: could not resolve session id for \"default\"" >&2; exit 1; }
FOUND=$(curl -s -X POST "https://api.smith.langchain.com/api/v1/runs/query" \
  -H "x-api-key: $LANGSMITH_API_KEY" \
  -H "Content-Type: application/json" \
  -d "$(jq -n --arg pid "$SESSION_ID" '{"session": [$pid], "limit": 1}')")
RUN_ID=$(echo "$FOUND" | jq -r '.runs[0].id')
[ -n "$RUN_ID" ] && [ "$RUN_ID" != "null" ] || { echo "error: could not resolve a run id" >&2; exit 1; }
# :remove-end:

curl -X POST "https://api.smith.langchain.com/api/v1/feedback" \
  -H "x-api-key: $LANGSMITH_API_KEY" \
  -H "Content-Type: application/json" \
  -d "$(jq -n --arg run "$RUN_ID" '{"run_id": $run, "key": "user_feedback", "score": 1}')"
# :snippet-end:
