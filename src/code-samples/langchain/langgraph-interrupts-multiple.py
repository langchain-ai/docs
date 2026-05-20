# :snippet-start: langgraph-interrupts-multiple-py
from typing import Annotated, TypedDict
import operator

from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.types import Command, interrupt


class State(TypedDict):
    vals: Annotated[list[str], operator.add]


def node_a(state):
    answer = interrupt("question_a")
    return {"vals": [f"a:{answer}"]}


def node_b(state):
    answer = interrupt("question_b")
    return {"vals": [f"b:{answer}"]}


graph = (
    StateGraph(State)
    .add_node("a", node_a)
    .add_node("b", node_b)
    .add_edge(START, "a")
    .add_edge(START, "b")
    .add_edge("a", END)
    .add_edge("b", END)
    .compile(checkpointer=InMemorySaver())
)

config = {"configurable": {"thread_id": "1"}}

# Step 1: invoke with version="v2" to get typed GraphOutput
# Both parallel nodes hit interrupt() and pause
interrupted_result = graph.invoke({"vals": []}, config, version="v2")
print(interrupted_result.interrupts)
# > (Interrupt(value='question_a', id='...'), Interrupt(value='question_b', id='...'))

# Step 2: resume all pending interrupts at once
resume_map = {
    i.id: f"answer for {i.value}" for i in interrupted_result.interrupts
}
result = graph.invoke(Command(resume=resume_map), config, version="v2")

print("Final state:", result.value)
# Final state: {'vals': ['a:answer for question_a', 'b:answer for question_b']}
# :snippet-end:

# :remove-start:
if __name__ == "__main__":
    assert graph is not None
    print("✓ langgraph-interrupts-multiple")
# :remove-end:
