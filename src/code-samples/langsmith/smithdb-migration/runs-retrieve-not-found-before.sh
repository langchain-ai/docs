#!/usr/bin/env bash
set -euo pipefail

# :snippet-start: runs-retrieve-not-found-before-sh
RUN_ID="<run-id>"
# :remove-start:
RUN_ID=$(uuidgen)
# :remove-end:

HTTP_STATUS=$(curl -s -o /dev/null -w "%{http_code}" \
  "https://api.smith.langchain.com/api/v1/runs/$RUN_ID" \
  -H "x-api-key: $LANGSMITH_API_KEY")

if [ "$HTTP_STATUS" = "404" ]; then
  echo "Run $RUN_ID not found"
fi
# :snippet-end:
