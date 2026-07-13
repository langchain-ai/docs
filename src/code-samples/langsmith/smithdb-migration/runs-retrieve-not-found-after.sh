#!/usr/bin/env bash
set -euo pipefail

# :snippet-start: runs-retrieve-not-found-after-sh
PROJECT_ID=$(curl -s "https://api.smith.langchain.com/api/v1/sessions?name=default&limit=1" \
  -H "x-api-key: $LANGSMITH_API_KEY" | jq -r '.[0].id')
# :remove-start:
[ -n "$PROJECT_ID" ] && [ "$PROJECT_ID" != "null" ] || { echo "error: could not resolve project id for \"default\"" >&2; exit 1; }
# :remove-end:

RUN_ID="<run-id>"
START_TIME="2025-01-01T12:00:00Z"
# :remove-start:
RUN_ID=$(uuidgen)
# :remove-end:

HTTP_STATUS=$(curl -s -o /dev/null -w "%{http_code}" \
  "https://api.smith.langchain.com/v2/runs/$RUN_ID?project_id=$PROJECT_ID&start_time=$START_TIME" \
  -H "x-api-key: $LANGSMITH_API_KEY")

if [ "$HTTP_STATUS" = "404" ]; then
  echo "Run $RUN_ID not found"
fi
# :snippet-end:
