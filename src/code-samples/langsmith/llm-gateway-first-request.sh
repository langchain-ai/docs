#!/usr/bin/env bash
set -euo pipefail
# The page sets these in an earlier step that readers fill in by hand. In CI,
# the gateway key arrives as LANGSMITH_GATEWAY_API_KEY; locally, fall back to
# your own LANGSMITH_API_KEY.
export LANGSMITH_API_KEY="${LANGSMITH_GATEWAY_API_KEY:-$LANGSMITH_API_KEY}"
export LANGSMITH_GATEWAY_BASE_URL="https://gateway.smith.langchain.com/v1"
# Readers replace <MODEL_ID> by hand; the test makes the same substitution.
MODEL_ID="openai/gpt-6-luna"
# curl exits 0 on an HTTP error status; make a 4xx or 5xx fail this test.
curl() { command curl --fail-with-body "${@//<MODEL_ID>/$MODEL_ID}"; }

# :snippet-start: llm-gateway-first-request-list-models-sh
curl "$LANGSMITH_GATEWAY_BASE_URL/models" \
    -H "Authorization: Bearer $LANGSMITH_API_KEY"
# :snippet-end:

# :snippet-start: llm-gateway-first-request-chat-sh
curl "$LANGSMITH_GATEWAY_BASE_URL/chat/completions" \
    -H "Authorization: Bearer $LANGSMITH_API_KEY" \
    -H "Content-Type: application/json" \
    -d '{"model":"<MODEL_ID>","messages":[{"role":"user","content":"Explain what an LLM gateway does in one sentence."}]}'
# :snippet-end:
