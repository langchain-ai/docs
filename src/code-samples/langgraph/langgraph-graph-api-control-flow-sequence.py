# :snippet-start: langgraph-graph-api-control-flow-sequence-state-py
from typing_extensions import TypedDict


class State(TypedDict):
    value_1: str
    value_2: int


# :snippet-end:

# :snippet-start: langgraph-graph-api-control-flow-sequence-nodes-py
def step_1(state: State):
    return {"value_1": "a"}


def step_2(state: State):
    current_value_1 = state["value_1"]
    return {"value_1": f"{current_value_1} b"}


def step_3(state: State):
    return {"value_2": 10}


# :snippet-end:

# :remove-start:
from langgraph.graph import StateGraph

builder = StateGraph(State)
# :remove-end:

# :snippet-start: langgraph-graph-api-control-flow-sequence-custom-name-py
builder.add_node("my_node", step_1)
# :snippet-end:

# :remove-start:
assert "my_node" in builder.nodes
print("✓ custom node name validated")
# :remove-end:

# :snippet-start: langgraph-graph-api-control-flow-sequence-builder-py
from langgraph.graph import START, StateGraph

builder = StateGraph(State)

# Add nodes
builder.add_node(step_1)
builder.add_node(step_2)
builder.add_node(step_3)

# Add edges
builder.add_edge(START, "step_1")
builder.add_edge("step_1", "step_2")
builder.add_edge("step_2", "step_3")
# :snippet-end:

# :snippet-start: langgraph-graph-api-control-flow-sequence-compile-py
graph = builder.compile()
# :snippet-end:

# :snippet-start: langgraph-graph-api-control-flow-sequence-invoke-py
graph.invoke({"value_1": "c"})
# :snippet-end:

# :remove-start:
result = graph.invoke({"value_1": "c"})
assert result == {"value_1": "a b", "value_2": 10}, result
print("✓ sequence graph validated")
# :remove-end:

# :snippet-start: langgraph-graph-api-control-flow-sequence-max-concurrency-py
graph.invoke({"value_1": "c"}, {"max_concurrency": 10})
# :snippet-end:

# :remove-start:
result = graph.invoke({"value_1": "c"}, {"max_concurrency": 10})
assert result == {"value_1": "a b", "value_2": 10}, result
print("✓ max_concurrency validated")
# :remove-end:

# :snippet-start: langgraph-graph-api-control-flow-sequence-add-sequence-py
builder = StateGraph(State).add_sequence([step_1, step_2, step_3])
builder.add_edge(START, "step_1")
# :snippet-end:

# :remove-start:
assert builder.compile().invoke({"value_1": "c"}) == {"value_1": "a b", "value_2": 10}
print("✓ add_sequence validated")
# :remove-end:

# :snippet-start: langgraph-graph-api-control-flow-sequence-add-sequence-compile-py
builder = StateGraph(State).add_sequence([step_1, step_2, step_3])  # [!code highlight]
builder.add_edge(START, "step_1")

graph = builder.compile()

graph.invoke({"value_1": "c"})
# :snippet-end:

# :remove-start:
assert graph.invoke({"value_1": "c"}) == {"value_1": "a b", "value_2": 10}
print("✓ add_sequence compile validated")
# :remove-end:
