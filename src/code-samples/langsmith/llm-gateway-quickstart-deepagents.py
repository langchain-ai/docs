"""LLM Gateway quickstart: route a Deep Agents model call through the gateway."""

# :remove-start:
import os as _os

# CI holds the gateway key as LS_GATEWAY_KEY; the docs read LANGSMITH_API_KEY.
if _os.environ.get("LS_GATEWAY_KEY"):
    _os.environ["LANGSMITH_API_KEY"] = _os.environ["LS_GATEWAY_KEY"]
# The docs tell the reader to export this in the shell.
_os.environ["LANGSMITH_GATEWAY"] = "true"
# :remove-end:

# :snippet-start: llm-gateway-quickstart-deepagents-py
# :codegroup-tab: Python
# pip install "deepagents>=0.1.0"
# export LANGSMITH_API_KEY="lsv2_..."
# export LANGSMITH_GATEWAY="true"
from deepagents import create_deep_agent

# KEEP MODEL
agent = create_deep_agent(model="anthropic:claude-opus-5")
result = agent.invoke({"messages": [{"role": "user", "content": "Explain what an LLM gateway does in one sentence."}]})
print(result["messages"][-1].content)
# :snippet-end:
