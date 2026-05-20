# :remove-start:
from typing import TypedDict

from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.types import Command, interrupt


class State(TypedDict):
    approved: bool


def approval_node(state: State):
    approved = interrupt("Do you approve this action?")
    return {"approved": approved}


graph = (
    StateGraph(State)
    .add_node("approval", approval_node)
    .add_edge(START, "approval")
    .add_edge("approval", END)
    .compile(checkpointer=InMemorySaver())
)
# :remove-end:

# :snippet-start: langgraph-interrupts-resume-v2-py
from langgraph.types import Command

# Initial run - hits the interrupt and pauses
# thread_id is the persistent pointer (stores a stable ID in production)
config = {"configurable": {"thread_id": "thread-1"}}
stream = graph.stream_events({"input": "data"}, config=config, version="v3")

# Drain the stream to drive the run; stream.output awaits the final state.
final = stream.output

# stream.interrupted is True when the run paused for human input, and
# stream.interrupts contains the payloads passed to interrupt().
if stream.interrupted:
    print(stream.interrupts)
    # > (Interrupt(value='Do you approve this action?'),)

# Resume with the human's response
# The resume payload becomes the return value of interrupt() inside the node
resumed = graph.stream_events(Command(resume=True), config=config, version="v3")
final = resumed.output
# :snippet-end:

# :remove-start:
if __name__ == "__main__":
    assert stream.interrupted
    resumed2 = graph.stream_events(Command(resume=True), config=config, version="v3")
    assert resumed2.output["approved"]
    print("✓ langgraph-interrupts-resume-v2")
# :remove-end:
