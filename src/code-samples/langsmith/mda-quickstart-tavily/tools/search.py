"""Managed Deep Agents quickstart, Tavily variant: the custom search tool.

Lives next to agent.py so `from tools.search import internet_search` resolves
when the runner executes agent.py (Python puts the script's directory first
on sys.path).
"""

# :snippet-start: mda-quickstart-tavily-search-py
# :codegroup-tab: tools/search.py
import os
from typing import Literal

from langchain.tools import tool
from tavily import TavilyClient


tavily_client = TavilyClient(api_key=os.environ["TAVILY_API_KEY"])


@tool
def internet_search(
    query: str,
    max_results: int = 5,
    topic: Literal["general", "news", "finance"] = "general",
) -> dict:
    """Search the internet for relevant sources."""
    return tavily_client.search(
        query,
        max_results=max_results,
        topic=topic,
    )
# :snippet-end:
