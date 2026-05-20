# :remove-start:
from typing import TypedDict

from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.types import Command, interrupt


class StreamState(TypedDict):
    done: bool


def stream_node(state: StreamState):
    interrupt("wait for user")
    return {"done": True}


graph = (
    StateGraph(StreamState)
    .add_node("n", stream_node)
    .add_edge(START, "n")
    .add_edge("n", END)
    .compile(checkpointer=InMemorySaver())
)

config = {"configurable": {"thread_id": "stream-1"}}
initial_input: dict = {}


def display_streaming_content(content: str) -> None:
    pass


def get_user_input(interrupt_info: object) -> str:
    return "ok"
# :remove-end:

# :snippet-start: langgraph-interrupts-hitl-stream-py
from langchain.messages import AIMessageChunk
from langgraph.types import Command

for chunk in graph.stream(
    initial_input,
    stream_mode=["messages", "updates", "values"],
    subgraphs=True,
    config=config,
    version="v2",
):
    if chunk["type"] == "messages":
        msg, _ = chunk["data"]
        if isinstance(msg, AIMessageChunk) and msg.content:
            display_streaming_content(msg.content)

    elif chunk["type"] == "values" and chunk.get("interrupts"):
        interrupt_info = chunk["interrupts"][0].value
        user_response = get_user_input(interrupt_info)
        initial_input = Command(resume=user_response)
        break

    elif chunk["type"] == "updates":
        current_node = list(chunk["data"].keys())[0]
# :snippet-end:

# :remove-start:
if __name__ == "__main__":
    saw_interrupt = False
    for chunk in graph.stream(
        {},
        stream_mode=["values"],
        config=config,
        version="v2",
    ):
        if chunk["type"] == "values" and chunk.get("interrupts"):
            saw_interrupt = True
            break
    assert saw_interrupt
    print("✓ langgraph-interrupts-hitl-stream")
# :remove-end:
