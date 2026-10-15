# :snippet-start: graph-api-using-tasks-task-py
from typing import NotRequired

import requests
from langchain_core.utils.uuid import uuid7
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.func import task
from langgraph.graph import END, START, StateGraph
from typing_extensions import TypedDict


class State(TypedDict):
    urls: list[str]
    results: NotRequired[list[str]]


@task
def _make_request(url: str):
    """Make a request."""
    return requests.get(url).text[:100]  # [!code highlight]


def call_api(state: State):
    """Example node that makes API requests as checkpointed tasks."""
    futures = [_make_request(url) for url in state["urls"]]  # [!code highlight]
    results = [f.result() for f in futures]
    return {"results": results}


builder = StateGraph(State)
builder.add_node("call_api", call_api)
builder.add_edge(START, "call_api")
builder.add_edge("call_api", END)

checkpointer = InMemorySaver()
graph = builder.compile(checkpointer=checkpointer)

thread_id = str(uuid7())
config = {"configurable": {"thread_id": thread_id}}

# :remove-start:
_original_get = requests.get


class _FakeResponse:
    text = "Example response body"


def _fake_get(url: str) -> _FakeResponse:
    assert url == "https://www.example.com"
    return _FakeResponse()


requests.get = _fake_get  # type: ignore[method-assign]
# :remove-end:
graph.invoke({"urls": ["https://www.example.com"]}, config)
# :remove-start:
results = graph.get_state(config).values["results"]
assert results == ["Example response body"]
requests.get = _original_get  # type: ignore[method-assign]
print("✓ graph API task sample works correctly")
# :remove-end:
# :snippet-end:
