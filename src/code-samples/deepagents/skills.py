"""Skills: agent setup, runtime loading, permissions, and subagents."""

from pathlib import Path

# :snippet-start: skills-create-agent-py
from deepagents import create_deep_agent
from deepagents.backends.filesystem import FilesystemBackend

backend = FilesystemBackend(root_dir="./my-project")

# KEEP MODEL
agent = create_deep_agent(
    model="anthropic:claude-sonnet-4-6",
    backend=backend,
    skills=["./my-project/skills/"],
)
# :snippet-end:

# :remove-start:
example_dir = (Path.cwd() / "src/code-samples/deepagents").resolve()
backend = FilesystemBackend(root_dir=str(example_dir), virtual_mode=True)
agent = create_deep_agent(
    model="anthropic:claude-sonnet-4-6",
    backend=backend,
    skills=["/skills/"],
)
# :remove-end:

# :snippet-start: skills-dynamic-lists-py
from deepagents import create_deep_agent

SKILLS_BY_ROLE = {
    "engineering": ["/skills/engineering/"],
    "data": ["/skills/data/"],
    "support": ["/skills/support/"],
}


def create_agent_for_user(user_role: str):
    # KEEP MODEL
    return create_deep_agent(
        model="anthropic:claude-sonnet-4-6",
        skills=SKILLS_BY_ROLE.get(user_role, []),
    )
# :snippet-end:

# :snippet-start: skills-namespaced-py
from deepagents import create_deep_agent
from deepagents.backends import CompositeBackend, StateBackend, StoreBackend

# KEEP MODEL
agent = create_deep_agent(
    model="anthropic:claude-sonnet-4-6",
    skills=["/skills/"],
    backend=CompositeBackend(
        default=StateBackend(),
        routes={
            "/skills/": StoreBackend(
                namespace=lambda rt: (
                    rt.server_info.assistant_id,
                    rt.server_info.user.identity,
                ),
            ),
        },
    ),
)
# :snippet-end:

# :remove-start:
def web_search(query: str) -> str:
    """Search the web for information."""
    return f"Results for {query}"
# :remove-end:

# :snippet-start: skills-subagents-py
from deepagents import create_deep_agent

research_subagent = {
    "name": "researcher",
    "description": "Research assistant with specialized skills",
    "system_prompt": "You are a researcher.",
    "tools": [web_search],
    "skills": ["/skills/researcher/"],  # Subagent-specific skills
}

# KEEP MODEL
agent = create_deep_agent(
    model="google_genai:gemini-3.6-flash",
    skills=["/skills/main/"],  # Main agent and GP subagent get these
    subagents=[research_subagent],  # Researcher gets only its own skills
)
# :snippet-end:

# :snippet-start: skills-compose-sources-py
from deepagents import create_deep_agent

# KEEP MODEL
agent = create_deep_agent(
    model="anthropic:claude-sonnet-4-6",
    skills=["/skills/org/", "/skills/team/", "/skills/request/"],
)
# :snippet-end:

# :snippet-start: skills-approval-py
from deepagents import FilesystemPermission, create_deep_agent
from langgraph.checkpoint.memory import MemorySaver

# KEEP MODEL
agent = create_deep_agent(
    model="anthropic:claude-sonnet-4-6",
    skills=["/skills/editable/"],
    permissions=[
        FilesystemPermission(
            operations=["write"],
            paths=["/skills/**"],
            mode="interrupt",
        ),
    ],
    checkpointer=MemorySaver(),  # Required to pause and resume
)
# :snippet-end:

# :snippet-start: skills-writable-py
from deepagents import FilesystemPermission, create_deep_agent
from deepagents.backends import CompositeBackend, StateBackend, StoreBackend
from langgraph.store.memory import InMemoryStore

store = InMemoryStore()  # Use for local dev; omit for LangSmith Deployment

# KEEP MODEL
agent = create_deep_agent(
    model="anthropic:claude-sonnet-4-6",
    backend=CompositeBackend(
        default=StateBackend(),
        routes={
            "/skills/approved/": StoreBackend(
                namespace=lambda rt: ("approved-skills", rt.context.org_id),
            ),
            "/skills/editable/": StoreBackend(
                namespace=lambda rt: (
                    "editable-skills",
                    rt.server_info.user.identity,
                ),
            ),
        },
    ),
    skills=["/skills/approved/", "/skills/editable/"],
    permissions=[
        FilesystemPermission(
            operations=["write"],
            paths=["/skills/approved/**"],
            mode="deny",
        ),
    ],
    store=store,
)
# :snippet-end:

# :remove-start:
assert agent is not None
assert create_agent_for_user("engineering") is not None
print("✓ Skills samples validated")
raise SystemExit(0)
# :remove-end:

# :snippet-start: skills-invoke-py
result = agent.invoke(
    {"messages": [{"role": "user", "content": "What is LangGraph?"}]},
    config={"configurable": {"thread_id": "1"}},
)
# :snippet-end:

# :snippet-start: skills-reload-invoke-py
config = {"configurable": {"thread_id": "1"}}

result = agent.invoke(
    {
        "messages": [{"role": "user", "content": "What is LangGraph?"}],
        "skills_metadata": None,
    },
    config=config,
)
# :snippet-end:

# :snippet-start: skills-reload-update-state-py
agent.update_state(config, {"skills_metadata": None})
# :snippet-end:


# :remove-start:
def agent_edited_skills(state: Any) -> bool:
    """Stand-in for your own check, such as scanning the run for writes under a skill source."""
    return False


# :remove-end:
# :snippet-start: skills-reload-middleware-py
from typing import Any

from deepagents.middleware import SkillsState
from langchain.agents.middleware import AgentMiddleware


class ReloadEditedSkills(AgentMiddleware[SkillsState]):
    """Reload skills on the next run when the agent edited one."""

    state_schema = SkillsState

    def after_agent(self, state: SkillsState, runtime) -> dict[str, Any] | None:
        if not agent_edited_skills(state):
            return None
        return {"skills_metadata": None}
# :snippet-end:
