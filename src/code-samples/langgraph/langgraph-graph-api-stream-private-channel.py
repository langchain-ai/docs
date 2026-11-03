from typing import TypedDict

from langgraph.graph import END, START, StateGraph


class InputState(TypedDict):
    user_input: str


class OutputState(TypedDict):
    graph_output: str


class OverallState(TypedDict):
    foo: str
    user_input: str
    graph_output: str


class PrivateState(TypedDict):
    bar: str


def node_1(state: InputState) -> OverallState:
    return {"foo": state["user_input"] + " name"}


def node_2(state: OverallState) -> PrivateState:
    return {"bar": state["foo"] + " is"}


def node_3(state: PrivateState) -> OutputState:
    return {"graph_output": state["bar"] + " Lance"}


builder = StateGraph(OverallState, input_schema=InputState, output_schema=OutputState)
builder.add_node("node_1", node_1)
builder.add_node("node_2", node_2)
builder.add_node("node_3", node_3)
builder.add_edge(START, "node_1")
builder.add_edge("node_1", "node_2")
builder.add_edge("node_2", "node_3")
builder.add_edge("node_3", END)

graph = builder.compile()

# :snippet-start: langgraph-graph-api-stream-private-channel-py
stream = graph.stream_events({"user_input": "My"}, version="v3")
for snapshot in stream.values:
    print(snapshot)
# {'user_input': 'My'}
# {'foo': 'My name', 'user_input': 'My'}
# {'foo': 'My name', 'user_input': 'My', 'bar': 'My name is'}        # <-- private channel
# {'foo': 'My name', 'user_input': 'My', 'graph_output': 'My name is Lance', 'bar': 'My name is'}
# :snippet-end:


# :remove-start:
if __name__ == "__main__":
    test_stream = graph.stream_events({"user_input": "My"}, version="v3")
    snapshots = list(test_stream.values)
    assert snapshots[0] == {"user_input": "My"}
    assert snapshots[1] == {"user_input": "My", "foo": "My name"}
    assert snapshots[2]["bar"] == "My name is"
    assert snapshots[-1]["graph_output"] == "My name is Lance"
    print("✓ langgraph-graph-api-stream-private-channel")
# :remove-end:
