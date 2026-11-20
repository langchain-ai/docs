# :snippet-start: langgraph-functional-api-overview-hello-py
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.func import entrypoint

checkpointer = InMemorySaver()


@entrypoint(checkpointer=checkpointer)
def my_workflow(name: str) -> str:
    return f"Hello, {name}"


config = {"configurable": {"thread_id": "1"}}
my_workflow.invoke("Alice", config)  # "Hello, Alice"
# :snippet-end:

# :remove-start:
assert my_workflow.invoke("Alice", config) == "Hello, Alice"
# :remove-end:

# :snippet-start: langgraph-functional-api-overview-hello-async-py
import asyncio

from langgraph.checkpoint.memory import InMemorySaver
from langgraph.func import entrypoint

checkpointer = InMemorySaver()


@entrypoint(checkpointer=checkpointer)
async def my_workflow(name: str) -> str:
    return f"Hello, {name}"


config = {"configurable": {"thread_id": "1"}}
asyncio.run(my_workflow.ainvoke("Alice", config))  # "Hello, Alice"
# :snippet-end:

# :remove-start:
import asyncio

assert asyncio.run(my_workflow.ainvoke("Alice", config)) == "Hello, Alice"
# :remove-end:

# :snippet-start: langgraph-functional-api-overview-task-py
from langgraph.func import task


@task
def slow_computation(input_value: int) -> int:
    # Long-running or side-effecting work
    return input_value * 2
# :snippet-end:

# :snippet-start: langgraph-functional-api-overview-task-exec-py
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.func import entrypoint, task

checkpointer = InMemorySaver()


@task
def slow_computation(input_value: int) -> int:
    return input_value * 2


@entrypoint(checkpointer=checkpointer)
def my_workflow(some_input: int) -> int:
    future = slow_computation(some_input)
    return future.result()
# :snippet-end:

# :remove-start:
assert my_workflow.invoke(3, {"configurable": {"thread_id": "1"}}) == 6
# :remove-end:

# :snippet-start: langgraph-functional-api-overview-task-exec-async-py
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.func import entrypoint, task

checkpointer = InMemorySaver()


@task
async def slow_computation(input_value: int) -> int:
    return input_value * 2


@entrypoint(checkpointer=checkpointer)
async def my_workflow(some_input: int) -> int:
    return await slow_computation(some_input)
# :snippet-end:

# :remove-start:
assert asyncio.run(my_workflow.ainvoke(3, {"configurable": {"thread_id": "1"}})) == 6
print("✓ langgraph-functional-api-overview")
# :remove-end:

# :snippet-start: langgraph-functional-api-overview-inject-py
from typing import Any

from langchain_core.runnables import RunnableConfig
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.func import entrypoint
from langgraph.runtime import Runtime
from langgraph.store.memory import InMemoryStore

checkpointer = InMemorySaver()
store = InMemoryStore()


@entrypoint(
    checkpointer=checkpointer,
    store=store,
)
def my_workflow(
    some_input: dict,  # The input (for example, passed via `invoke`)
    *,
    previous: Any = None,  # Short-term memory from the previous invocation
    config: RunnableConfig,  # Run-time configuration
    runtime: Runtime,  # Context, store, and writer for the current run
) -> dict:
    memory_store = runtime.store
    writer = runtime.stream_writer
    return {
        "previous": previous,
        "some_input": some_input,
        "has_store": memory_store is not None,
        "has_writer": writer is not None,
        "thread_id": config["configurable"]["thread_id"],
    }
# :snippet-end:

# :remove-start:
_inject_config = {"configurable": {"thread_id": "1"}}
_inject_result = my_workflow.invoke({"x": 1}, _inject_config)
assert _inject_result["previous"] is None
assert _inject_result["some_input"] == {"x": 1}
assert _inject_result["has_store"] is True
assert _inject_result["has_writer"] is True
assert _inject_result["thread_id"] == "1"
print("✓ langgraph-functional-api-overview-inject")
# :remove-end:

# :snippet-start: langgraph-functional-api-overview-essay-py
import time

from langgraph.checkpoint.memory import InMemorySaver
from langgraph.func import entrypoint, task
from langgraph.types import interrupt


@task
def write_essay(topic: str) -> str:
    """Write an essay about the given topic."""
    time.sleep(1)  # Placeholder for a long-running task.
    return f"An essay about topic: {topic}"


@entrypoint(checkpointer=InMemorySaver())
def workflow(topic: str) -> dict:
    """Write an essay and pause for review."""
    essay = write_essay(topic).result()
    is_approved = interrupt({
        # Any JSON-serializable payload. Surfaces as an Interrupt when streaming.
        "essay": essay,
        "action": "Please approve/reject the essay",
    })

    return {
        "essay": essay,
        "is_approved": is_approved,
    }
# :snippet-end:

# :remove-start:
from langgraph.types import Command

_essay_config = {"configurable": {"thread_id": "essay-1"}}
_paused = workflow.invoke("cat", _essay_config)
assert "__interrupt__" in _paused
assert _paused["__interrupt__"][0].value["essay"] == "An essay about topic: cat"
_resumed = workflow.invoke(Command(resume=True), _essay_config)
assert _resumed == {
    "essay": "An essay about topic: cat",
    "is_approved": True,
}
print("✓ langgraph-functional-api-overview-essay")
# :remove-end:
