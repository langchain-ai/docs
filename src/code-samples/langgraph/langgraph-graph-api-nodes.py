# :remove-start:
import asyncio
import contextlib
import io
import os

# Constructing chat models needs a credential even though no request is sent.
os.environ.setdefault("ANTHROPIC_API_KEY", "test-key")
os.environ.setdefault("OPENAI_API_KEY", "test-key")
# :remove-end:

# :snippet-start: langgraph-graph-api-nodes-runtime-config-py
from langgraph.graph import END, StateGraph, START
from langgraph.runtime import Runtime
from typing_extensions import TypedDict

# 1. Specify config schema
class ContextSchema(TypedDict):
    my_runtime_value: str

# 2. Define a graph that accesses the config in a node
class State(TypedDict):
    my_state_value: int

def node(state: State, runtime: Runtime[ContextSchema]):  # [!code highlight]
    if runtime.context["my_runtime_value"] == "a":  # [!code highlight]
        return {"my_state_value": 1}
    elif runtime.context["my_runtime_value"] == "b":  # [!code highlight]
        return {"my_state_value": 2}
    else:
        raise ValueError("Unknown values.")

builder = StateGraph(State, context_schema=ContextSchema)  # [!code highlight]
builder.add_node(node)
builder.add_edge(START, "node")
builder.add_edge("node", END)

graph = builder.compile()

# 3. Pass in configuration at runtime:
print(graph.invoke({}, context={"my_runtime_value": "a"}))  # [!code highlight]
print(graph.invoke({}, context={"my_runtime_value": "b"}))  # [!code highlight]
# :snippet-end:

# :remove-start:
assert graph.invoke({}, context={"my_runtime_value": "a"}) == {"my_state_value": 1}
assert graph.invoke({}, context={"my_runtime_value": "b"}) == {"my_state_value": 2}
print("✓ langgraph-graph-api-nodes-runtime-config-py validated")
# :remove-end:

# :remove-start:
# Context for the snippet below, which shows only the `add_node` call.
from typing_extensions import TypedDict

from langgraph.graph import END, START, StateGraph


class State(TypedDict):
    count: int


retry_default_calls = 0


def node_function(state: State):
    global retry_default_calls
    retry_default_calls += 1
    if retry_default_calls == 1:
        msg = "transient failure"
        raise _TransientError(msg)
    return {"count": retry_default_calls}


class _TransientError(Exception):
    """Not in the default non-retryable list, so the default policy retries it."""


builder = StateGraph(State)
# :remove-end:

# :snippet-start: langgraph-graph-api-nodes-retry-default-py
from langgraph.types import RetryPolicy

builder.add_node(
    "node_name",
    node_function,
    retry_policy=RetryPolicy(),
)
# :snippet-end:

# :remove-start:
builder.add_edge(START, "node_name")
builder.add_edge("node_name", END)
graph = builder.compile()
assert graph.invoke({"count": 0}) == {"count": 2}
assert retry_default_calls == 2
print("✓ langgraph-graph-api-nodes-retry-default-py validated")
# :remove-end:

# :snippet-start: langgraph-graph-api-nodes-retry-custom-py
import sqlite3
from langchain.chat_models import init_chat_model
from langgraph.graph import END, MessagesState, StateGraph, START
from langgraph.types import RetryPolicy
from langchain.messages import AIMessage

con = sqlite3.connect(":memory:")
model = init_chat_model("claude-haiku-4-5-20251001")

def query_database(state: MessagesState):
    cursor = con.cursor()
    cursor.execute("SELECT * FROM Artist LIMIT 10;")
    query_result = str(cursor.fetchall())
    return {"messages": [AIMessage(content=query_result)]}

def call_model(state: MessagesState):
    response = model.invoke(state["messages"])
    return {"messages": [response]}

# Define a new graph
builder = StateGraph(MessagesState)
builder.add_node(
    "query_database",
    query_database,
    retry_policy=RetryPolicy(retry_on=sqlite3.OperationalError),
)
builder.add_node("model", call_model, retry_policy=RetryPolicy(max_attempts=5))
builder.add_edge(START, "model")
builder.add_edge("model", "query_database")
builder.add_edge("query_database", END)
graph = builder.compile()
# :snippet-end:

# :remove-start:
# Construction only: do not invoke the graph, which would call the model.
assert {"model", "query_database"} <= set(graph.nodes)
print("✓ langgraph-graph-api-nodes-retry-custom-py validated")
# :remove-end:

# :snippet-start: langgraph-graph-api-nodes-timeout-py
import asyncio
from typing_extensions import TypedDict

from langgraph.errors import NodeTimeoutError
from langgraph.graph import END, START, StateGraph


class State(TypedDict):
    value: str


async def call_model(state: State) -> State:
    await asyncio.sleep(2)
    return {"value": "done"}


builder = StateGraph(State)
builder.add_node("model", call_model, timeout=1.0)
# Or: timeout=TimeoutPolicy(run_timeout=120, idle_timeout=30)
builder.add_edge(START, "model")
builder.add_edge("model", END)
graph = builder.compile()


async def main():
    try:
        await graph.ainvoke({"value": "start"})
    except NodeTimeoutError:
        print("Node timed out")


asyncio.run(main())
# :snippet-end:

# :remove-start:
async def _check_timeout() -> bool:
    try:
        await graph.ainvoke({"value": "start"})
    except NodeTimeoutError:
        return True
    return False


assert asyncio.run(_check_timeout())
print("✓ langgraph-graph-api-nodes-timeout-py validated")
# :remove-end:

# :remove-start:
# Context for the snippet below, which shows only the `add_node` call.
from typing_extensions import TypedDict

from langgraph.graph import START, StateGraph


class State(TypedDict):
    status: str


def charge_payment(state: State):
    msg = "payment gateway timeout"
    raise ConnectionError(msg)


def finalize(state: State):
    return {}


builder = StateGraph(State)
builder.add_node("finalize", finalize)
# :remove-end:

# :snippet-start: langgraph-graph-api-nodes-error-handler-py
from langgraph.errors import NodeError
from langgraph.types import Command, RetryPolicy

def payment_error_handler(state: State, error: NodeError) -> Command:
    return Command(
        update={"status": f"compensated: {error.error}"},
        goto="finalize",
    )

builder.add_node(
    "charge_payment",
    charge_payment,
    retry_policy=RetryPolicy(max_attempts=3, retry_on=ConnectionError),
    error_handler=payment_error_handler,
)
# :snippet-end:

# :remove-start:
builder.add_edge(START, "charge_payment")
graph = builder.compile()
result = graph.invoke({"status": "pending"})
assert result == {"status": "compensated: payment gateway timeout"}, result
print("✓ langgraph-graph-api-nodes-error-handler-py validated")
# :remove-end:

# :remove-start:
# Context for the snippet below. Node timeouts require async nodes, and the
# `timeout` default also applies to the error-handler node.
from typing_extensions import TypedDict

from langgraph.errors import NodeError
from langgraph.graph import StateGraph, START
from langgraph.types import Command


class State(TypedDict):
    result: str


async def node_a(state: State):
    return {"result": "a"}


async def node_b(state: State):
    return {"result": "b"}


async def fallback_handler(state: State, error: NodeError) -> Command:
    return Command(update={"result": "fallback"})
# :remove-end:

# :snippet-start: langgraph-graph-api-nodes-node-defaults-py
from langgraph.types import RetryPolicy, TimeoutPolicy

graph = (
    StateGraph(State)
    .set_node_defaults(
        retry_policy=RetryPolicy(max_attempts=3),
        timeout=TimeoutPolicy(run_timeout=30),
        error_handler=fallback_handler,
    )
    .add_node("a", node_a)
    .add_node("b", node_b, retry_policy=RetryPolicy(max_attempts=5))  # overrides default
    .add_edge(START, "a")
    .compile()
)
# :snippet-end:

# :remove-start:
assert {"a", "b"} <= set(graph.nodes)
assert asyncio.run(graph.ainvoke({"result": ""})) == {"result": "a"}
print("✓ langgraph-graph-api-nodes-node-defaults-py validated")
# :remove-end:

# :snippet-start: langgraph-graph-api-nodes-execution-info-ids-py
from langgraph.graph import StateGraph, START, END
from langgraph.runtime import Runtime
from typing_extensions import TypedDict

class State(TypedDict):
    result: str

def my_node(state: State, runtime: Runtime):
    info = runtime.execution_info
    if info is None:
        return {"result": "done"}
    print(f"Thread: {info.thread_id}, Run: {info.run_id}")  # [!code highlight]
    return {"result": "done"}

builder = StateGraph(State)
builder.add_node("my_node", my_node)
builder.add_edge(START, "my_node")
builder.add_edge("my_node", END)
graph = builder.compile()
# :snippet-end:

# :remove-start:
_buffer = io.StringIO()
with contextlib.redirect_stdout(_buffer):
    assert graph.invoke({"result": ""}) == {"result": "done"}
assert "Thread:" in _buffer.getvalue()
print("✓ langgraph-graph-api-nodes-execution-info-ids-py validated")
# :remove-end:

# :remove-start:
# Context for the snippet below. The primary call fails once, so the retry
# runs the node a second time with `node_attempt == 2`.
primary_calls = 0


class _PrimaryUnavailableError(Exception):
    """Not in the default non-retryable list, so the default policy retries it."""


def call_primary_api() -> str:
    global primary_calls
    primary_calls += 1
    msg = "primary unavailable"
    raise _PrimaryUnavailableError(msg)


def call_fallback_api() -> str:
    return "fallback"
# :remove-end:

# :snippet-start: langgraph-graph-api-nodes-execution-info-retry-py
from langgraph.graph import StateGraph, START, END
from langgraph.runtime import Runtime
from langgraph.types import RetryPolicy
from typing_extensions import TypedDict

class State(TypedDict):
    result: str

def my_node(state: State, runtime: Runtime):
    info = runtime.execution_info
    if info is not None and info.node_attempt > 1:  # [!code highlight]
        # use a fallback on retries
        return {"result": call_fallback_api()}
    return {"result": call_primary_api()}

builder = StateGraph(State)
builder.add_node("my_node", my_node, retry_policy=RetryPolicy(max_attempts=3))
builder.add_edge(START, "my_node")
builder.add_edge("my_node", END)
graph = builder.compile()
# :snippet-end:

# :remove-start:
assert graph.invoke({"result": ""}) == {"result": "fallback"}
assert primary_calls == 1
print("✓ langgraph-graph-api-nodes-execution-info-retry-py validated")
# :remove-end:

# :snippet-start: langgraph-graph-api-nodes-server-info-py
from langgraph.graph import StateGraph, START, END
from langgraph.runtime import Runtime
from typing_extensions import TypedDict

class State(TypedDict):
    result: str

def my_node(state: State, runtime: Runtime):
    server = runtime.server_info
    if server is not None:
        print(f"Assistant: {server.assistant_id}, Graph: {server.graph_id}")  # [!code highlight]
        if server.user is not None:
            print(f"User: {server.user.identity}")
    return {"result": "done"}

builder = StateGraph(State)
builder.add_node("my_node", my_node)
builder.add_edge(START, "my_node")
builder.add_edge("my_node", END)
graph = builder.compile()
# :snippet-end:

# :remove-start:
# `server_info` is None outside LangGraph Server, so the node skips the prints.
assert graph.invoke({"result": ""}) == {"result": "done"}
print("✓ langgraph-graph-api-nodes-server-info-py validated")
# :remove-end:

# :remove-start:
# Context for the snippet below.
from typing_extensions import TypedDict


class State(TypedDict, total=False):
    status: str
    reason: str | None


def do_work() -> str:
    return "done"
# :remove-end:

# :snippet-start: langgraph-graph-api-nodes-drain-py
from langgraph.runtime import Runtime

def my_node(state: State, runtime: Runtime) -> State:
    if runtime.drain_requested:  # [!code highlight]
        return {"status": "skipped", "reason": runtime.drain_reason}
    return {"status": do_work()}
# :snippet-end:

# :remove-start:
from langgraph.runtime import RunControl

assert my_node({}, Runtime()) == {"status": "done"}
_control = RunControl()
_control.request_drain("shutdown")
assert my_node({}, Runtime(control=_control)) == {
    "status": "skipped",
    "reason": "shutdown",
}
print("✓ langgraph-graph-api-nodes-drain-py validated")
# :remove-end:

# :snippet-start: langgraph-graph-api-nodes-cache-py
import time

from typing_extensions import TypedDict

from langgraph.cache.memory import InMemoryCache
from langgraph.graph import END, START, StateGraph
from langgraph.types import CachePolicy


class State(TypedDict):
    x: int
    result: int


def expensive_node(state: State) -> dict[str, int]:
    # Expensive computation
    time.sleep(2)
    return {"result": state["x"] * 2}


builder = StateGraph(State)
builder.add_node("expensive_node", expensive_node, cache_policy=CachePolicy(ttl=3))
builder.add_edge(START, "expensive_node")
builder.add_edge("expensive_node", END)

graph = builder.compile(cache=InMemoryCache())

print(graph.invoke({"x": 5}, stream_mode="updates"))  # [!code highlight]
# [{'expensive_node': {'result': 10}}]
print(graph.invoke({"x": 5}, stream_mode="updates"))  # [!code highlight]
# [{'expensive_node': {'result': 10}, '__metadata__': {'cached': True}}]
# :snippet-end:

# :remove-start:
_cached = graph.invoke({"x": 5}, stream_mode="updates")
assert _cached == [
    {"expensive_node": {"result": 10}, "__metadata__": {"cached": True}}
], _cached
print("✓ langgraph-graph-api-nodes-cache-py validated")
# :remove-end:
