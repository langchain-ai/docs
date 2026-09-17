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

# :snippet-start: langgraph-graph-api-reducers-merge-does-not-clear-py
from operator import add
from typing import Annotated

from typing_extensions import TypedDict


class State(TypedDict):
    errors: Annotated[list[str], add]


# node A returns {"errors": ["bad sql"]}
# node B returns {"errors": []}
# state["errors"] is still ["bad sql"]; the empty list is merged in, not cleared
# :snippet-end:

# :snippet-start: langgraph-graph-api-reducers-overwrite-clear-py
from operator import add
from typing import Annotated

from langgraph.types import Overwrite
from typing_extensions import TypedDict


class State(TypedDict):
    errors: Annotated[list[str], add]


def clear_errors(state: State):
    # Bypass the merging reducer and clear the field
    return {"errors": Overwrite([])}
# :snippet-end:

# :remove-start:
from langgraph.graph import END, START, StateGraph


class DefaultReducerState(TypedDict):
    foo: int
    bar: list[str]


class CustomReducerState(TypedDict):
    foo: int
    bar: Annotated[list[str], add]


class MergeDoesNotClearState(TypedDict):
    errors: Annotated[list[str], add]


class OverwriteClearState(TypedDict):
    errors: Annotated[list[str], add]


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

    merge_graph = (
        StateGraph(MergeDoesNotClearState)
        .add_node("record_error", lambda _state: {"errors": ["bad sql"]})
        .add_node("attempt_clear", lambda _state: {"errors": []})
        .add_edge(START, "record_error")
        .add_edge("record_error", "attempt_clear")
        .add_edge("attempt_clear", END)
        .compile()
    )
    merge_result = merge_graph.invoke({"errors": []})
    assert merge_result == {"errors": ["bad sql"]}

    overwrite_graph = (
        StateGraph(OverwriteClearState)
        .add_node("record_error", lambda _state: {"errors": ["bad sql"]})
        .add_node("clear_errors", clear_errors)
        .add_edge(START, "record_error")
        .add_edge("record_error", "clear_errors")
        .add_edge("clear_errors", END)
        .compile()
    )
    overwrite_result = overwrite_graph.invoke({"errors": []})
    assert overwrite_result == {"errors": []}

    print("✓ langgraph-graph-api-reducers-py")
# :remove-end:
