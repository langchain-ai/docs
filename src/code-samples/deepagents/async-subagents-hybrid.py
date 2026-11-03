"""Async subagents: hybrid ASGI and HTTP deployment."""

# :snippet-start: async-subagents-hybrid-py
from deepagents import AsyncSubAgent

async_subagents = [
    AsyncSubAgent(
        name="researcher",
        description="Research agent",
        graph_id="researcher",
        # No url → ASGI (co-deployed)
    ),
    AsyncSubAgent(
        name="coder",
        description="Coding agent",
        graph_id="coder",
        url="https://coder-deployment.langsmith.dev",
        # url present → HTTP (remote)
    ),
]
# :snippet-end:

# :remove-start:
assert len(async_subagents) == 2
print("✓ async-subagents-hybrid sample validated")
# :remove-end:
