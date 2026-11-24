"""Multi-agent subagents: enum constraint on the dispatch tool."""

# :snippet-start: multi-agent-subagents-enum-tool-py
from enum import Enum

from langchain.tools import tool


class AgentName(str, Enum):
    RESEARCH = "research"
    WRITER = "writer"
    REVIEWER = "reviewer"


@tool
def task(
    agent_name: AgentName,  # Enum constraint
    description: str,
) -> str:
    """Launch an ephemeral subagent for a task."""
    return f'Delegated "{description}" to {agent_name}'


# :snippet-end:

# :remove-start:
assert task is not None
print("✓ multi-agent-subagents-enum-tool validated")
# :remove-end:
