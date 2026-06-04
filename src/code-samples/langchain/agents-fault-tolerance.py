"""Agents docs: fault tolerance middleware example."""

# :snippet-start: agents-fault-tolerance-py
from langchain.agents import create_agent
from langchain.agents.middleware import ModelRetryMiddleware, ToolRetryMiddleware
from langchain.tools import tool


@tool
def search(query: str) -> str:
    """Search for a query and return a short summary."""
    return f"Search results for: {query}"


agent = create_agent(
    model="anthropic:claude-sonnet-4-6",
    tools=[search],
    middleware=[
        ModelRetryMiddleware(max_retries=3),
        ToolRetryMiddleware(max_retries=2),
    ],
)
# :snippet-end:


# :remove-start:
if __name__ == "__main__":
    assert agent is not None
    print("✓ agents fault tolerance sample compiles")
# :remove-end:

