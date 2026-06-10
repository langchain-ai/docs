"""Agents docs: steering middleware example."""

# :snippet-start: agents-steering-py
from langchain.agents import create_agent
from langchain.agents.middleware import HumanInTheLoopMiddleware
from langchain.tools import tool


@tool
def search(query: str) -> str:
    """Search for a query and return a short summary."""
    return f"Search results for: {query}"


agent = create_agent(
    model="anthropic:claude-sonnet-4-6",
    tools=[search],
    middleware=[HumanInTheLoopMiddleware(interrupt_on={"write_file": True})],
)
# :snippet-end:


# :remove-start:
if __name__ == "__main__":
    assert agent is not None
    print("✓ agents steering sample compiles")
# :remove-end:

