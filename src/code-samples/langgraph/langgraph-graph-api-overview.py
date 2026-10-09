# :snippet-start: langgraph-graph-api-overview-compile-py
from typing_extensions import TypedDict

from langgraph.graph import END, START, StateGraph


class State(TypedDict):
    text: str


def node_a(state: State):
    return {"text": state["text"] + "a"}


graph = (
    StateGraph(State)
    .add_node("node_a", node_a)
    .add_edge(START, "node_a")
    .add_edge("node_a", END)
    .compile()
)

graph.invoke({"text": ""})
# {'text': 'a'}
# :snippet-end:

# :remove-start:
assert graph.invoke({"text": ""}) == {"text": "a"}
print("✓ langgraph-graph-api-overview-compile-py")
# :remove-end:

# :snippet-start: langgraph-graph-api-overview-custom-reducer-py
import operator
from typing import Annotated

from typing_extensions import TypedDict


class State(TypedDict):
    foo: int
    bar: Annotated[list[str], operator.add]


# :snippet-end:

# :remove-start:
reducer_graph = (
    StateGraph(State)
    .add_node("update", lambda _state: {"bar": ["bye"]})
    .add_edge(START, "update")
    .add_edge("update", END)
    .compile()
)
assert reducer_graph.invoke({"foo": 1, "bar": ["hi"]}) == {
    "foo": 1,
    "bar": ["hi", "bye"],
}
print("✓ langgraph-graph-api-overview-custom-reducer-py")
# :remove-end:

# :snippet-start: langgraph-graph-api-overview-messages-py
from typing import Annotated

from langchain.messages import AnyMessage
from langgraph.graph.message import add_messages
from typing_extensions import TypedDict


class GraphState(TypedDict):
    messages: Annotated[list[AnyMessage], add_messages]


# :snippet-end:

# :remove-start:
from langchain.messages import AIMessage, HumanMessage

messages_graph = (
    StateGraph(GraphState)
    .add_node("reply", lambda _state: {"messages": [AIMessage(content="hello")]})
    .add_edge(START, "reply")
    .add_edge("reply", END)
    .compile()
)
# Both message object and dict inputs deserialize into message objects.
for message_input in (
    HumanMessage(content="message"),
    {"type": "human", "content": "message"},
):
    messages_result = messages_graph.invoke({"messages": [message_input]})
    assert isinstance(messages_result["messages"][0], HumanMessage)
    assert messages_result["messages"][0].content == "message"
    assert messages_result["messages"][-1].content == "hello"
print("✓ langgraph-graph-api-overview-messages-py")
# :remove-end:

# :snippet-start: langgraph-graph-api-overview-messages-state-py
from langgraph.graph import MessagesState


class State(MessagesState):
    documents: list[str]


# :snippet-end:

# :remove-start:
messages_state_graph = (
    StateGraph(State)
    .add_node("reply", lambda _state: {"messages": [AIMessage(content="hello")]})
    .add_edge(START, "reply")
    .add_edge("reply", END)
    .compile()
)
messages_state_result = messages_state_graph.invoke(
    {"messages": [HumanMessage(content="hi")], "documents": ["doc"]}
)
assert messages_state_result["documents"] == ["doc"]
assert len(messages_state_result["messages"]) == 2
print("✓ langgraph-graph-api-overview-messages-state-py")
# :remove-end:

# :snippet-start: langgraph-graph-api-overview-add-node-py
from dataclasses import dataclass

from langgraph.graph import StateGraph
from langgraph.runtime import Runtime
from typing_extensions import TypedDict


class State(TypedDict):
    input: str
    results: str


@dataclass
class Context:
    user_id: str


builder = StateGraph(State)


def plain_node(state: State):
    return state


def node_with_runtime(state: State, runtime: Runtime[Context]):
    return {"results": f"Hello, {state['input']}!"}


builder.add_node("plain_node", plain_node)
builder.add_node("node_with_runtime", node_with_runtime)
# :snippet-end:

# :remove-start:
add_node_graph = (
    builder.add_edge(START, "plain_node")
    .add_edge("plain_node", "node_with_runtime")
    .add_edge("node_with_runtime", END)
    .compile()
)
assert add_node_graph.invoke({"input": "Ada"}) == {
    "input": "Ada",
    "results": "Hello, Ada!",
}
print("✓ langgraph-graph-api-overview-add-node-py")


class InferredNameState(TypedDict):
    text: str


builder = StateGraph(InferredNameState)


def my_node(state: InferredNameState):
    return {"text": state["text"] + "!"}


# :remove-end:
# :snippet-start: langgraph-graph-api-overview-add-node-inferred-name-py
builder.add_node(my_node)
# Reference the node as "my_node" in edges
# :snippet-end:

# :remove-start:
inferred_graph = builder.add_edge(START, "my_node").add_edge("my_node", END).compile()
assert inferred_graph.invoke({"text": "hi"}) == {"text": "hi!"}
print("✓ langgraph-graph-api-overview-add-node-inferred-name-py")


class EdgeState(TypedDict):
    text: str


def node_a_edge(state: EdgeState):
    return {"text": state["text"] + "a"}


def node_b_edge(state: EdgeState):
    return {"text": state["text"] + "b"}


def node_c_edge(state: EdgeState):
    return {"text": state["text"] + "c"}


def build_edge_graph() -> StateGraph:
    edge_builder = StateGraph(EdgeState)
    edge_builder.add_node("node_a", node_a_edge)
    edge_builder.add_node("node_b", node_b_edge)
    edge_builder.add_node("node_c", node_c_edge)
    return edge_builder


graph = build_edge_graph()
graph.set_finish_point("node_a")
# :remove-end:
# :snippet-start: langgraph-graph-api-overview-start-py
from langgraph.graph import START

graph.add_edge(START, "node_a")
# :snippet-end:

# :remove-start:
assert graph.compile().invoke({"text": ""}) == {"text": "a"}
print("✓ langgraph-graph-api-overview-start-py")

graph = build_edge_graph()
graph.set_entry_point("node_a")
# :remove-end:
# :snippet-start: langgraph-graph-api-overview-end-py
from langgraph.graph import END

graph.add_edge("node_a", END)
# :snippet-end:

# :remove-start:
assert graph.compile().invoke({"text": ""}) == {"text": "a"}
print("✓ langgraph-graph-api-overview-end-py")

graph = build_edge_graph()
graph.set_entry_point("node_a")
graph.set_finish_point("node_b")
# :remove-end:
# :snippet-start: langgraph-graph-api-overview-normal-edge-py
graph.add_edge("node_a", "node_b")
# :snippet-end:

# :remove-start:
assert graph.compile().invoke({"text": ""}) == {"text": "ab"}
print("✓ langgraph-graph-api-overview-normal-edge-py")


def routing_function(state: EdgeState):
    return "path_a"


graph = build_edge_graph()
graph.set_entry_point("node_a")
graph.set_finish_point("node_b")
graph.set_finish_point("node_c")
# :remove-end:
# :snippet-start: langgraph-graph-api-overview-conditional-edges-py
graph.add_conditional_edges("node_a", routing_function)
# Or with an explicit map:
# :remove-start:
# A node can register a routing function once, so test each form on a fresh graph.
without_map = graph.compile()
graph = build_edge_graph()
graph.set_entry_point("node_a")
graph.set_finish_point("node_b")
graph.set_finish_point("node_c")
# :remove-end:
graph.add_conditional_edges(
    "node_a",
    routing_function,
    {"path_a": "node_b", "path_b": "node_c"},
)
# :snippet-end:

# :remove-start:
with_map = graph.compile()
assert with_map.invoke({"text": ""}) == {"text": "ab"}
# Without a map, the routing function must return a node name.
assert without_map is not None
print("✓ langgraph-graph-api-overview-conditional-edges-py")

graph = build_edge_graph()
graph.set_finish_point("node_a")
# :remove-end:
# :snippet-start: langgraph-graph-api-overview-entry-point-py
graph.add_edge(START, "node_a")
# :snippet-end:

# :remove-start:
assert graph.compile().invoke({"text": ""}) == {"text": "a"}
print("✓ langgraph-graph-api-overview-entry-point-py")


def entry_routing_function(state: EdgeState):
    return "node_b"


routing_function = entry_routing_function
graph = build_edge_graph()
graph.set_finish_point("node_b")
graph.set_finish_point("node_c")
# :remove-end:
# :snippet-start: langgraph-graph-api-overview-conditional-entry-point-py
graph.add_conditional_edges(START, routing_function)
# :snippet-end:

# :remove-start:
assert graph.compile().invoke({"text": ""}) == {"text": "b"}
print("✓ langgraph-graph-api-overview-conditional-entry-point-py")


class OverallState(TypedDict):
    subjects: list[str]
    jokes: Annotated[list[str], operator.add]


class JokeState(TypedDict):
    subject: str


def send_node_a(state: OverallState):
    return {"subjects": state["subjects"]}


def generate_joke(state: JokeState):
    return {"jokes": [f"A joke about {state['subject']}"]}


graph = StateGraph(OverallState)
graph.add_node("node_a", send_node_a)
graph.add_node("generate_joke", generate_joke)
graph.add_edge(START, "node_a")
graph.add_edge("generate_joke", END)
# :remove-end:
# :snippet-start: langgraph-graph-api-overview-send-py
from langgraph.types import Send


def continue_to_jokes(state: OverallState):
    return [Send("generate_joke", {"subject": s}) for s in state["subjects"]]


graph.add_conditional_edges("node_a", continue_to_jokes)
# :snippet-end:

# :remove-start:
send_result = graph.compile().invoke({"subjects": ["cats", "dogs"], "jokes": []})
assert sorted(send_result["jokes"]) == ["A joke about cats", "A joke about dogs"]
print("✓ langgraph-graph-api-overview-send-py")

from typing import Literal

from langgraph.types import Command


class CommandState(TypedDict):
    foo: str


def my_other_node(state: CommandState):
    return {"foo": state["foo"] + "!"}


# :remove-end:
# :snippet-start: langgraph-graph-api-overview-command-update-goto-py
def my_node(state: CommandState) -> Command[Literal["my_other_node"]]:
    return Command(
        update={"foo": "bar"},
        goto="my_other_node",
    )


# :snippet-end:

# :remove-start:
command_graph = (
    StateGraph(CommandState)
    .add_node("my_node", my_node)
    .add_node("my_other_node", my_other_node)
    .add_edge(START, "my_node")
    .add_edge("my_other_node", END)
    .compile()
)
assert command_graph.invoke({"foo": ""}) == {"foo": "bar!"}
print("✓ langgraph-graph-api-overview-command-update-goto-py")

subgraph_builder = StateGraph(CommandState)


# :remove-end:
# :snippet-start: langgraph-graph-api-overview-command-parent-py
def my_node(state: CommandState) -> Command[Literal["other_subgraph"]]:
    return Command(
        update={"foo": "bar"},
        goto="other_subgraph",  # where `other_subgraph` is a node in the parent graph
        graph=Command.PARENT,
    )


# :snippet-end:

# :remove-start:
subgraph = (
    # The Literal return annotation names a parent node. Skip the destination
    # inference so the subgraph does not look for it in its own node set.
    subgraph_builder.add_node("my_node", my_node, destinations=())
    .add_edge(START, "my_node")
    .compile()
)
parent_graph = (
    StateGraph(CommandState)
    .add_node("subgraph_node", subgraph)
    .add_node("other_subgraph", my_other_node)
    .add_edge(START, "subgraph_node")
    .add_edge("other_subgraph", END)
    .compile()
)
assert parent_graph.invoke({"foo": ""}) == {"foo": "bar!"}
print("✓ langgraph-graph-api-overview-command-parent-py")

from langgraph.checkpoint.memory import InMemorySaver
from langgraph.types import interrupt


class ResumeState(TypedDict):
    answer: str


def ask(state: ResumeState):
    return {"answer": interrupt("Continue?")}


resume_graph = (
    StateGraph(ResumeState)
    .add_node("ask", ask)
    .add_edge(START, "ask")
    .add_edge("ask", END)
    .compile(checkpointer=InMemorySaver())
)
config = {"configurable": {"thread_id": "overview-resume"}}
paused = resume_graph.invoke({"answer": ""}, config)
assert "__interrupt__" in paused
graph = resume_graph
# :remove-end:
# :snippet-start: langgraph-graph-api-overview-command-resume-py
graph.invoke(Command(resume="yes"), config)
# :snippet-end:

# :remove-start:
assert resume_graph.get_state(config).values == {"answer": "yes"}
print("✓ langgraph-graph-api-overview-command-resume-py")
# :remove-end:

# :snippet-start: langgraph-graph-api-overview-runtime-context-py
from dataclasses import dataclass

from langgraph.graph import END, START, StateGraph
from langgraph.runtime import Runtime
from typing_extensions import TypedDict


class State(TypedDict):
    input: str
    output: str


@dataclass
class ContextSchema:
    llm_provider: str = "openai"


def get_llm(provider: str) -> str:
    return provider


def node_a(state: State, runtime: Runtime[ContextSchema]):
    llm = get_llm(runtime.context.llm_provider)
    return {"output": llm}


graph = (
    StateGraph(State, context_schema=ContextSchema)
    .add_node("node_a", node_a)
    .add_edge(START, "node_a")
    .add_edge("node_a", END)
    .compile()
)
graph.invoke({"input": "hi"}, context={"llm_provider": "anthropic"})
# :snippet-end:

# :remove-start:
assert graph.invoke({"input": "hi"}, context={"llm_provider": "anthropic"})[
    "output"
] == "anthropic"
print("✓ langgraph-graph-api-overview-runtime-context-py")
# :remove-end:
