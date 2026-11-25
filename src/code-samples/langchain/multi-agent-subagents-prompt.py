"""Multi-agent subagents: system prompt enumeration."""

# :remove-start:
import os

os.environ.setdefault("OPENAI_API_KEY", "sk-test-key")

from langchain.tools import tool


@tool
def task(agent_name: str, description: str) -> str:
    """Launch an ephemeral subagent for a task."""
    return f'Delegated "{description}" to {agent_name}'


# :remove-end:

# :snippet-start: multi-agent-subagents-prompt-py
from langchain.agents import create_agent

main_agent = create_agent(
    model="openai:gpt-5.4",
    tools=[task],
    system_prompt=(
        "You coordinate specialized sub-agents. "
        "Available agents:\n"
        "- research: Research and fact-finding\n"
        "- writer: Content creation and editing\n"
        "- reviewer: Code and document review\n"
        "Use the task tool to delegate work."
    ),
)
# :snippet-end:

# :remove-start:
assert main_agent is not None
print("✓ multi-agent-subagents-prompt validated")
# :remove-end:
