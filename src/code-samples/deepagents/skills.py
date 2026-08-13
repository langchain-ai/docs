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
    "engineering": ["/skills/code-review/", "/skills/testing/", "/skills/deployment/"],
    "data": ["/skills/sql-analysis/", "/skills/visualization/", "/skills/data-pipeline/"],
    "support": ["/skills/ticket-triage/", "/skills/runbook/"],
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
    "skills": ["/skills/research/", "/skills/web-search/"],  # Subagent-specific skills
}

# KEEP MODEL
agent = create_deep_agent(
    model="google_genai:gemini-3.5-flash",
    skills=["/skills/main/"],  # Main agent and GP subagent get these
    subagents=[research_subagent],  # Researcher gets only its own skills
)
# :snippet-end:

# :snippet-start: skills-approval-py
from deepagents import FilesystemPermission, create_deep_agent
from langgraph.checkpoint.memory import MemorySaver

# KEEP MODEL
agent = create_deep_agent(
    model="anthropic:claude-sonnet-4-6",
    skills=["/skills/personal/"],
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

# :snippet-start: skills-personal-writable-py
from deepagents import FilesystemPermission, create_deep_agent
from deepagents.backends import CompositeBackend, StateBackend, StoreBackend

# KEEP MODEL
agent = create_deep_agent(
    model="anthropic:claude-sonnet-4-6",
    backend=CompositeBackend(
        default=StateBackend(),
        routes={
            "/skills/shared/": StoreBackend(
                namespace=lambda rt: ("curated-skills", rt.context.org_id),
            ),
            "/skills/personal/": StoreBackend(
                namespace=lambda rt: (
                    "user-skills",
                    rt.server_info.user.identity,
                ),
            ),
        },
    ),
    skills=["/skills/shared/", "/skills/personal/"],
    permissions=[
        FilesystemPermission(
            operations=["write"],
            paths=["/skills/shared/**"],
            mode="deny",
        ),
    ],
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
