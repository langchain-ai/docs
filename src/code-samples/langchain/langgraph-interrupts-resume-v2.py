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
result = graph.invoke({"input": "data"}, config=config, version="v2")

# result is a GraphOutput with .value and .interrupts
# .interrupts contains the payloads passed to interrupt()
print(result.interrupts)
# > (Interrupt(value='Do you approve this action?'),)

# Resume with the human's response
# The resume payload becomes the return value of interrupt() inside the node
graph.invoke(Command(resume=True), config=config, version="v2")
# :snippet-end:

# :remove-start:
if __name__ == "__main__":
    assert result.interrupts
    results2 = graph.invoke(Command(resume=True), config=config, version="v2")
    assert results2.value["approved"]
    print("✓ langgraph-interrupts-resume-v2")
# :remove-end:
