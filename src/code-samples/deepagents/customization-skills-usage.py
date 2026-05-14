"""Customization: wiring skills with different backends."""

# :snippet-start: skills-usage-state-py
from pathlib import Path

from deepagents import create_deep_agent
from deepagents.backends import StateBackend
from deepagents.backends.utils import create_file_data
from langchain_quickjs import CodeInterpreterMiddleware
from langgraph.checkpoint.memory import MemorySaver

checkpointer = MemorySaver()
backend = StateBackend()

skill_path = Path(__file__).resolve().parent / "skills/write-timestamp/SKILL.md"
skill_content = skill_path.read_text(encoding="utf-8")

skills_files = {
    "/skills/write-timestamp/SKILL.md": create_file_data(skill_content),
}

agent = create_deep_agent(
    model="anthropic:claude-sonnet-4-6",
    backend=backend,
    skills=["/skills/"],
    checkpointer=checkpointer,
    middleware=[CodeInterpreterMiddleware(skills_backend=backend)],
)

result = agent.invoke(
    {
        "messages": [{"role": "user", "content": "What is langgraph?"}],
        "files": skills_files,
    },
    config={"configurable": {"thread_id": "12345"}},
)
# :snippet-end:
assert result is not None

# :snippet-start: skills-usage-store-py
from pathlib import Path

from deepagents import create_deep_agent
from deepagents.backends import StoreBackend
from deepagents.backends.utils import create_file_data
from langchain_quickjs import CodeInterpreterMiddleware
from langgraph.store.memory import InMemoryStore

store = InMemoryStore()
backend = StoreBackend()

skill_path = Path(__file__).resolve().parent / "skills/write-timestamp/SKILL.md"
skill_content = skill_path.read_text(encoding="utf-8")

store.put(
    namespace=("filesystem",),
    key="/skills/write-timestamp/SKILL.md",
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

# Example invocation (requires LLM credentials):
# result = agent.invoke(
#     {"messages": [{"role": "user", "content": "What is langgraph?"}]},
#     config={"configurable": {"thread_id": "12345"}},
# )
# :snippet-end:

# :snippet-start: skills-usage-filesystem-py
import tempfile
from pathlib import Path

from deepagents import create_deep_agent
from deepagents.backends.filesystem import FilesystemBackend
from langchain_quickjs import CodeInterpreterMiddleware
from langgraph.checkpoint.memory import MemorySaver

checkpointer = MemorySaver()
root_dir = tempfile.mkdtemp(prefix="deepagents-skills-")
backend = FilesystemBackend(root_dir=root_dir, virtual_mode=True)

skills_root = Path(root_dir) / "skills" / "write-timestamp"
skills_root.mkdir(parents=True)
skill_src = Path(__file__).resolve().parent / "skills/write-timestamp/SKILL.md"
skills_root.joinpath("SKILL.md").write_text(skill_src.read_text(encoding="utf-8"), encoding="utf-8")

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
    checkpointer=checkpointer,
    middleware=[CodeInterpreterMiddleware(skills_backend=backend)],
)

# Example invocation (requires LLM credentials):
# result = agent.invoke(
#     {"messages": [{"role": "user", "content": "What is langgraph?"}]},
#     config={"configurable": {"thread_id": "12345"}},
# )
# :snippet-end:

# :remove-start:
assert agent is not None
# :remove-end:
