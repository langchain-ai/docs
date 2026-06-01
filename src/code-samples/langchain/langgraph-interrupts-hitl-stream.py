# :remove-start:
from typing import TypedDict

from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.types import Command, interrupt


class StreamState(TypedDict):
    step: int
    done: bool


def first_interrupt(state: StreamState):
    interrupt("first question")
    return {"step": 1}


def second_interrupt(state: StreamState):
    interrupt("second question")
    return {"done": True}


graph = (
    StateGraph(StreamState)
    .add_node("first", first_interrupt)
    .add_node("second", second_interrupt)
    .add_edge(START, "first")
    .add_edge("first", "second")
    .add_edge("second", END)
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

stream_input: dict | Command = initial_input

while True:
    stream = graph.stream_events(stream_input, config=config, version="v3")

    # Stream LLM message chunks (including any in subgraphs) as they arrive.
    for message in stream.messages:
        for token in message.text:
            display_streaming_content(token)

    # After the run finishes (or pauses), check for interrupts and resume.
    if not stream.interrupted:
        final_state = stream.output
        break

    interrupt_info = stream.interrupts[0].value
    user_response = get_user_input(interrupt_info)
    stream_input = Command(resume=user_response)
# :snippet-end:

# :remove-start:
if __name__ == "__main__":
    test_config = {"configurable": {"thread_id": "stream-test"}}
    stream_input: dict | Command = {}
    resume_rounds = 0
    while True:
        test_stream = graph.stream_events(stream_input, config=test_config, version="v3")
        _ = list(test_stream.messages)
        if not test_stream.interrupted:
            final = test_stream.output
            break
        stream_input = Command(resume="ok")
        resume_rounds += 1
    assert resume_rounds == 2
    assert final["done"]
    print("✓ langgraph-interrupts-hitl-stream")
# :remove-end:
