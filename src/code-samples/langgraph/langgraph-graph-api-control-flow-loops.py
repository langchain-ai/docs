# :snippet-start: langgraph-graph-api-control-flow-loops-define-py
import operator
from typing import Annotated, Literal

from typing_extensions import TypedDict

from langgraph.graph import END, START, StateGraph


class State(TypedDict):
    # The operator.add reducer fn makes this append-only
    aggregate: Annotated[list, operator.add]


def a(state: State):
    print(f'Node A sees {state["aggregate"]}')
    return {"aggregate": ["A"]}


def b(state: State):
    print(f'Node B sees {state["aggregate"]}')
    return {"aggregate": ["B"]}


# Define nodes
builder = StateGraph(State)
builder.add_node(a)
builder.add_node(b)


# Define edges
def route(state: State) -> Literal["b", END]:
    if len(state["aggregate"]) < 7:
        return "b"
    else:
        return END


builder.add_edge(START, "a")
builder.add_conditional_edges("a", route)
builder.add_edge("b", "a")
graph = builder.compile()
# :snippet-end:

# :snippet-start: langgraph-graph-api-control-flow-loops-invoke-py
graph.invoke({"aggregate": []})
# :snippet-end:

# :remove-start:
result = graph.invoke({"aggregate": []})
assert result["aggregate"] == ["A", "B", "A", "B", "A", "B", "A"], result
print("✓ loop validated")
inputs = {"aggregate": []}
# :remove-end:

# :snippet-start: langgraph-graph-api-control-flow-loops-recursion-limit-py
from langgraph.errors import GraphRecursionError

try:
    graph.invoke(inputs, {"recursion_limit": 3})
except GraphRecursionError:
    print("Recursion Error")
# :snippet-end:

# :remove-start:
try:
    graph.invoke(inputs, {"recursion_limit": 3})
except GraphRecursionError:
    print("✓ recursion limit of 3 raised GraphRecursionError")
else:
    msg = "Expected GraphRecursionError"
    raise AssertionError(msg)
# :remove-end:

# :snippet-start: langgraph-graph-api-control-flow-loops-impose-limit-py
from langgraph.errors import GraphRecursionError

try:
    graph.invoke({"aggregate": []}, {"recursion_limit": 4})
except GraphRecursionError:
    print("Recursion Error")
# :snippet-end:

# :remove-start:
try:
    graph.invoke({"aggregate": []}, {"recursion_limit": 4})
except GraphRecursionError:
    print("✓ recursion limit of 4 raised GraphRecursionError")
else:
    msg = "Expected GraphRecursionError"
    raise AssertionError(msg)
# :remove-end:

# :remove-start:
def termination_condition(state: State) -> bool:
    return len(state["aggregate"]) >= 7


# :remove-end:

# :snippet-start: langgraph-graph-api-control-flow-loops-termination-py
builder = StateGraph(State)
builder.add_node(a)
builder.add_node(b)


def route(state: State) -> Literal["b", END]:
    if termination_condition(state):
        return END
    else:
        return "b"


builder.add_edge(START, "a")
builder.add_conditional_edges("a", route)
builder.add_edge("b", "a")
graph = builder.compile()
# :snippet-end:

# :remove-start:
result = graph.invoke({"aggregate": []})
assert result["aggregate"] == ["A", "B", "A", "B", "A", "B", "A"], result
print("✓ termination condition validated")
# :remove-end:

# :snippet-start: langgraph-graph-api-control-flow-loops-branches-py
import operator
from typing import Annotated, Literal

from typing_extensions import TypedDict

from langgraph.graph import END, START, StateGraph


class State(TypedDict):
    aggregate: Annotated[list, operator.add]


def a(state: State):
    print(f'Node A sees {state["aggregate"]}')
    return {"aggregate": ["A"]}


def b(state: State):
    print(f'Node B sees {state["aggregate"]}')
    return {"aggregate": ["B"]}


def c(state: State):
    print(f'Node C sees {state["aggregate"]}')
    return {"aggregate": ["C"]}


def d(state: State):
    print(f'Node D sees {state["aggregate"]}')
    return {"aggregate": ["D"]}


builder = StateGraph(State)
builder.add_node(a)
builder.add_node(b)
builder.add_node(c)
builder.add_node(d)


def route(state: State) -> Literal["b", END]:
    if len(state["aggregate"]) < 7:
        return "b"
    else:
        return END


builder.add_edge(START, "a")
builder.add_conditional_edges("a", route)
builder.add_edge("b", "c")
builder.add_edge("b", "d")
builder.add_edge(["c", "d"], "a")
graph = builder.compile()
# :snippet-end:

# :snippet-start: langgraph-graph-api-control-flow-loops-branches-invoke-py
result = graph.invoke({"aggregate": []})
# :snippet-end:

# :remove-start:
assert result["aggregate"][0] == "A", result
assert result["aggregate"] == ["A", "B", "C", "D", "A", "B", "C", "D", "A"], result
print("✓ loop with branches validated")
# :remove-end:

# :snippet-start: langgraph-graph-api-control-flow-loops-branches-limit-py
from langgraph.errors import GraphRecursionError

try:
    result = graph.invoke({"aggregate": []}, {"recursion_limit": 4})
except GraphRecursionError:
    print("Recursion Error")
# :snippet-end:

# :remove-start:
try:
    graph.invoke({"aggregate": []}, {"recursion_limit": 4})
except GraphRecursionError:
    print("✓ loop with branches raised GraphRecursionError at limit 4")
else:
    msg = "Expected GraphRecursionError"
    raise AssertionError(msg)
# :remove-end:

# :snippet-start: langgraph-graph-api-control-flow-loops-step-counter-py
from langchain_core.runnables import RunnableConfig


def my_node(state: dict, config: RunnableConfig) -> dict:
    current_step = config["metadata"]["langgraph_step"]
    print(f"Currently on step: {current_step}")
    return state


# :snippet-end:

# :remove-start:
step_builder = StateGraph(State)
step_builder.add_node("my_node", my_node)
step_builder.add_edge(START, "my_node")
step_builder.add_edge("my_node", END)
step_result = step_builder.compile().invoke({"aggregate": []})
assert step_result == {"aggregate": []}, step_result
print("✓ langgraph_step metadata validated")
# :remove-end:

# :snippet-start: langgraph-graph-api-control-flow-loops-remaining-steps-py
import operator
from typing import Annotated, Literal

from typing_extensions import TypedDict

from langgraph.graph import END, START, StateGraph
from langgraph.managed.is_last_step import RemainingSteps


class State(TypedDict):
    messages: Annotated[list, operator.add]
    remaining_steps: RemainingSteps


def reasoning_node(state: State) -> dict:
    remaining = state["remaining_steps"]
    if remaining <= 2:
        return {"messages": ["Approaching limit, wrapping up..."]}
    return {"messages": ["thinking..."]}


def route_decision(state: State) -> Literal["reasoning_node", "fallback_node"]:
    if state["remaining_steps"] <= 2:
        return "fallback_node"
    return "reasoning_node"


def fallback_node(state: State) -> dict:
    return {"messages": ["Reached complexity limit, providing best effort answer"]}


builder = StateGraph(State)
builder.add_node("reasoning_node", reasoning_node)
builder.add_node("fallback_node", fallback_node)
builder.add_edge(START, "reasoning_node")
builder.add_conditional_edges("reasoning_node", route_decision)
builder.add_edge("fallback_node", END)
graph = builder.compile()

result = graph.invoke({"messages": []}, {"recursion_limit": 10})
# :snippet-end:

# :remove-start:
assert result["messages"][-1] == (
    "Reached complexity limit, providing best effort answer"
), result
assert "thinking..." in result["messages"], result
print("✓ RemainingSteps validated")
# :remove-end:
