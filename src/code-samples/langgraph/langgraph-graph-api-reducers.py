# :snippet-start: langgraph-graph-api-reducers-append-strings-py
from typing import Annotated

from typing_extensions import TypedDict


def append_strings(left: list[str], right: list[str]) -> list[str]:
    """Combine the existing state value (left) with a node update (right)."""
    return left + right


class State(TypedDict):
    tags: Annotated[list[str], append_strings]
# :snippet-end:

# :snippet-start: langgraph-graph-api-reducers-append-strings-call-py
append_strings(left=["draft"], right=["review"])  # returns ["draft", "review"]
# :snippet-end:

# :snippet-start: langgraph-graph-api-reducers-default-state-py
from typing_extensions import TypedDict


class State(TypedDict):
    foo: int
    bar: list[str]
# :snippet-end:

# :snippet-start: langgraph-graph-api-reducers-custom-state-py
from operator import add
from typing import Annotated

from typing_extensions import TypedDict


class State(TypedDict):
    foo: int
    bar: Annotated[list[str], add]
# :snippet-end:

# :remove-start:
from langgraph.graph import END, START, StateGraph


class DefaultReducerState(TypedDict):
    foo: int
    bar: list[str]


class CustomReducerState(TypedDict):
    foo: int
    bar: Annotated[list[str], add]


def _build_two_node_graph(state_type):
    graph = (
        StateGraph(state_type)
        .add_node("first", lambda _state: {"foo": 2})
        .add_node("second", lambda _state: {"bar": ["bye"]})
        .add_edge(START, "first")
        .add_edge("first", "second")
        .add_edge("second", END)
        .compile()
    )
    return graph


if __name__ == "__main__":
    assert append_strings(left=["draft"], right=["review"]) == ["draft", "review"]

    default_graph = _build_two_node_graph(DefaultReducerState)
    default_result = default_graph.invoke({"foo": 1, "bar": ["hi"]})
    assert default_result == {"foo": 2, "bar": ["bye"]}

    custom_graph = _build_two_node_graph(CustomReducerState)
    custom_result = custom_graph.invoke({"foo": 1, "bar": ["hi"]})
    assert custom_result == {"foo": 2, "bar": ["hi", "bye"]}

    print("✓ langgraph-graph-api-reducers-py")
# :remove-end:
