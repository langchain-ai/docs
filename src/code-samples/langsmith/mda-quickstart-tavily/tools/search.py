"""Managed Deep Agents quickstart, Tavily variant: the custom search tool.

Lives next to agent.py so `from tools.search import internet_search` resolves
when the runner executes agent.py (Python puts the script's directory first
on sys.path).
"""

# :snippet-start: mda-quickstart-tavily-search-py
# :codegroup-tab: tools/search.py
from typing import Literal

from langchain.tools import tool
from managed_deepagents import connections
from tavily import AsyncTavilyClient


@tool
async def internet_search(
    query: str,
    max_results: int = 5,
    topic: Literal["general", "news", "finance"] = "general",
) -> dict:
    """Search the internet for relevant sources."""
    api_key = await connections.get("research-tavily", {"type": "agent"})
    tavily_client = AsyncTavilyClient(api_key=api_key)
    return await tavily_client.search(
        query,
        max_results=max_results,
        topic=topic,
    )
# :snippet-end:

# :remove-start:
assert internet_search.name == "internet_search"
print("✓ internet_search tool defined with connections.get")
# :remove-end:
