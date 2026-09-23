"""Customization: wiring skills with different backends."""

# :snippet-start: skills-usage-state-py
from urllib.request import urlopen
from deepagents import create_deep_agent
from deepagents.backends import StateBackend
from deepagents.backends.utils import create_file_data
from langgraph.checkpoint.memory import MemorySaver

checkpointer = MemorySaver()
backend = StateBackend()

skill_url = "https://raw.githubusercontent.com/langchain-ai/deepagents/refs/heads/main/libs/code/examples/skills/langgraph-docs/SKILL.md"
with urlopen(skill_url) as response:
    skill_content = response.read().decode('utf-8')

skills_files = {
    "/skills/langgraph-docs/SKILL.md": create_file_data(skill_content),
}

agent = create_deep_agent(
    model="anthropic:claude-sonnet-4-6",
    backend=backend,
    skills=["/skills/"],
    checkpointer=checkpointer,
)

result = agent.invoke(
    {
        "messages": [{"role": "user", "content": "What is langgraph?"}],
        # Seed the default StateBackend's in-state filesystem (virtual paths must start with "/").
        "files": skills_files,
    },
    config={"configurable": {"thread_id": "12345"}},
)
# :snippet-end:
assert result is not None

# :snippet-start: skills-usage-store-py
from urllib.request import urlopen
from deepagents import create_deep_agent
from deepagents.backends import StoreBackend
from langgraph.store.memory import InMemoryStore

store = InMemoryStore()
backend = StoreBackend(
    namespace=lambda _rt: ("filesystem",),
    store=store,
)

skill_url = "https://raw.githubusercontent.com/langchain-ai/deepagents/refs/heads/main/libs/code/examples/skills/langgraph-docs/SKILL.md"
with urlopen(skill_url) as response:
    skill_content = response.read().decode('utf-8')

backend.upload_files(
    [("/skills/langgraph-docs/SKILL.md", skill_content.encode("utf-8"))]
)

# KEEP MODEL
agent = create_deep_agent(
    model="google_genai:gemini-3.6-flash",
    backend=backend,
    store=store,
    skills=["/skills/"],
)

result = agent.invoke(
    {"messages": [{"role": "user", "content": "What is langgraph?"}]},
    config={"configurable": {"thread_id": "12345"}},
)
# :snippet-end:

from pathlib import Path
# :snippet-start: skills-usage-filesystem-py
from urllib.request import urlopen
from deepagents import create_deep_agent
from deepagents.backends.filesystem import FilesystemBackend
from langgraph.checkpoint.memory import MemorySaver

# Checkpointer is REQUIRED for human-in-the-loop
checkpointer = MemorySaver()

skill_url = "https://raw.githubusercontent.com/langchain-ai/deepagents/refs/heads/main/libs/code/examples/skills/langgraph-docs/SKILL.md"
with urlopen(skill_url) as response:
    skill_content = response.read().decode('utf-8')

backend = FilesystemBackend(root_dir="/Users/user/{project}", virtual_mode=True)
# :remove-start:
# Test harness: make test-code-samples runs from the repo root.
example_dir = (Path.cwd() / "src/code-samples/deepagents").resolve()
backend = FilesystemBackend(root_dir=str(example_dir), virtual_mode=True)
# :remove-end:
backend.upload_files(
    [("/skills/langgraph-docs/SKILL.md", skill_content.encode("utf-8"))]
)

# KEEP MODEL
agent = create_deep_agent(
    model="google_genai:gemini-3.6-flash",
    backend=backend,
    skills=["/skills/"],
    interrupt_on={
        "write_file": True,
        "read_file": False,
        "edit_file": True,
    },
    checkpointer=checkpointer,  # Required for filesystem operations!
)

result = agent.invoke(
    {"messages": [{"role": "user", "content": "What is langgraph?"}]},
    config={"configurable": {"thread_id": "12345"}},
)
# :snippet-end:

# :remove-start:
assert agent is not None
# :remove-end:
