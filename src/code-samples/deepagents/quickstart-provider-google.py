"""Quickstart: Google built-in web search."""

# :remove-start:
import os
import sys

if not os.environ.get("GOOGLE_API_KEY"):
    print("[quickstart-provider-google] Skipping (GOOGLE_API_KEY required).")
    sys.exit(0)
# :remove-end:

# :snippet-start: quickstart-search-tool-provider-google-py
# :codegroup-tab: Google
from deepagents import create_deep_agent

# Google's built-in search — no extra install or API key needed
internet_search = {"google_search": {}}
# :snippet-end:

# :remove-start:
research_instructions = """You are an expert researcher. Your job is to conduct thorough research and then write a polished report.

You have access to an internet search tool as your primary means of gathering information.

## `internet_search`

Use this to run an internet search for a given query. You can specify the max number of results to return, the topic, and whether raw content should be included.
"""

agent = create_deep_agent(
    model="google_genai:gemini-3.6-flash",
    tools=[internet_search],
    system_prompt=research_instructions,
)
result = agent.invoke(
    {"messages": [{"role": "user", "content": "What is langgraph?"}]}
)
assert result is not None
assert result["messages"][-1].content
print("✓ quickstart-provider-google")
# :remove-end:
