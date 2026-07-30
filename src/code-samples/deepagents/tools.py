"""Deep Agents tools page examples."""

# :snippet-start: tools-pass-tools-py
from deepagents import create_deep_agent

# :remove-start:
def search(query: str) -> str:
    """Search the web."""
    return query


def fetch_url(url: str) -> str:
    """Fetch a URL."""
    return url


def run_query(sql: str) -> str:
    """Run a SQL query."""
    return sql

# :remove-end:

agent = create_deep_agent(
    model="anthropic:claude-sonnet-4-6",
    tools=[search, fetch_url, run_query],
)
# :snippet-end:

# :remove-start:
assert agent is not None
# :remove-end:
