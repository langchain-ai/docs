#!/usr/bin/env bash
set -euo pipefail

# :snippet-start: runs-list-from-queue-before-sh
QUEUE_ID="<queue-id>"
# :remove-start:
PROJECT_ID=$(curl -s "https://api.smith.langchain.com/api/v1/sessions?name=default&limit=1" \
  -H "x-api-key: $LANGSMITH_API_KEY" | jq -r '.[0].id')
[ -n "$PROJECT_ID" ] && [ "$PROJECT_ID" != "null" ] || { echo "error: could not resolve project id for \"default\"" >&2; exit 1; }
QUEUE_ID=$(curl -s -X POST "https://api.smith.langchain.com/api/v1/annotation-queues" \
  -H "x-api-key: $LANGSMITH_API_KEY" \
  -H "Content-Type: application/json" \
  -d "$(jq -n --arg name "docs-smithdb-migration-$(date +%s%N)-$RANDOM" '{name: $name}')" | jq -r '.id')
[ -n "$QUEUE_ID" ] && [ "$QUEUE_ID" != "null" ] || { echo "error: could not create annotation queue" >&2; exit 1; }
MIN_START=$(date -u -d '-1 month' +%Y-%m-%dT%H:%M:%SZ 2>/dev/null || date -u -v-1m +%Y-%m-%dT%H:%M:%SZ)
SEED_RUN_ID=$(curl -s -X POST "https://api.smith.langchain.com/api/v2/runs/query" \
  -H "x-api-key: $LANGSMITH_API_KEY" \
  -H "Content-Type: application/json" \
  -d "$(jq -n --arg pid "$PROJECT_ID" --arg min "$MIN_START" '{"project_ids": [$pid], "min_start_time": $min, "page_size": 1}')" | jq -r '.items[0].id // empty')
[ -n "$SEED_RUN_ID" ] || { echo "error: could not resolve a run id" >&2; exit 1; }
curl -sf -X POST "https://api.smith.langchain.com/api/v1/annotation-queues/$QUEUE_ID/runs" \
  -H "x-api-key: $LANGSMITH_API_KEY" \
  -H "Content-Type: application/json" \
  -d "[\"$SEED_RUN_ID\"]" > /dev/null
# :remove-end:

SIZE=$(curl -s "https://api.smith.langchain.com/api/v1/annotation-queues/$QUEUE_ID/size?status=needs_my_review" \
  -H "x-api-key: $LANGSMITH_API_KEY")

RUNS=$(curl -s "https://api.smith.langchain.com/api/v1/annotation-queues/$QUEUE_ID/runs?status=needs_my_review" \
  -H "x-api-key: $LANGSMITH_API_KEY")
echo "$RUNS" | jq -r '.[] | "\(.name) \(.status)"'

FIRST_RUN=$(curl -s "https://api.smith.langchain.com/api/v1/annotation-queues/$QUEUE_ID/run/0" \
  -H "x-api-key: $LANGSMITH_API_KEY")
# :snippet-end:

# :remove-start:
[ "$(echo "$SIZE" | jq -r '.size')" = "1" ] || { echo "error: expected size 1, got $SIZE" >&2; exit 1; }
[ "$(echo "$RUNS" | jq 'length')" = "1" ] || { echo "error: expected 1 run, got $RUNS" >&2; exit 1; }
[ "$(echo "$FIRST_RUN" | jq -r '.id')" = "$SEED_RUN_ID" ] || { echo "error: index 0 returned a different run" >&2; exit 1; }
echo "✓ runs-list-from-queue-before validated"
# :remove-end:
