"""Managed Deep Agents quickstart, Tavily variant: the agent definition.

Defining the agent needs no LangSmith call; deployment is `mda deploy`,
which the page runs separately.
"""

# :snippet-start: mda-quickstart-tavily-agent-py
# :codegroup-tab: agent.py
from managed_deepagents import define_deep_agent

from tools.search import internet_search

# KEEP MODEL
agent = define_deep_agent(
    name="research-assistant",
    model="openai:gpt-5.5",
    tools=[internet_search],
)
# :snippet-end:

# :remove-start:
assert agent is not None
print("✓ research-assistant defined with the Tavily search tool")
# :remove-end:
