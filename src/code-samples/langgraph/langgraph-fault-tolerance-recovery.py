# :snippet-start: langgraph-fault-tolerance-llm-recoverable-py
from typing import Literal

from langgraph.types import Command
from typing_extensions import TypedDict


class ToolError(Exception):
    """Raised when a tool call fails in a way the model can correct."""


class State(TypedDict):
    tool_call: str
    tool_result: str | None


def run_tool(tool_call: str) -> str:
    if tool_call == "bad":
        raise ToolError("invalid args")
    return f"ok:{tool_call}"


def execute_tool(state: State) -> Command[Literal["agent", "execute_tool"]]:
    try:
        result = run_tool(state["tool_call"])
        return Command(update={"tool_result": result}, goto="agent")
    except ToolError as e:
        # Let the LLM see what went wrong and try again
        return Command(
            update={"tool_result": f"Tool error: {e}"},
            goto="agent",
        )


# :snippet-end:

# :remove-start:
cmd = execute_tool({"tool_call": "bad", "tool_result": None})
assert cmd.goto == "agent"
assert cmd.update == {"tool_result": "Tool error: invalid args"}
cmd_ok = execute_tool({"tool_call": "search", "tool_result": None})
assert cmd_ok.goto == "agent"
assert cmd_ok.update == {"tool_result": "ok:search"}
print("✓ langgraph-fault-tolerance-llm-recoverable-py validated")
# :remove-end:

# :snippet-start: langgraph-fault-tolerance-unexpected-py
from typing_extensions import TypedDict


class EmailAgentState(TypedDict):
    draft_response: str


class EmailService:
    def send(self, body: str) -> None:
        raise RuntimeError(f"SMTP unavailable while sending: {body}")


email_service = EmailService()


def send_reply(state: EmailAgentState) -> EmailAgentState:
    # Do not catch unexpected failures here. Let them bubble up and fail the run.
    email_service.send(state["draft_response"])
    return state


# :snippet-end:

# :remove-start:
from langgraph.graph import END, START, StateGraph

graph = (
    StateGraph(EmailAgentState)
    .add_node("send_reply", send_reply)
    .add_edge(START, "send_reply")
    .add_edge("send_reply", END)
    .compile()
)

try:
    graph.invoke({"draft_response": "Thanks for your email."})
except RuntimeError as exc:
    assert "SMTP unavailable" in str(exc)
else:
    raise AssertionError("expected RuntimeError to bubble up")
print("✓ langgraph-fault-tolerance-unexpected-py validated")
# :remove-end:
