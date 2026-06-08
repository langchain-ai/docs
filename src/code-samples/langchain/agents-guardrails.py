"""Agents docs: guardrails middleware example."""

# :snippet-start: agents-guardrails-py
from langchain.agents import create_agent
from langchain.agents.middleware import PIIMiddleware
from langchain.tools import tool


@tool
def search(query: str) -> str:
    """Search for a query and return a short summary."""
    return f"Search results for: {query}"


agent = create_agent(
    model="anthropic:claude-sonnet-4-6",
    tools=[search],
    middleware=[PIIMiddleware("email")],
)
# :snippet-end:


# :remove-start:
if __name__ == "__main__":
    assert agent is not None
    print("✓ agents guardrails sample compiles")
# :remove-end:

