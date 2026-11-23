"""Deep Agents subagents: filter LangSmith runs by lc_agent_name."""

# :snippet-start: subagents-filter-runs-by-name-py
from langsmith import Client

client = Client()

runs = client.list_runs(
    project_name="<your-project>",
    filter='has(metadata, \'{"lc_agent_name": "research-agent"}\')',
)
# :snippet-end:

# :snippet-start: subagents-filter-runs-any-py
runs = client.list_runs(
    project_name="<your-project>",
    filter="has(metadata, 'lc_agent_name')",
)
# :snippet-end:

# :remove-start:
assert client is not None
assert runs is not None
print("✓ subagents-filter-runs validated")
# :remove-end:
