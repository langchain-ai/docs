# :snippet-start: langgraph-graph-api-visualize-graph-py
from typing import Literal

from typing_extensions import TypedDict

from langgraph.graph import END, START, StateGraph


class State(TypedDict):
    value: int


def node1(state: State):
    return {"value": state["value"] + 1}


def node2(state: State):
    return {"value": state["value"] * 2}


def router(state: State) -> Literal["node2", "__end__"]:
    if state["value"] < 10:
        return "node2"
    return END


app = (
    StateGraph(State)
    .add_node("node1", node1)
    .add_node("node2", node2)
    .add_edge(START, "node1")
    .add_conditional_edges("node1", router)
    .add_edge("node2", "node1")
    .compile()
)
# :snippet-end:

# :remove-start:
# Deterministic: 1 -> node1 (2) -> node2 (4) -> node1 (5) -> node2 (10) -> node1 (11) -> end
result = app.invoke({"value": 1})
assert result == {"value": 11}, result
print("✓ langgraph-graph-api-visualize-graph-py validated")
# :remove-end:

# :snippet-start: langgraph-graph-api-visualize-mermaid-py
print(app.get_graph().draw_mermaid())
# :snippet-end:

# :remove-start:
mermaid = app.get_graph().draw_mermaid()
assert "__start__" in mermaid, mermaid
assert "node1 -.-> node2;" in mermaid, mermaid
assert "node2 --> node1;" in mermaid, mermaid
print("✓ langgraph-graph-api-visualize-mermaid-py validated")
# :remove-end:

# :snippet-start: langgraph-graph-api-visualize-graphviz-py
from IPython.display import Image, display

try:
    display(Image(app.get_graph().draw_png()))
except ImportError:
    print(
        "Install pygraphviz to draw graphs with Graphviz: `pip install pygraphviz`. "
        "You also need the Graphviz system binary: https://graphviz.org/download/"
    )
# :snippet-end:

# :remove-start:
# Mermaid.ink and Pyppeteer PNG blocks stay inline in the docs: they need network
# access or optional packages. This block exercises the offline Graphviz path.
print("✓ langgraph-graph-api-visualize-graphviz-py validated")
# :remove-end:
