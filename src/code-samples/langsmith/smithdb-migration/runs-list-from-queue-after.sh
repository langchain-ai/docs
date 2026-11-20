#!/usr/bin/env bash
set -euo pipefail

# :snippet-start: runs-list-from-queue-after-sh
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
FETCHED=0
# :remove-end:

COUNT=$(curl -s "https://api.smith.langchain.com/api/v1/platform/annotation-queues/$QUEUE_ID/items/count?status=needs_my_review" \
  -H "x-api-key: $LANGSMITH_API_KEY")

# Items carry the run's lookup keys, not its contents. Pass next_cursor back as
# ?cursor= to fetch the next page.
ITEMS=$(curl -s "https://api.smith.langchain.com/api/v1/platform/annotation-queues/$QUEUE_ID/items?status=needs_my_review&item_type=RUN" \
  -H "x-api-key: $LANGSMITH_API_KEY")

while read -r RUN_ID PROJECT_ID START_TIME; do
  RUN=$(curl -s "https://api.smith.langchain.com/api/v2/runs/$RUN_ID?project_id=$PROJECT_ID&start_time=$START_TIME&selects=NAME&selects=STATUS&selects=INPUTS&selects=OUTPUTS" \
    -H "x-api-key: $LANGSMITH_API_KEY")
  echo "$RUN" | jq -r '"\(.name) \(.status)"'
  # :remove-start:
  [ "$(echo "$RUN" | jq -r '.name // empty')" != "" ] || { echo "error: run has no name: $RUN" >&2; exit 1; }
  FETCHED=$((FETCHED + 1))
  # :remove-end:
done < <(echo "$ITEMS" | jq -r '.items[] | "\(.run_id) \(.project_id) \(.start_time)"')
# :snippet-end:

# :remove-start:
[ "$(echo "$COUNT" | jq -r '.count')" = "1" ] || { echo "error: expected count 1, got $COUNT" >&2; exit 1; }
[ "$FETCHED" = "1" ] || { echo "error: expected 1 fetched run, got $FETCHED" >&2; exit 1; }
echo "✓ runs-list-from-queue-after validated"
# :remove-end:
