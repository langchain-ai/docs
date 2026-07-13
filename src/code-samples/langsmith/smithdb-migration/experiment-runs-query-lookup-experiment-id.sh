#!/usr/bin/env bash
set -euo pipefail

# :remove-start:
if false; then
# :remove-end:
# :snippet-start: experiment-runs-query-lookup-experiment-id-sh
EXPERIMENT_ID=$(curl -s "https://api.smith.langchain.com/api/v1/sessions?name=my-experiment" \
  -H "x-api-key: $LANGSMITH_API_KEY" | jq -r '.[0].id')
# :snippet-end:
# :remove-start:
fi
# :remove-end:
