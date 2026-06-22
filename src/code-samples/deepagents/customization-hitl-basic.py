"""Customization: human-in-the-loop interrupt_on example."""

# :snippet-start: hitl-basic-config-py
from langchain.tools import tool
from deepagents import create_deep_agent
from langgraph.checkpoint.memory import MemorySaver


@tool
def remove_file(path: str) -> str:
    """Delete a file from the filesystem."""
    return f"Deleted {path}"


@tool
def fetch_file(path: str) -> str:
    """Read a file from the filesystem."""
    return f"Contents of {path}"


@tool
def notify_email(to: str, subject: str, body: str) -> str:
    """Send an email."""
    return f"Sent email to {to}"


# Checkpointer is REQUIRED for human-in-the-loop
checkpointer = MemorySaver()

agent = create_deep_agent(
    model="google_genai:gemini-3.5-flash",
    tools=[remove_file, fetch_file, notify_email],
    interrupt_on={
        "remove_file": True,  # Default: approve, edit, reject, respond
        "fetch_file": False,  # No interrupts needed
        "notify_email": {"allowed_decisions": ["approve", "reject"]},  # No editing
    },
    checkpointer=checkpointer,  # Required!
)
# :snippet-end:

# :snippet-start: hitl-conditional-interrupts-py
from deepagents import create_deep_agent
from langchain.agents.middleware import ToolCallRequest
from langgraph.checkpoint.memory import MemorySaver


def writes_outside_workspace(request: ToolCallRequest) -> bool:
    """Pause writes to paths outside the workspace directory."""
    path = request.tool_call["args"].get("file_path", "")
    return not path.startswith("/workspace/")


agent = create_deep_agent(
    model="openai:gpt-5.5",
    interrupt_on={
        "write_file": {
            "allowed_decisions": ["approve", "edit", "reject"],
            "when": writes_outside_workspace,
        },
    },
    checkpointer=MemorySaver(),
)
# :snippet-end:

# :remove-start:
assert agent is not None

inside_workspace = ToolCallRequest(
    tool_call={
        "id": "1",
        "name": "write_file",
        "args": {"file_path": "/workspace/notes.txt"},
    },
    tool=object(),
    state={},
    runtime={},
)
outside_workspace = ToolCallRequest(
    tool_call={
        "id": "2",
        "name": "write_file",
        "args": {"file_path": "/tmp/notes.txt"},
    },
    tool=object(),
    state={},
    runtime={},
)
assert writes_outside_workspace(inside_workspace) is False
assert writes_outside_workspace(outside_workspace) is True
# :remove-end:
