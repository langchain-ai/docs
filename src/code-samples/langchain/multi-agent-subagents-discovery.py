"""Multi-agent subagents: tool-based discovery."""

# :remove-start:
import os

os.environ.setdefault("OPENAI_API_KEY", "sk-test-key")


def search_agent_registry(query: str = "") -> list[dict[str, str]]:
    agents = [
        {"name": "research", "description": "Research and fact-finding"},
        {"name": "writer", "description": "Content creation and editing"},
        {"name": "reviewer", "description": "Code and document review"},
    ]
    if not query:
        return agents
    return [
        agent
        for agent in agents
        if query in agent["name"] or query in agent["description"]
    ]


def format_agent_list(agents: list[dict[str, str]]) -> str:
    return "\n".join(
        f"- {agent['name']}: {agent['description']}" for agent in agents
    )


# :remove-end:

# :snippet-start: multi-agent-subagents-discovery-py
from langchain.agents import create_agent
from langchain.tools import tool


@tool
def list_agents(query: str = "") -> str:
    """List available subagents, optionally filtered by query."""
    agents = search_agent_registry(query)
    return format_agent_list(agents)


@tool
def task(agent_name: str, description: str) -> str:
    """Launch an ephemeral subagent for a task."""
    return f'Delegated "{description}" to {agent_name}'


main_agent = create_agent(
    model="openai:gpt-5.4",
    tools=[task, list_agents],
    system_prompt="Use list_agents to discover available subagents, then use task to invoke them.",
)
# :snippet-end:

# :remove-start:
assert main_agent is not None
print("✓ multi-agent-subagents-discovery validated")
# :remove-end:
