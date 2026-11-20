"""Async subagents: deliver results through your app with a webhook."""

# :snippet-start: async-subagents-deliver-results-py
from deepagents import AsyncSubAgent

async_subagents = [
    AsyncSubAgent(
        name="researcher",
        description="Research agent for information gathering and synthesis",
        graph_id="researcher",
        webhook="https://my-app.example.com/hooks/subagent-finished",
        notify_parent=False,  # Your app delivers the result
    ),
]
# :snippet-end:

# :remove-start:
assert async_subagents[0]["notify_parent"] is False
print("✓ async-subagents-deliver-results sample validated")
# :remove-end:
