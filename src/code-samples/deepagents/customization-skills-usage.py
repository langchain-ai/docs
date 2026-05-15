"""Customization: wiring skills with different backends."""

# :snippet-start: skills-usage-state-py
from urllib.request import urlopen
from deepagents import create_deep_agent
from deepagents.backends import StateBackend
from deepagents.backends.utils import create_file_data
from langchain_quickjs import CodeInterpreterMiddleware
from langgraph.checkpoint.memory import MemorySaver

checkpointer = MemorySaver()
backend = StateBackend()

skill_url = "https://raw.githubusercontent.com/langchain-ai/deepagents/refs/heads/main/libs/cli/examples/skills/langgraph-docs/SKILL.md"
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
    middleware=[CodeInterpreterMiddleware(skills_backend=backend)], # for interpreter skills
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
from deepagents.backends.utils import create_file_data
from langchain_quickjs import CodeInterpreterMiddleware
from langgraph.store.memory import InMemoryStore

store = InMemoryStore()
backend = StoreBackend(namespace=lambda _rt: ("filesystem",))

skill_url = "https://raw.githubusercontent.com/langchain-ai/deepagents/refs/heads/main/libs/cli/examples/skills/langgraph-docs/SKILL.md"
with urlopen(skill_url) as response:
    skill_content = response.read().decode('utf-8')

store.put(
    namespace=("filesystem",),
    key="/skills/langgraph-docs/SKILL.md",
    value=create_file_data(skill_content),
)

# KEEP MODEL
agent = create_deep_agent(
    model="google_genai:gemini-3.1-pro-preview",
    backend=backend,
    store=store,
    skills=["/skills/"],
    middleware=[CodeInterpreterMiddleware(skills_backend=backend)],
)

result = agent.invoke(
    {"messages": [{"role": "user", "content": "What is langgraph?"}]},
    config={"configurable": {"thread_id": "12345"}},
)
# :snippet-end:

from pathlib import Path
# :snippet-start: skills-usage-filesystem-py
from deepagents import create_deep_agent
from deepagents.backends.filesystem import FilesystemBackend
from langchain_quickjs import CodeInterpreterMiddleware
from langgraph.checkpoint.memory import MemorySaver

# Checkpointer is REQUIRED for human-in-the-loop
checkpointer = MemorySaver()
root_dir = "/Users/user/{project}"
backend = FilesystemBackend(root_dir=root_dir)
# :remove-start:
# Test harness: make test-code-samples runs from the repo root.
example_dir = (Path.cwd() / "src/code-samples/deepagents").resolve()
root_dir = str(example_dir)
backend = FilesystemBackend(root_dir=root_dir, virtual_mode=True)
# :remove-end:

# KEEP MODEL
agent = create_deep_agent(
    model="google_genai:gemini-3.1-pro-preview",
    backend=backend,
    skills=[str(Path(root_dir) / "skills")],
    interrupt_on={
        "write_file": True,
        "read_file": False,
        "edit_file": True,
    },
    checkpointer=checkpointer, # Required!
    middleware=[CodeInterpreterMiddleware(skills_backend=backend)], # for interpreter skills
)

result = agent.invoke(
    {"messages": [{"role": "user", "content": "What is langgraph?"}]},
    config={"configurable": {"thread_id": "12345"}},
)
# :snippet-end:

# :remove-start:
assert agent is not None
# :remove-end:
