"""Customization: memory configuration examples (StateBackend, StoreBackend, FilesystemBackend)."""

# :snippet-start: customization-memory-state-py
from urllib.request import urlopen

from deepagents import create_deep_agent
from deepagents.backends.utils import create_file_data
from langgraph.checkpoint.memory import MemorySaver

with urlopen(
    "https://raw.githubusercontent.com/langchain-ai/deepagents/refs/heads/main/examples/text-to-sql-agent/AGENTS.md"
) as response:
    agents_md = response.read().decode("utf-8")
checkpointer = MemorySaver()

agent = create_deep_agent(
    model="anthropic:claude-sonnet-4-6",
    memory=[
        "/AGENTS.md"
    ],
    checkpointer=checkpointer,
)

result = agent.invoke(
    {
        "messages": [
            {
                "role": "user",
                "content": "Please tell me what's in your memory files.",
            }
        ],
        # Seed the default StateBackend's in-state filesystem (virtual paths must start with "/").
        "files": {"/AGENTS.md": create_file_data(agents_md)},
    },
    config={"configurable": {"thread_id": "123456"}},
)
# :snippet-end:

# :remove-start:
assert result is not None
# :remove-end:

# :snippet-start: customization-memory-store-py
from urllib.request import urlopen

from deepagents import create_deep_agent
from deepagents.backends import StoreBackend
from deepagents.backends.utils import create_file_data
from langgraph.store.memory import InMemoryStore

with urlopen(
    "https://raw.githubusercontent.com/langchain-ai/deepagents/refs/heads/main/examples/text-to-sql-agent/AGENTS.md"
) as response:
    agents_md = response.read().decode("utf-8")

# Create the store and add the file to it
store = InMemoryStore()
file_data = create_file_data(agents_md)
store.put(
    namespace=("filesystem",),
    key="/AGENTS.md",
    value=file_data,
)

agent = create_deep_agent(
    model="anthropic:claude-sonnet-4-6",
    backend=StoreBackend(),
    store=store,
    memory=["/AGENTS.md"],
)

result = agent.invoke(
    {
        "messages": [
            {
                "role": "user",
                "content": "Please tell me what's in your memory files.",
            }
        ],
        "files": {"/AGENTS.md": create_file_data(agents_md)},
    },
    config={"configurable": {"thread_id": "12345"}},
)
# :snippet-end:

# :remove-start:
assert result is not None
# :remove-end:

# :snippet-start: customization-memory-filesystem-py
from deepagents import create_deep_agent
from deepagents.backends import FilesystemBackend
from langgraph.checkpoint.memory import MemorySaver

# Checkpointer is REQUIRED for human-in-the-loop
checkpointer = MemorySaver()

agent = create_deep_agent(
    model="anthropic:claude-sonnet-4-6",
    backend=FilesystemBackend(root_dir="/Users/user/{project}"),
    memory=[
        "./AGENTS.md"
    ],
    interrupt_on={
        "write_file": True,  # Default: approve, edit, reject
        "read_file": False,  # No interrupts needed
        "edit_file": True,   # Default: approve, edit, reject
    },
    checkpointer=checkpointer,  # Required!
)
# :snippet-end:

# :remove-start:
assert agent is not None
# :remove-end:
