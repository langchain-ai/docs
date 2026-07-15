#!/usr/bin/env bash
set -euo pipefail

# :snippet-start: threads-stats-first-start-time-before-sh
PROJECT_ID=$(curl -s "https://api.smith.langchain.com/api/v1/sessions?name=default&limit=1" \
  -H "x-api-key: $LANGSMITH_API_KEY" | jq -r '.[0].id')
# :remove-start:
[ -n "$PROJECT_ID" ] && [ "$PROJECT_ID" != "null" ] || { echo "error: could not resolve project id for \"default\"" >&2; exit 1; }
# :remove-end:
THREAD_ID="<thread-id>"
# :remove-start:
THREAD_ID=$(curl -s -X POST "https://api.smith.langchain.com/v2/threads/query" \
  -H "x-api-key: $LANGSMITH_API_KEY" \
  -H "Content-Type: application/json" \
  -d "$(jq -n --arg pid "$PROJECT_ID" '{"project_id": $pid, "min_start_time": "2026-07-01T00:00:00Z", "max_start_time": "2026-07-31T23:59:59Z", "page_size": 1}')" \
  | jq -r '.items[0].thread_id')
[ -n "$THREAD_ID" ] && [ "$THREAD_ID" != "null" ] || { echo "error: could not resolve a thread id for \"default\"" >&2; exit 1; }
# :remove-end:
THREAD_FILTER="eq(thread_id, \"$THREAD_ID\")"

STATS=$(curl -s -X POST "https://api.smith.langchain.com/api/v1/runs/stats" \
  -H "x-api-key: $LANGSMITH_API_KEY" \
  -H "Content-Type: application/json" \
  -d "$(jq -n --arg pid "$PROJECT_ID" --arg f "$THREAD_FILTER" '{"session": [$pid], "is_root": true, "filter": $f}')")

# The stats endpoint has no "first_start_time" field — a second call, sorted
# ascending, is needed to find the thread's earliest run.
FIRST_RUN=$(curl -s -X POST "https://api.smith.langchain.com/api/v1/runs/query" \
  -H "x-api-key: $LANGSMITH_API_KEY" \
  -H "Content-Type: application/json" \
  -d "$(jq -n --arg pid "$PROJECT_ID" --arg f "$THREAD_FILTER" '{"session": [$pid], "is_root": true, "filter": $f, "order": "asc", "limit": 1}')")

jq -n --argjson stats "$STATS" --argjson first "$FIRST_RUN" \
  '{run_count: $stats.run_count, first_start_time: ($first.runs // [])[0].start_time}'
# :snippet-end:
