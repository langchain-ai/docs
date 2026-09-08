"""Quickstart: OpenAI built-in web search."""

# :remove-start:
import os
import sys

if not os.environ.get("OPENAI_API_KEY"):
    print("[quickstart-provider-openai] Skipping (OPENAI_API_KEY required).")
    sys.exit(0)
# :remove-end:

# :snippet-start: quickstart-search-tool-provider-openai-py
# :codegroup-tab: OpenAI
from deepagents import create_deep_agent

# OpenAI's built-in web search — no extra install or API key needed
internet_search = {"type": "web_search"}
# :snippet-end:

# :remove-start:
research_instructions = """You are an expert researcher. Your job is to conduct thorough research and then write a polished report.

You have access to an internet search tool as your primary means of gathering information.

## `internet_search`

Use this to run an internet search for a given query. You can specify the max number of results to return, the topic, and whether raw content should be included.
"""

agent = create_deep_agent(
    model="openai:gpt-5.5",
    tools=[internet_search],
    system_prompt=research_instructions,
)
result = agent.invoke(
    {"messages": [{"role": "user", "content": "What is langgraph?"}]}
)
assert result is not None
assert result["messages"][-1].content
print("✓ quickstart-provider-openai")
# :remove-end:
