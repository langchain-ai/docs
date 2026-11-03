"""Overview page: tools parameter example."""

# :remove-start:
def search(query: str) -> str:
    """Search for information."""
    return query


def fetch_page(url: str) -> str:
    """Fetch a web page."""
    return url


def run_query(sql: str) -> str:
    """Run a database query."""
    return sql


# :remove-end:

# :snippet-start: overview-tools-py
from deepagents import create_deep_agent

# KEEP MODEL
agent = create_deep_agent(
    model="anthropic:claude-sonnet-4-6",
    tools=[search, fetch_page, run_query],
)
# :snippet-end:

# :remove-start:
assert agent is not None
print("✓ overview-tools sample validated")
# :remove-end:
