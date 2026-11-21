# :snippet-start: langgraph-graph-api-state-define-py
from langchain.messages import AnyMessage
from typing_extensions import TypedDict


class State(TypedDict):
    messages: list[AnyMessage]
    extra_field: int


# :snippet-end:

# :remove-start:
assert set(State.__annotations__) == {"messages", "extra_field"}
# :remove-end:

# :snippet-start: langgraph-graph-api-state-update-node-py
from langchain.messages import AIMessage


def node(state: State):
    messages = state["messages"]
    new_message = AIMessage("Hello!")
    return {"messages": messages + [new_message], "extra_field": 10}


# :snippet-end:

# :remove-start:
_node_result = node({"messages": [], "extra_field": 0})
assert _node_result["extra_field"] == 10
assert _node_result["messages"][0].content == "Hello!"
# :remove-end:

# :snippet-start: langgraph-graph-api-state-build-graph-py
from langgraph.graph import StateGraph

builder = StateGraph(State)
builder.add_node(node)
builder.set_entry_point("node")
graph = builder.compile()
# :snippet-end:

# :remove-start:
assert graph is not None
# :remove-end:

# :snippet-start: langgraph-graph-api-state-invoke-py
from langchain.messages import HumanMessage

result = graph.invoke({"messages": [HumanMessage("Hi")]})
result
# :snippet-end:

# :remove-start:
assert [m.content for m in result["messages"]] == ["Hi", "Hello!"]
assert result["extra_field"] == 10
# :remove-end:

# :snippet-start: langgraph-graph-api-state-pretty-print-py
for message in result["messages"]:
    message.pretty_print()
# :snippet-end:

# :snippet-start: langgraph-graph-api-state-reducer-define-py
from typing_extensions import Annotated


def add(left, right):
    """Can also import `add` from the `operator` built-in."""
    return left + right


class State(TypedDict):
    messages: Annotated[list[AnyMessage], add]  # [!code highlight]
    extra_field: int


# :snippet-end:

# :remove-start:
assert add([1], [2]) == [1, 2]
# :remove-end:

# :snippet-start: langgraph-graph-api-state-reducer-node-py
def node(state: State):
    new_message = AIMessage("Hello!")
    return {"messages": [new_message], "extra_field": 10}  # [!code highlight]


# :snippet-end:

# :remove-start:
assert node({"messages": [], "extra_field": 0})["extra_field"] == 10
# :remove-end:

# :snippet-start: langgraph-graph-api-state-reducer-invoke-py
from langgraph.graph import START

graph = StateGraph(State).add_node(node).add_edge(START, "node").compile()

result = graph.invoke({"messages": [HumanMessage("Hi")]})

for message in result["messages"]:
    message.pretty_print()
# :snippet-end:

# :remove-start:
assert [m.content for m in result["messages"]] == ["Hi", "Hello!"]
# :remove-end:

# :snippet-start: langgraph-graph-api-state-add-messages-py
from langgraph.graph.message import add_messages


class State(TypedDict):
    messages: Annotated[list[AnyMessage], add_messages]  # [!code highlight]
    extra_field: int


def node(state: State):
    new_message = AIMessage("Hello!")
    return {"messages": [new_message], "extra_field": 10}


graph = StateGraph(State).add_node(node).set_entry_point("node").compile()
# :snippet-end:

# :snippet-start: langgraph-graph-api-state-add-messages-invoke-py
input_message = {"role": "user", "content": "Hi"}  # [!code highlight]

result = graph.invoke({"messages": [input_message]})

for message in result["messages"]:
    message.pretty_print()
# :snippet-end:

# :remove-start:
assert [m.type for m in result["messages"]] == ["human", "ai"]
assert [m.content for m in result["messages"]] == ["Hi", "Hello!"]
# :remove-end:

# :snippet-start: langgraph-graph-api-state-messages-state-py
from langgraph.graph import MessagesState


class State(MessagesState):
    extra_field: int


# :snippet-end:

# :remove-start:
assert "messages" in State.__annotations__ or "messages" in {
    key for base in State.__mro__ for key in getattr(base, "__annotations__", {})
}
assert "extra_field" in State.__annotations__
# :remove-end:

# :snippet-start: langgraph-graph-api-state-overwrite-py
import operator

from langgraph.graph import END, START, StateGraph
from langgraph.types import Overwrite
from typing_extensions import Annotated, TypedDict


class State(TypedDict):
    messages: Annotated[list, operator.add]


def add_message(state: State):
    return {"messages": ["first message"]}


def replace_messages(state: State):
    # Bypass the reducer and replace the entire messages list
    return {"messages": Overwrite(["replacement message"])}


builder = StateGraph(State)
builder.add_node("add_message", add_message)
builder.add_node("replace_messages", replace_messages)
builder.add_edge(START, "add_message")
builder.add_edge("add_message", "replace_messages")
builder.add_edge("replace_messages", END)

graph = builder.compile()

result = graph.invoke({"messages": ["initial"]})
print(result["messages"])
# :snippet-end:

# :remove-start:
assert result["messages"] == ["replacement message"]
# :remove-end:

# :snippet-start: langgraph-graph-api-state-overwrite-json-py
def replace_messages(state: State):
    return {"messages": {"__overwrite__": ["replacement message"]}}


# :snippet-end:

# :remove-start:
_json_graph = (
    StateGraph(State)
    .add_node("add_message", add_message)
    .add_node("replace_messages", replace_messages)
    .add_edge(START, "add_message")
    .add_edge("add_message", "replace_messages")
    .add_edge("replace_messages", END)
    .compile()
)
assert _json_graph.invoke({"messages": ["initial"]})["messages"] == [
    "replacement message"
]
# :remove-end:

# :snippet-start: langgraph-graph-api-state-input-output-py
from langgraph.graph import END, START, StateGraph
from typing_extensions import TypedDict


# Define the schema for the input
class InputState(TypedDict):
    question: str


# Define the schema for the output
class OutputState(TypedDict):
    answer: str


# Define the overall schema, combining both input and output
class OverallState(InputState, OutputState):
    pass


# Define the node that processes the input and generates an answer
def answer_node(state: InputState):
    # Example answer and an extra key
    return {"answer": "bye", "question": state["question"]}


# Build the graph with input and output schemas specified
builder = StateGraph(OverallState, input_schema=InputState, output_schema=OutputState)
builder.add_node(answer_node)  # Add the answer node
builder.add_edge(START, "answer_node")  # Define the starting edge
builder.add_edge("answer_node", END)  # Define the ending edge
graph = builder.compile()  # Compile the graph

# Invoke the graph with an input and print the result
print(graph.invoke({"question": "hi"}))
# :snippet-end:

# :remove-start:
assert graph.invoke({"question": "hi"}) == {"answer": "bye"}
# :remove-end:

# :snippet-start: langgraph-graph-api-state-private-state-py
from langgraph.graph import END, START, StateGraph
from typing_extensions import TypedDict


# The overall state of the graph (this is the public state shared across nodes)
class OverallState(TypedDict):
    a: str


# Output from node_1 contains private data that is not part of the overall state
class Node1Output(TypedDict):
    private_data: str


# The private data is only shared between node_1 and node_2
def node_1(state: OverallState) -> Node1Output:
    output = {"private_data": "set by node_1"}
    print(f"Entered node `node_1`:\n\tInput: {state}.\n\tReturned: {output}")
    return output


# Node 2 input only requests the private data available after node_1
class Node2Input(TypedDict):
    private_data: str


def node_2(state: Node2Input) -> OverallState:
    output = {"a": "set by node_2"}
    print(f"Entered node `node_2`:\n\tInput: {state}.\n\tReturned: {output}")
    return output


# Node 3 only has access to the overall state (no access to private data from node_1)
def node_3(state: OverallState) -> OverallState:
    output = {"a": "set by node_3"}
    print(f"Entered node `node_3`:\n\tInput: {state}.\n\tReturned: {output}")
    return output


# Connect nodes in a sequence
# node_2 accepts private data from node_1, whereas
# node_3 does not see the private data.
builder = StateGraph(OverallState).add_sequence([node_1, node_2, node_3])
builder.add_edge(START, "node_1")
graph = builder.compile()

# Invoke the graph with the initial state
response = graph.invoke(
    {
        "a": "set at start",
    }
)

print()
print(f"Output of graph invocation: {response}")
# :snippet-end:

# :remove-start:
assert response == {"a": "set by node_3"}
# :remove-end:

# :remove-start:
from typing import TypedDict as _TypedDict


class _StreamInput(_TypedDict):
    user_input: str


class _StreamOutput(_TypedDict):
    graph_output: str


class _StreamOverall(_TypedDict):
    foo: str
    user_input: str
    graph_output: str


class _StreamPrivate(_TypedDict):
    bar: str


def _stream_node_1(state: _StreamInput) -> _StreamOverall:
    return {"foo": state["user_input"] + " name"}


def _stream_node_2(state: _StreamOverall) -> _StreamPrivate:
    return {"bar": state["foo"] + " is"}


def _stream_node_3(state: _StreamPrivate) -> _StreamOutput:
    return {"graph_output": state["bar"] + " Lance"}


graph = (
    StateGraph(_StreamOverall, input_schema=_StreamInput, output_schema=_StreamOutput)
    .add_node("node_1", _stream_node_1)
    .add_node("node_2", _stream_node_2)
    .add_node("node_3", _stream_node_3)
    .add_edge(START, "node_1")
    .add_edge("node_1", "node_2")
    .add_edge("node_2", "node_3")
    .add_edge("node_3", END)
    .compile()
)
# :remove-end:

# :snippet-start: langgraph-graph-api-state-stream-output-keys-py
for snapshot in graph.stream(
    {"user_input": "My"},
    stream_mode="values",
    output_keys=["graph_output"],  # [!code highlight]
):
    print(snapshot)
# {'graph_output': 'My name is Lance'}
# :snippet-end:

# :remove-start:
_snapshots = list(
    graph.stream(
        {"user_input": "My"}, stream_mode="values", output_keys=["graph_output"]
    )
)
assert _snapshots[-1] == {"graph_output": "My name is Lance"}
assert all(set(s) <= {"graph_output"} for s in _snapshots)
# :remove-end:

# :snippet-start: langgraph-graph-api-state-pydantic-py
from langgraph.graph import END, START, StateGraph
from pydantic import BaseModel


# The overall state of the graph (this is the public state shared across nodes)
class OverallState(BaseModel):
    a: str


def node(state: OverallState):
    return {"a": "goodbye"}


# Build the state graph
builder = StateGraph(OverallState)
builder.add_node(node)  # node_1 is the first node
builder.add_edge(START, "node")  # Start the graph with node_1
builder.add_edge("node", END)  # End the graph after node_1
graph = builder.compile()

# Test the graph with a valid input
graph.invoke({"a": "hello"})
# :snippet-end:

# :remove-start:
assert graph.invoke({"a": "hello"}) == {"a": "goodbye"}
# :remove-end:

# :snippet-start: langgraph-graph-api-state-pydantic-invalid-py
try:
    graph.invoke({"a": 123})  # Should be a string
except Exception as e:
    print("An exception was raised because `a` is an integer rather than a string.")
    print(e)
# :snippet-end:

# :remove-start:
try:
    graph.invoke({"a": 123})
except Exception as _exc:
    assert "validation error" in str(_exc)
else:
    msg = "Expected a validation error for invalid input"
    raise AssertionError(msg)
# :remove-end:

# :snippet-start: langgraph-graph-api-state-pydantic-serialization-py
from langgraph.graph import END, START, StateGraph
from pydantic import BaseModel


class NestedModel(BaseModel):
    value: str


class ComplexState(BaseModel):
    text: str
    count: int
    nested: NestedModel


def process_node(state: ComplexState):
    # Node receives a validated Pydantic object
    print(f"Input state type: {type(state)}")
    print(f"Nested type: {type(state.nested)}")
    # Return a dictionary update
    return {"text": state.text + " processed", "count": state.count + 1}


# Build the graph
builder = StateGraph(ComplexState)
builder.add_node("process", process_node)
builder.add_edge(START, "process")
builder.add_edge("process", END)
graph = builder.compile()

# Create a Pydantic instance for input
input_state = ComplexState(text="hello", count=0, nested=NestedModel(value="test"))
print(f"Input object type: {type(input_state)}")

# Invoke graph with a Pydantic instance
result = graph.invoke(input_state)
print(f"Output type: {type(result)}")
print(f"Output content: {result}")

# Convert back to Pydantic model if needed
output_model = ComplexState(**result)
print(f"Converted back to Pydantic: {type(output_model)}")
# :snippet-end:

# :remove-start:
assert isinstance(result, dict)
assert result["text"] == "hello processed"
assert result["count"] == 1
assert isinstance(output_model, ComplexState)
assert isinstance(output_model.nested, NestedModel)
# :remove-end:

# :snippet-start: langgraph-graph-api-state-pydantic-coercion-py
from langgraph.graph import END, START, StateGraph
from pydantic import BaseModel


class CoercionExample(BaseModel):
    # Pydantic will coerce string numbers to integers
    number: int
    # Pydantic will parse string booleans to bool
    flag: bool


def inspect_node(state: CoercionExample):
    print(f"number: {state.number} (type: {type(state.number)})")
    print(f"flag: {state.flag} (type: {type(state.flag)})")
    return {}


builder = StateGraph(CoercionExample)
builder.add_node("inspect", inspect_node)
builder.add_edge(START, "inspect")
builder.add_edge("inspect", END)
graph = builder.compile()

# Demonstrate coercion with string inputs that will be converted
result = graph.invoke({"number": "42", "flag": "true"})

# This would fail with a validation error
try:
    graph.invoke({"number": "not-a-number", "flag": "true"})
except Exception as e:
    print(f"\nExpected validation error: {e}")
# :snippet-end:

# :remove-start:
# The node returns no update, so the graph returns the raw (uncoerced) input.
assert result == {"number": "42", "flag": "true"}
# :remove-end:

# :snippet-start: langgraph-graph-api-state-pydantic-messages-py
from typing import List

from langchain.messages import AIMessage, AnyMessage, HumanMessage
from langgraph.graph import END, START, StateGraph
from pydantic import BaseModel


class ChatState(BaseModel):
    messages: List[AnyMessage]
    context: str


def add_message(state: ChatState):
    return {"messages": state.messages + [AIMessage(content="Hello there!")]}


builder = StateGraph(ChatState)
builder.add_node("add_message", add_message)
builder.add_edge(START, "add_message")
builder.add_edge("add_message", END)
graph = builder.compile()

# Create input with a message
initial_state = ChatState(
    messages=[HumanMessage(content="Hi")], context="Customer support chat"
)

result = graph.invoke(initial_state)
print(f"Output: {result}")

# Convert back to Pydantic model to see message types
output_model = ChatState(**result)
for i, msg in enumerate(output_model.messages):
    print(f"Message {i}: {type(msg).__name__} - {msg.content}")
# :snippet-end:

# :remove-start:
assert [type(m).__name__ for m in output_model.messages] == [
    "HumanMessage",
    "AIMessage",
]
assert output_model.messages[1].content == "Hello there!"
print("✓ langgraph-graph-api-state-py")
# :remove-end:
