#!/usr/bin/env bash
set -euo pipefail

# :snippet-start: feedback-create-after-sh
RUN_ID="<run-id>"
SESSION_ID="<session-id>"
# :remove-start:
SESSION_ID=$(curl -s "https://api.smith.langchain.com/api/v1/sessions?name=default&limit=1" \
  -H "x-api-key: $LANGSMITH_API_KEY" | jq -r '.[0].id')
[ -n "$SESSION_ID" ] && [ "$SESSION_ID" != "null" ] || { echo "error: could not resolve session id for \"default\"" >&2; exit 1; }
# Prefer v2 with an explicit window; unbounded v1 queries often return empty under load.
MAX_START=$(date -u +%Y-%m-%dT%H:%M:%SZ)
MIN_START=$(date -u -d '-1 month' +%Y-%m-%dT%H:%M:%SZ 2>/dev/null || date -u -v-1m +%Y-%m-%dT%H:%M:%SZ)
FOUND=$(curl -s -X POST "https://api.smith.langchain.com/api/v2/runs/query" \
  -H "x-api-key: $LANGSMITH_API_KEY" \
  -H "Content-Type: application/json" \
  -d "$(jq -n --arg pid "$SESSION_ID" --arg min "$MIN_START" --arg max "$MAX_START" '{"project_ids": [$pid], "min_start_time": $min, "max_start_time": $max, "page_size": 1}')")
RUN_ID=$(echo "$FOUND" | jq -r '.items[0].id // empty')
[ -n "$RUN_ID" ] || { echo "error: could not resolve a run id: $FOUND" >&2; exit 1; }
# :remove-end:

curl -X POST "https://api.smith.langchain.com/api/v1/feedback" \
  -H "x-api-key: $LANGSMITH_API_KEY" \
  -H "Content-Type: application/json" \
  -d "$(jq -n --arg run "$RUN_ID" --arg session "$SESSION_ID" '{"run_id": $run, "key": "user_feedback", "score": 1, "session_id": $session}')"
# :snippet-end:
