"""Human-in-the-loop: per-call interrupts."""

# :remove-start:
import os

os.environ.setdefault("OPENAI_API_KEY", "sk-test-key")
# :remove-end:

# :snippet-start: hitl-per-call-agent-py
from langchain.agents import create_agent
from langchain.agents.middleware import HumanInTheLoopMiddleware
from langchain.tools import tool
from langgraph.checkpoint.memory import InMemorySaver


@tool
def write_file(path: str, content: str) -> str:
    """Write content to a file."""
    return f"Wrote {len(content)} characters to {path}"


@tool
def execute_sql(query: str) -> str:
    """Run a SQL query."""
    return "Deleted 42 rows"


@tool
def read_data(table: str) -> str:
    """Read rows from a table."""
    return f"3 rows from {table}"


agent = create_agent(
    model="gpt-5.5",
    tools=[write_file, execute_sql, read_data],
    middleware=[
        HumanInTheLoopMiddleware(
            interrupt_on={
                "write_file": True,
                "execute_sql": {"allowed_decisions": ["approve", "reject"]},
                "read_data": False,
            },
            interrupt_mode="per_call",  # [!code highlight]
        ),
    ],
    checkpointer=InMemorySaver(),
)
# :snippet-end:

# :remove-start:
import json
from itertools import cycle

from langchain.messages import AIMessage, AIMessageChunk
from langchain_core.language_models.fake_chat_models import GenericFakeChatModel
from langchain_core.outputs import ChatGenerationChunk


class _ScriptedModel(GenericFakeChatModel):
    """Asks for all three tools in one turn, then answers."""

    def bind_tools(self, tools, **kwargs):
        return self

    def _stream(self, messages, stop=None, run_manager=None, **kwargs):
        message = next(self.messages)
        chunks = [
            {"name": c["name"], "args": json.dumps(c["args"]), "id": c["id"], "index": i}
            for i, c in enumerate(message.tool_calls)
        ]
        chunk = AIMessageChunk(content=message.content, tool_call_chunks=chunks)
        yield ChatGenerationChunk(message=chunk)


_TOOL_CALLS = AIMessage(
    content="",
    tool_calls=[
        {
            "name": "write_file",
            "args": {"path": "orders_archive.csv", "content": "id,total\n1,20\n"},
            "id": "call_write",
        },
        {
            "name": "execute_sql",
            "args": {"query": "DELETE FROM orders WHERE created_at < '2025-01-01'"},
            "id": "call_sql",
        },
        {"name": "read_data", "args": {"table": "orders"}, "id": "call_read"},
    ],
)

agent = create_agent(
    model=_ScriptedModel(messages=cycle([_TOOL_CALLS, AIMessage(content="Done.")])),
    tools=[write_file, execute_sql, read_data],
    middleware=[
        HumanInTheLoopMiddleware(
            interrupt_on={
                "write_file": True,
                "execute_sql": {"allowed_decisions": ["approve", "reject"]},
                "read_data": False,
            },
            interrupt_mode="per_call",
        ),
    ],
    checkpointer=InMemorySaver(),
)


def _tool_results(state) -> dict[str, tuple[str, str]]:
    return {m.name: (m.status, m.content) for m in state["messages"] if m.type == "tool"}


# :remove-end:

# :snippet-start: hitl-per-call-invoke-py
config = {"configurable": {"thread_id": "1"}}
result = agent.invoke(
    {"messages": [{"role": "user", "content": "Archive old orders, then delete them."}]},
    config=config,
    version="v2",
)

# One interrupt per gated tool call, in no fixed order
for interrupt in result.interrupts:
    print(interrupt.value)
# > {'type': 'tool_approval', 'tool_call_id': 'call_write', 'name': 'write_file', 'args': {'path': 'orders_archive.csv', 'content': 'id,total\n1,20\n'}, 'description': "Tool execution requires approval\n\nTool: write_file\nArgs: {'path': 'orders_archive.csv', 'content': 'id,total\\n1,20\\n'}"}
# > {'type': 'tool_approval', 'tool_call_id': 'call_sql', 'name': 'execute_sql', 'args': {'query': "DELETE FROM orders WHERE created_at < '2025-01-01'"}, 'description': 'Tool execution requires approval\n\nTool: execute_sql\nArgs: {\'query\': "DELETE FROM orders WHERE created_at < \'2025-01-01\'"}'}
# :snippet-end:

# :remove-start:
assert sorted((i.value for i in result.interrupts), key=lambda v: v["name"], reverse=True) == [
    {
        "type": "tool_approval",
        "tool_call_id": "call_write",
        "name": "write_file",
        "args": {"path": "orders_archive.csv", "content": "id,total\n1,20\n"},
        "description": "Tool execution requires approval\n\nTool: write_file\nArgs: {'path': 'orders_archive.csv', 'content': 'id,total\\n1,20\\n'}",
    },
    {
        "type": "tool_approval",
        "tool_call_id": "call_sql",
        "name": "execute_sql",
        "args": {"query": "DELETE FROM orders WHERE created_at < '2025-01-01'"},
        "description": "Tool execution requires approval\n\nTool: execute_sql\nArgs: {'query': \"DELETE FROM orders WHERE created_at < '2025-01-01'\"}",
    },
]
# `read_data` isn't gated, so it ran without waiting for the review.
assert _tool_results(result.value) == {"read_data": ("success", "3 rows from orders")}
# One branch per allowed decision, matched on `type`.
schemas = {i.value["name"]: i.response_schema for i in result.interrupts}
assert schemas["write_file"]["discriminator"]["propertyName"] == "type"
assert sorted(schemas["write_file"]["discriminator"]["mapping"]) == [
    "approve",
    "edit",
    "reject",
    "respond",
]
assert sorted(schemas["execute_sql"]["discriminator"]["mapping"]) == ["approve", "reject"]
# :remove-end:

# :snippet-start: hitl-per-call-resume-py
from langgraph.types import Command

decisions = {}
for interrupt in result.interrupts:
    if interrupt.value["name"] == "execute_sql":
        decisions[interrupt.id] = {
            "type": "reject",
            "message": "Archive the rows before deleting them.",
        }
    else:
        decisions[interrupt.id] = {"type": "approve"}

result = agent.invoke(Command(resume=decisions), config=config, version="v2")
# :snippet-end:

# :remove-start:
assert not result.interrupts
assert _tool_results(result.value) == {
    "read_data": ("success", "3 rows from orders"),
    "write_file": ("success", "Wrote 14 characters to orders_archive.csv"),
    "execute_sql": (
        "error",
        "User rejected the tool call for `execute_sql` with reason: "
        "Archive the rows before deleting them.",
    ),
}

config = {"configurable": {"thread_id": "2"}}
result = agent.invoke(
    {"messages": [{"role": "user", "content": "Archive old orders, then delete them."}]},
    config=config,
    version="v2",
)
# :remove-end:

# :snippet-start: hitl-per-call-invalid-py
from pydantic import ValidationError

write_file_interrupt = next(
    interrupt for interrupt in result.interrupts if interrupt.value["name"] == "write_file"
)
edit = {
    "type": "edit",
    "edited_action": {"name": "write_file", "args": {"path": "archive/orders_2024.csv"}},
}

try:
    agent.invoke(Command(resume={write_file_interrupt.id: edit}), config=config, version="v2")
except ValidationError as error:
    for problem in error.errors():
        print(".".join(str(part) for part in problem["loc"]), problem["msg"])
# > edit.edited_action.args.content Field required

# Nothing was saved, so answer the same interrupt again
edit["edited_action"]["args"]["content"] = "id,total\n1,20\n"
result = agent.invoke(
    Command(resume={write_file_interrupt.id: edit}), config=config, version="v2"
)
# :snippet-end:

# :remove-start:
# The corrected edit ran; `execute_sql` is still waiting for its own answer.
assert [i.value["name"] for i in result.interrupts] == ["execute_sql"]
status, content = _tool_results(result.value)["write_file"]
assert status == "success"
assert content.endswith("Wrote 14 characters to archive/orders_2024.csv")
result = agent.invoke(
    Command(resume={result.interrupts[0].id: {"type": "approve"}}),
    config=config,
    version="v2",
)
assert _tool_results(result.value)["execute_sql"] == ("success", "Deleted 42 rows")

config = {"configurable": {"thread_id": "3"}}
stream = agent.stream_events(
    {"messages": [{"role": "user", "content": "Archive old orders, then delete them."}]},
    config=config,
    version="v3",
)
for message in stream.messages:
    for token in message.text:
        pass
assert stream.interrupted
# :remove-end:

# :snippet-start: hitl-per-call-stream-py
decisions = {interrupt.id: {"type": "approve"} for interrupt in stream.interrupts}
stream = agent.stream_events(Command(resume=decisions), config=config, version="v3")
for message in stream.messages:
    for token in message.text:
        print(token, end="", flush=True)
# :snippet-end:

# :remove-start:
assert not stream.interrupted
assert _tool_results(stream.output)["execute_sql"] == ("success", "Deleted 42 rows")
print("✓ per-call interrupts: invoke, resume by ID, invalid answer, streaming")
# :remove-end:
