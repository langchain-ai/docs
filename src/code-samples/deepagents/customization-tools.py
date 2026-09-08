"""Customization: custom tools example."""

# :snippet-start: customization-tools-py
import os
from typing import Literal
from tavily import TavilyClient
from deepagents import create_deep_agent

tavily_client = TavilyClient(api_key=os.environ["TAVILY_API_KEY"])


def internet_search(
    query: str,
    max_results: int = 5,
    topic: Literal["general", "news", "finance"] = "general",
    include_raw_content: bool = False,
):
    """Run a web search"""
    return tavily_client.search(
        query,
        max_results=max_results,
        include_raw_content=include_raw_content,
        topic=topic,
    )


agent = create_deep_agent(
    model="anthropic:claude-sonnet-4-6",
    tools=[internet_search],
)
# :snippet-end:

# :remove-start:
assert agent is not None
# :remove-end:
