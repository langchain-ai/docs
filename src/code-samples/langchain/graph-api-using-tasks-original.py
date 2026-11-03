# :snippet-start: graph-api-using-tasks-original-py
from typing import NotRequired

import requests
from langchain_core.utils.uuid import uuid7
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, StateGraph
from typing_extensions import TypedDict


class State(TypedDict):
    url: str
    result: NotRequired[str]


def call_api(state: State):
    """Example node that makes an API request."""
    result = requests.get(state["url"]).text[:100]  # [!code highlight]
    return {"result": result}


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
graph.invoke({"url": "https://www.example.com"}, config)
# :remove-start:
result = graph.get_state(config).values["result"]
assert result == "Example response body"
requests.get = _original_get  # type: ignore[method-assign]
print("✓ graph API original sample works correctly")
# :remove-end:
# :snippet-end:
