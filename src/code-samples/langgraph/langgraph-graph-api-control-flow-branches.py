# :snippet-start: langgraph-graph-api-control-flow-branches-parallel-py
import operator
from typing import Annotated

from typing_extensions import TypedDict

from langgraph.graph import END, START, StateGraph


class State(TypedDict):
    # The operator.add reducer fn makes this append-only
    aggregate: Annotated[list, operator.add]


def a(state: State):
    print(f'Adding "A" to {state["aggregate"]}')
    return {"aggregate": ["A"]}


def b(state: State):
    print(f'Adding "B" to {state["aggregate"]}')
    return {"aggregate": ["B"]}


def c(state: State):
    print(f'Adding "C" to {state["aggregate"]}')
    return {"aggregate": ["C"]}


def d(state: State):
    print(f'Adding "D" to {state["aggregate"]}')
    return {"aggregate": ["D"]}


builder = StateGraph(State)
builder.add_node(a)
builder.add_node(b)
builder.add_node(c)
builder.add_node(d)
builder.add_edge(START, "a")
builder.add_edge("a", "b")
builder.add_edge("a", "c")
builder.add_edge("b", "d")
builder.add_edge("c", "d")
builder.add_edge("d", END)
graph = builder.compile()
# :snippet-end:

# :snippet-start: langgraph-graph-api-control-flow-branches-parallel-invoke-py
graph.invoke({"aggregate": []}, {"configurable": {"thread_id": "foo"}})
# :snippet-end:

# :remove-start:
result = graph.invoke({"aggregate": []}, {"configurable": {"thread_id": "foo"}})
assert result["aggregate"][0] == "A", result
assert sorted(result["aggregate"][1:3]) == ["B", "C"], result
assert result["aggregate"][3] == "D", result
print("✓ parallel branches validated")
# :remove-end:

# :snippet-start: langgraph-graph-api-control-flow-branches-defer-py
import operator
from typing import Annotated

from typing_extensions import TypedDict

from langgraph.graph import END, START, StateGraph


class State(TypedDict):
    # The operator.add reducer fn makes this append-only
    aggregate: Annotated[list, operator.add]


def a(state: State):
    print(f'Adding "A" to {state["aggregate"]}')
    return {"aggregate": ["A"]}


def b(state: State):
    print(f'Adding "B" to {state["aggregate"]}')
    return {"aggregate": ["B"]}


def b_2(state: State):
    print(f'Adding "B_2" to {state["aggregate"]}')
    return {"aggregate": ["B_2"]}


def c(state: State):
    print(f'Adding "C" to {state["aggregate"]}')
    return {"aggregate": ["C"]}


def d(state: State):
    print(f'Adding "D" to {state["aggregate"]}')
    return {"aggregate": ["D"]}


builder = StateGraph(State)
builder.add_node(a)
builder.add_node(b)
builder.add_node(b_2)
builder.add_node(c)
builder.add_node(d, defer=True)  # [!code highlight]
builder.add_edge(START, "a")
builder.add_edge("a", "b")
builder.add_edge("a", "c")
builder.add_edge("b", "b_2")
builder.add_edge("b_2", "d")
builder.add_edge("c", "d")
builder.add_edge("d", END)
graph = builder.compile()
# :snippet-end:

# :snippet-start: langgraph-graph-api-control-flow-branches-defer-invoke-py
graph.invoke({"aggregate": []})
# :snippet-end:

# :remove-start:
result = graph.invoke({"aggregate": []})
assert result["aggregate"][0] == "A", result
assert sorted(result["aggregate"][1:3]) == ["B", "C"], result
assert result["aggregate"][3:] == ["B_2", "D"], result
print("✓ deferred node validated")

builder = StateGraph(State)
builder.add_node(a)
builder.add_node(b)
builder.add_node(b_2)
builder.add_node(c)
builder.add_node(d)
builder.add_edge(START, "a")
builder.add_edge("a", "b")
builder.add_edge("a", "c")
builder.add_edge("b", "b_2")
# :remove-end:

# :snippet-start: langgraph-graph-api-control-flow-branches-defer-list-edge-py
builder.add_edge(["b_2", "c"], "d")  # d runs once, after both b_2 and c complete
# :snippet-end:

# :remove-start:
builder.add_edge("d", END)
list_result = builder.compile().invoke({"aggregate": []})
assert list_result["aggregate"][0] == "A", list_result
assert list_result["aggregate"].count("D") == 1, list_result
assert list_result["aggregate"][-1] == "D", list_result
print("✓ list-form edge validated")
# :remove-end:

# :snippet-start: langgraph-graph-api-control-flow-branches-conditional-py
import operator
from typing import Annotated, Literal, Sequence

from typing_extensions import TypedDict

from langgraph.graph import END, START, StateGraph


class State(TypedDict):
    aggregate: Annotated[list, operator.add]
    # Branching key set by node a
    which: str


def a(state: State):
    print(f'Adding "A" to {state["aggregate"]}')
    return {"aggregate": ["A"], "which": "c"}  # [!code highlight]


def b(state: State):
    print(f'Adding "B" to {state["aggregate"]}')
    return {"aggregate": ["B"]}


def c(state: State):
    print(f'Adding "C" to {state["aggregate"]}')
    return {"aggregate": ["C"]}


builder = StateGraph(State)
builder.add_node(a)
builder.add_node(b)
builder.add_node(c)
builder.add_edge(START, "a")
builder.add_edge("b", END)
builder.add_edge("c", END)


def conditional_edge(state: State) -> Literal["b", "c"]:
    # Fill in arbitrary logic here that uses the state
    # to determine the next node
    return state["which"]


builder.add_conditional_edges("a", conditional_edge)  # [!code highlight]

graph = builder.compile()
# :snippet-end:

# :snippet-start: langgraph-graph-api-control-flow-branches-conditional-invoke-py
result = graph.invoke({"aggregate": []})
print(result)
# :snippet-end:

# :remove-start:
assert result == {"aggregate": ["A", "C"], "which": "c"}, result
print("✓ conditional branching validated")
# :remove-end:

# :snippet-start: langgraph-graph-api-control-flow-branches-multi-route-py
def route_bc_or_cd(state: State) -> Sequence[str]:
    if state["which"] == "cd":
        return ["c", "d"]
    return ["b", "c"]


# :snippet-end:

# :remove-start:
assert route_bc_or_cd({"aggregate": [], "which": "cd"}) == ["c", "d"]
assert route_bc_or_cd({"aggregate": [], "which": "bc"}) == ["b", "c"]
print("✓ multi-destination router validated")
# :remove-end:
