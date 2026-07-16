#!/usr/bin/env bash
set -euo pipefail

# :snippet-start: runs-add-to-queue-after-sh
QUEUE_ID="<queue-id>"
RUN_ID="<run-id>"
PROJECT_ID="<project-id>"
START_TIME="2026-06-01T12:00:00Z"
# :remove-start:
PROJECT_ID=$(curl -s "https://api.smith.langchain.com/api/v1/sessions?name=default&limit=1" \
  -H "x-api-key: $LANGSMITH_API_KEY" | jq -r '.[0].id')
[ -n "$PROJECT_ID" ] && [ "$PROJECT_ID" != "null" ] || { echo "error: could not resolve project id for \"default\"" >&2; exit 1; }
QUEUE_ID=$(curl -s -X POST "https://api.smith.langchain.com/api/v1/annotation-queues" \
  -H "x-api-key: $LANGSMITH_API_KEY" \
  -H "Content-Type: application/json" \
  -d "$(jq -n --arg name "docs-smithdb-migration-$(date +%s%N)-$RANDOM" '{name: $name}')" | jq -r '.id')
[ -n "$QUEUE_ID" ] && [ "$QUEUE_ID" != "null" ] || { echo "error: could not create annotation queue" >&2; exit 1; }
FOUND=$(curl -s -X POST "https://api.smith.langchain.com/api/v1/runs/query" \
  -H "x-api-key: $LANGSMITH_API_KEY" \
  -H "Content-Type: application/json" \
  -d "$(jq -n --arg pid "$PROJECT_ID" '{"session": [$pid], "limit": 1}')")
RUN_ID=$(echo "$FOUND" | jq -r '.runs[0].id')
START_TIME=$(echo "$FOUND" | jq -r '.runs[0].start_time')
[ -n "$RUN_ID" ] && [ "$RUN_ID" != "null" ] || { echo "error: could not resolve a run id" >&2; exit 1; }
# :remove-end:

curl -X POST "https://api.smith.langchain.com/api/v1/annotation-queues/$QUEUE_ID/runs/by-key" \
  -H "x-api-key: $LANGSMITH_API_KEY" \
  -H "Content-Type: application/json" \
  -d "[{\"run_id\": \"$RUN_ID\", \"session_id\": \"$PROJECT_ID\", \"start_time\": \"$START_TIME\"}]"
# :snippet-end:
