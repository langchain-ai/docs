# :snippet-start: langgraph-use-graph-api-state-py
import operator
from typing import Annotated

from typing_extensions import TypedDict


class State(TypedDict):
    foo: int
    bar: Annotated[list[str], operator.add]
# :snippet-end:

# :remove-start:
assert State.__annotations__["foo"] is int
assert "bar" in State.__annotations__
print("✓ langgraph-use-graph-api-state-py validated")
# :remove-end:

# :snippet-start: langgraph-use-graph-api-control-flow-py
from typing_extensions import TypedDict

from langgraph.graph import END, START, StateGraph


class State(TypedDict):
    number: int
    is_even: bool
    message: str


def check_even(state: State):
    return {"is_even": state["number"] % 2 == 0}


def format_message(state: State):
    return {
        "message": (
            "The number is even." if state["is_even"] else "The number is odd."
        )
    }


workflow = StateGraph(State)
workflow.add_node("check_even", check_even)
workflow.add_node("format_message", format_message)
workflow.add_edge(START, "check_even")
workflow.add_edge("check_even", "format_message")
workflow.add_edge("format_message", END)
graph = workflow.compile()

graph.invoke({"number": 7})
# :snippet-end:

# :remove-start:
odd_result = graph.invoke({"number": 7})
assert odd_result["message"] == "The number is odd.", odd_result
even_result = graph.invoke({"number": 4})
assert even_result["message"] == "The number is even.", even_result
print("✓ langgraph-use-graph-api-control-flow-py validated")
# :remove-end:

# :snippet-start: langgraph-use-graph-api-visualize-py
print(graph.get_graph().draw_mermaid())
# :snippet-end:

# :remove-start:
assert "__start__" in graph.get_graph().draw_mermaid()
print("✓ langgraph-use-graph-api-visualize-py validated")
# :remove-end:

# :remove-start:
# Setup that the docs snippet leaves out: state schemas the snippet refers to.
class OverallState(TypedDict):
    subjects: list[str]


class State(TypedDict):  # noqa: F811
    foo: str


# :remove-end:
# :snippet-start: langgraph-use-graph-api-send-command-py
from typing import Literal

from langgraph.types import Command, Send


# Send: fan out one worker per item
def continue_to_jokes(state: OverallState):
    return [Send("generate_joke", {"subject": s}) for s in state["subjects"]]


# Command: update state and route in one return
def my_node(state: State) -> Command[Literal["my_other_node"]]:
    return Command(
        update={"foo": "bar"},
        goto="my_other_node",
    )
# :snippet-end:

# :remove-start:
sends = continue_to_jokes({"subjects": ["cats", "dogs"]})
assert [(s.node, s.arg) for s in sends] == [
    ("generate_joke", {"subject": "cats"}),
    ("generate_joke", {"subject": "dogs"}),
], sends
command = my_node({"foo": "baz"})
assert command.update == {"foo": "bar"}, command
assert command.goto == "my_other_node", command

# Wire the nodes into a graph so the Command routing and Send fan-out run.
import operator  # noqa: E402
from typing import Annotated  # noqa: E402


class JokeState(TypedDict):
    subjects: list[str]
    foo: str
    jokes: Annotated[list[str], operator.add]


def generate_joke(state: dict) -> dict:
    return {"jokes": [f"Joke about {state['subject']}"]}


def my_other_node(state: JokeState) -> dict:
    return {"foo": state["foo"] + "!"}


joke_graph = (
    StateGraph(JokeState)
    .add_node("generate_joke", generate_joke)
    .add_node("my_node", my_node)
    .add_node("my_other_node", my_other_node)
    .add_conditional_edges(START, continue_to_jokes, ["generate_joke"])
    .add_edge("generate_joke", "my_node")
    .add_edge("my_other_node", END)
    .compile()
)
joke_result = joke_graph.invoke({"subjects": ["cats", "dogs"], "foo": "baz"})
assert sorted(joke_result["jokes"]) == ["Joke about cats", "Joke about dogs"]
assert joke_result["foo"] == "bar!", joke_result
print("✓ langgraph-use-graph-api-send-command-py validated")
# :remove-end:

# :remove-start:
# Setup that the docs snippet leaves out: a builder, a node function, and state.
class NodeConfigState(TypedDict):
    foo: str


def node_function(state: NodeConfigState):
    return {"foo": state["foo"] + "!"}


builder = StateGraph(NodeConfigState)
builder.add_edge(START, "node_name")
builder.add_edge("node_name", END)
# :remove-end:
# :snippet-start: langgraph-use-graph-api-node-config-py
from langgraph.types import RetryPolicy

builder.add_node(
    "node_name",
    node_function,
    retry_policy=RetryPolicy(),
)
# :snippet-end:

# :remove-start:
retry_graph = builder.compile()
assert retry_graph.invoke({"foo": "hi"}) == {"foo": "hi!"}
print("✓ langgraph-use-graph-api-node-config-py validated")
# :remove-end:
