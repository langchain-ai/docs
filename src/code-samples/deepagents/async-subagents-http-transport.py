"""Async subagents: HTTP transport subagent spec."""

# :snippet-start: async-subagents-http-transport-py
from deepagents import AsyncSubAgent

AsyncSubAgent(
    name="researcher",
    description="Research agent",
    graph_id="researcher",
    url="https://my-research-deployment.langsmith.dev",
)
# :snippet-end:

# :remove-start:
print("✓ async-subagents-http-transport sample validated")
# :remove-end:
