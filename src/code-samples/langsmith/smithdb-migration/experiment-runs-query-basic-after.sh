#!/usr/bin/env bash
set -euo pipefail

# :remove-start:
if false; then
# :remove-end:
# :snippet-start: experiment-runs-query-basic-after-sh
# :codegroup-tab: After
curl -X POST "https://api.smith.langchain.com/v2/datasets/$DATASET_ID/experiment-runs" \
  -H "x-api-key: $LANGSMITH_API_KEY" \
  -H "Content-Type: application/json" \
  -d "$(jq -n --arg eid "$EXPERIMENT_ID" '{
    "experiment_ids": [$eid],
    "page_size": 20,
    "selects": ["ID", "NAME", "STATUS", "INPUTS_PREVIEW", "OUTPUTS_PREVIEW"]
  }')"
# :snippet-end:
# :remove-start:
fi
# :remove-end:
