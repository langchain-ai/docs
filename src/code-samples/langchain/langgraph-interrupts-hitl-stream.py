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
from langgraph.types import Command

stream = graph.stream_events(initial_input, config=config, version="v3")

# Stream LLM message chunks (including any in subgraphs) as they arrive.
for message in stream.messages:
    for token in message.text:
        display_streaming_content(token)

# After the run finishes (or pauses), check for interrupts and resume.
if stream.interrupted:
    interrupt_info = stream.interrupts[0].value
    user_response = get_user_input(interrupt_info)
    stream = graph.stream_events(
        Command(resume=user_response), config=config, version="v3"
    )
    final_state = stream.output
# :snippet-end:

# :remove-start:
if __name__ == "__main__":
    test_config = {"configurable": {"thread_id": "stream-test"}}
    test_stream = graph.stream_events({}, config=test_config, version="v3")
    _ = test_stream.output  # drive to completion
    assert test_stream.interrupted
    print("✓ langgraph-interrupts-hitl-stream")
# :remove-end:
