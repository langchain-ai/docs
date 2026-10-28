# :remove-start:
#!/usr/bin/env bash
set -euo pipefail
# CI holds the gateway key as LS_GATEWAY_KEY; the docs read LANGSMITH_API_KEY.
export LANGSMITH_API_KEY="${LS_GATEWAY_KEY:-$LANGSMITH_API_KEY}"
# curl exits 0 on an HTTP error status; make a 4xx or 5xx fail this test.
curl() { command curl --fail-with-body "$@"; }
# :remove-end:

# :snippet-start: llm-gateway-quickstart-chat-sh
# :codegroup-tab: cURL
curl https://gateway.smith.langchain.com/v1/chat/completions \
    -H "Authorization: Bearer $LANGSMITH_API_KEY" \
    -H "Content-Type: application/json" \
    -d '{"model":"anthropic/claude-opus-5","messages":[{"role":"user","content":"Explain what an LLM gateway does in one sentence."}]}'
# :snippet-end:
