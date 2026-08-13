"""Async subagents: prevent polling immediately after launch."""

# :remove-start:
from deepagents import AsyncSubAgent

async_subagents = [
    AsyncSubAgent(
        name="researcher",
        description="Research agent",
        graph_id="researcher",
    ),
]
# :remove-end:

# :snippet-start: async-subagents-troubleshooting-polling-py
from deepagents import create_deep_agent

agent = create_deep_agent(
    # KEEP MODEL
    model="google_genai:gemini-3.5-flash",
    system_prompt="""...your instructions...

    After launching an async subagent, ALWAYS return control to the user.
    Never call check_async_task immediately after launch.""",
    subagents=async_subagents,
)
# :snippet-end:

# :remove-start:
assert agent is not None
print("✓ async-subagents-troubleshooting-polling sample validated")
# :remove-end:
