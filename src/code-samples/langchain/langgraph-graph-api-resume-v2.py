# :snippet-start: langgraph-graph-api-resume-v2-py
from typing import TypedDict

from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.types import Command, interrupt


class State(TypedDict):
    messages: list[dict]


def human_review(state: State):
    # Pauses the graph and waits for a value
    answer = interrupt("Do you approve?")
    return {"messages": [{"role": "user", "content": answer}]}


graph = (
    StateGraph(State)
    .add_node("human_review", human_review)
    .add_edge(START, "human_review")
    .add_edge("human_review", END)
    .compile(checkpointer=InMemorySaver())
)

config = {"configurable": {"thread_id": "graph-api-resume"}}

# First invocation - hits the interrupt and pauses
result = graph.invoke({"messages": []}, config, version="v2")
print(result.interrupts)

# Resume with a value - the interrupt() call returns "yes"
result = graph.invoke(Command(resume="yes"), config, version="v2")
# :snippet-end:

# :remove-start:
if __name__ == "__main__":
    paused = graph.invoke({"messages": []}, config, version="v2")
    assert paused.interrupts
    finished = graph.invoke(Command(resume="yes"), config, version="v2")
    assert finished.value["messages"][-1]["content"] == "yes"
    print("✓ langgraph-graph-api-resume-v2")
# :remove-end:
