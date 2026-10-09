# :snippet-start: langgraph-graph-api-send-command-send-py
import operator
from typing_extensions import Annotated, TypedDict

from langgraph.graph import END, START, StateGraph
from langgraph.types import Send


class OverallState(TypedDict):
    topic: str
    subjects: list[str]
    jokes: Annotated[list[str], operator.add]
    best_selected_joke: str


class JokeState(TypedDict):
    subject: str


def generate_topics(state: OverallState):
    return {"subjects": ["lions", "elephants", "penguins"]}


def generate_joke(state: JokeState):
    joke_map = {
        "lions": "Why don't lions like fast food? Because they can't catch it!",
        "elephants": "Why don't elephants use computers? They're afraid of the mouse!",
        "penguins": "Why don't penguins like talking to strangers at parties? Because they find it hard to break the ice.",
    }
    return {"jokes": [joke_map[state["subject"]]]}


def continue_to_jokes(state: OverallState):
    return [Send("generate_joke", {"subject": s}) for s in state["subjects"]]


def best_joke(state: OverallState):
    return {"best_selected_joke": "penguins"}


builder = StateGraph(OverallState)
builder.add_node("generate_topics", generate_topics)
builder.add_node("generate_joke", generate_joke)
builder.add_node("best_joke", best_joke)
builder.add_edge(START, "generate_topics")
builder.add_conditional_edges("generate_topics", continue_to_jokes, ["generate_joke"])
builder.add_edge("generate_joke", "best_joke")
builder.add_edge("best_joke", END)
graph = builder.compile()
# :snippet-end:

# :snippet-start: langgraph-graph-api-send-command-send-stream-py
for chunk in graph.stream({"topic": "animals"}, stream_mode="updates"):
    print(chunk)
# :snippet-end:

# :remove-start:
send_chunks = list(graph.stream({"topic": "animals"}, stream_mode="updates"))
assert send_chunks[0] == {
    "generate_topics": {"subjects": ["lions", "elephants", "penguins"]}
}
assert send_chunks[-1] == {"best_joke": {"best_selected_joke": "penguins"}}
joke_chunks = [c["generate_joke"]["jokes"][0] for c in send_chunks[1:-1]]
assert len(joke_chunks) == 3
assert len(set(joke_chunks)) == 3
assert any("lions" in joke for joke in joke_chunks)
assert any("elephants" in joke for joke in joke_chunks)
assert any("penguins" in joke for joke in joke_chunks)

send_result = graph.invoke({"topic": "animals"})
assert len(send_result["jokes"]) == 3
assert send_result["best_selected_joke"] == "penguins"
print("✓ langgraph-graph-api-send-command-send-py")
# :remove-end:

# :remove-start:
from typing_extensions import Literal

from langgraph.types import Command


class State(TypedDict):
    foo: str


# :remove-end:

# :snippet-start: langgraph-graph-api-send-command-command-shape-py
def my_node(state: State) -> Command[Literal["my_other_node"]]:
    return Command(
        # state update
        update={"foo": "bar"},
        # control flow
        goto="my_other_node",
    )
# :snippet-end:

# :remove-start:
shape_result = my_node({"foo": ""})
assert isinstance(shape_result, Command)
assert shape_result.update == {"foo": "bar"}
assert shape_result.goto == "my_other_node"
print("✓ langgraph-graph-api-send-command-command-shape-py")
# :remove-end:

# :snippet-start: langgraph-graph-api-send-command-command-graph-nodes-py
import random
from typing_extensions import Literal, TypedDict

from langgraph.graph import START, StateGraph
from langgraph.types import Command


class State(TypedDict):
    foo: str


def node_a(state: State) -> Command[Literal["node_b", "node_c"]]:
    print("Called A")
    value = random.choice(["b", "c"])
    goto = "node_b" if value == "b" else "node_c"

    return Command(
        update={"foo": value},
        goto=goto,
    )


def node_b(state: State):
    print("Called B")
    return {"foo": state["foo"] + "b"}


def node_c(state: State):
    print("Called C")
    return {"foo": state["foo"] + "c"}
# :snippet-end:

# :snippet-start: langgraph-graph-api-send-command-command-graph-build-py
builder = StateGraph(State)
builder.add_edge(START, "node_a")
builder.add_node(node_a)
builder.add_node(node_b)
builder.add_node(node_c)
# No edges between nodes A, B, and C

graph = builder.compile()
# :snippet-end:

# :snippet-start: langgraph-graph-api-send-command-command-graph-invoke-py
graph.invoke({"foo": ""})
# :snippet-end:

# :remove-start:
from unittest import mock

# The docs snippet uses random.choice; pin it so both paths are asserted.
with mock.patch.object(random, "choice", return_value="b"):
    assert graph.invoke({"foo": ""}) == {"foo": "bb"}
with mock.patch.object(random, "choice", return_value="c"):
    assert graph.invoke({"foo": ""}) == {"foo": "cc"}
# node_a must declare both destinations for rendering
drawn_edges = {(e.source, e.target) for e in graph.get_graph().edges}
assert ("node_a", "node_b") in drawn_edges
assert ("node_a", "node_c") in drawn_edges
print("✓ langgraph-graph-api-send-command-command-graph-py")
# :remove-end:

# :snippet-start: langgraph-graph-api-send-command-command-parent-shape-py
def my_node(state: State) -> Command[Literal["other_subgraph"]]:
    return Command(
        update={"foo": "bar"},
        goto="other_subgraph",  # node in the parent graph
        graph=Command.PARENT,
    )
# :snippet-end:

# :remove-start:
parent_shape_result = my_node({"foo": ""})
assert parent_shape_result.graph == Command.PARENT
assert parent_shape_result.goto == "other_subgraph"
print("✓ langgraph-graph-api-send-command-command-parent-shape-py")
# :remove-end:

# :snippet-start: langgraph-graph-api-send-command-command-parent-graph-py
import operator
import random
from typing_extensions import Annotated, TypedDict

from langgraph.graph import START, StateGraph
from langgraph.types import Command


class State(TypedDict):
    foo: Annotated[str, operator.add]  # [!code highlight]


def node_a(state: State) -> Command:
    print("Called A")
    value = random.choice(["a", "b"])
    goto = "node_b" if value == "a" else "node_c"

    return Command(
        update={"foo": value},
        goto=goto,
        # Closest parent graph relative to this subgraph
        graph=Command.PARENT,  # [!code highlight]
    )


subgraph = StateGraph(State).add_node(node_a).add_edge(START, "node_a").compile()


def node_b(state: State):
    print("Called B")
    # Reducer appends; do not manually concatenate onto state["foo"]
    return {"foo": "b"}  # [!code highlight]


def node_c(state: State):
    print("Called C")
    return {"foo": "c"}  # [!code highlight]


builder = StateGraph(State)
builder.add_edge(START, "subgraph")
builder.add_node("subgraph", subgraph)
builder.add_node(node_b)
builder.add_node(node_c)

graph = builder.compile()
# :snippet-end:

# :snippet-start: langgraph-graph-api-send-command-command-parent-invoke-py
graph.invoke({"foo": ""})
# :snippet-end:

# :remove-start:
# value "a" routes to node_b; value "b" routes to node_c.
with mock.patch.object(random, "choice", return_value="a"):
    assert graph.invoke({"foo": ""}) == {"foo": "ab"}
with mock.patch.object(random, "choice", return_value="b"):
    assert graph.invoke({"foo": ""}) == {"foo": "bc"}
print("✓ langgraph-graph-api-send-command-command-parent-graph-py")
# :remove-end:

# :remove-start:
from langchain_core.messages import AIMessage

from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode


def get_user_info(user_id: str | None) -> dict:
    return {"id": user_id, "name": "Test User"}


# :remove-end:

# :snippet-start: langgraph-graph-api-send-command-command-tool-py
from langchain.messages import ToolMessage
from langchain.tools import tool, ToolRuntime
from langgraph.types import Command


@tool
def lookup_user_info(runtime: ToolRuntime):
    """Look up user information to better assist with questions."""
    user = runtime.server_info.user if runtime.server_info else None
    user_info = get_user_info(user.identity if user is not None else None)  # [!code highlight]
    return Command(
        update={
            "user_info": user_info,
            "messages": [
                ToolMessage(
                    "Successfully looked up user information",
                    tool_call_id=runtime.tool_call_id,
                )
            ],
        }
    )
# :snippet-end:

# :remove-start:
assert lookup_user_info.name == "lookup_user_info"

tool_message = AIMessage(
    content="",
    tool_calls=[{"name": "lookup_user_info", "args": {}, "id": "call_1"}],
)

class ToolState(TypedDict):
    messages: Annotated[list, add_messages]
    user_info: dict


tool_graph = (
    StateGraph(ToolState)
    .add_node("tools", ToolNode([lookup_user_info]))
    .add_edge(START, "tools")
    .compile()
)
tool_result = tool_graph.invoke({"messages": [tool_message]})
assert tool_result["user_info"] == {"id": None, "name": "Test User"}
assert tool_result["messages"][-1].tool_call_id == "call_1"
assert tool_result["messages"][-1].content == "Successfully looked up user information"
print("✓ langgraph-graph-api-send-command-command-tool-py")
# :remove-end:
