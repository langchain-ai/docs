#!/usr/bin/env bash
set -euo pipefail

# :remove-start:
if false; then
# :remove-end:
# :snippet-start: experiment-runs-query-sort-before-sh
# :codegroup-tab: Before
curl -X POST "https://api.smith.langchain.com/api/v1/datasets/$DATASET_ID/runs" \
  -H "x-api-key: $LANGSMITH_API_KEY" \
  -H "Content-Type: application/json" \
  -d "$(jq -n --arg eid "$EXPERIMENT_ID" '{
    "session_ids": [$eid],
    "sort_params": {
      "sort_by": "correctness",
      "sort_order": "ASC"
    }
  }')"
# :snippet-end:
# :remove-start:
fi
# :remove-end:
