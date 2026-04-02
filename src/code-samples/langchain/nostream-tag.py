"""Example of using nostream tag to exclude LLM output from the stream."""

# :snippet-start: nostream-tag-py
from typing import Any, TypedDict

from langchain_anthropic import ChatAnthropic
from langgraph.graph import START, StateGraph

stream_model = ChatAnthropic(model_name="claude-3-haiku-20240307")
internal_model = ChatAnthropic(model_name="claude-3-haiku-20240307").with_config(
    {"tags": ["nostream"]}
)


class State(TypedDict):
    topic: str
    answer: str
    notes: str


def answer(state: State) -> dict[str, Any]:
    r = stream_model.invoke(
        [{"role": "user", "content": f"Reply briefly about {state['topic']}"}]
    )
    return {"answer": r.content}


def internal_notes(state: State) -> dict[str, Any]:
    # Tokens from this model are omitted from stream_mode="messages" because of nostream
    r = internal_model.invoke(
        [{"role": "user", "content": f"Private notes on {state['topic']}"}]
    )
    return {"notes": r.content}


graph = (
    StateGraph(State)
    .add_node("write_answer", answer)
    .add_node("internal_notes", internal_notes)
    .add_edge(START, "write_answer")
    .add_edge("write_answer", "internal_notes")
    .compile()
)

initial_state: State = {"topic": "AI", "answer": "", "notes": ""}
stream = graph.stream(initial_state, stream_mode="messages")

# :remove-start:
streamed_nodes: list[str] = []
for msg, metadata in stream:
    if getattr(msg, "content", None) and isinstance(metadata, dict):
        streamed_nodes.append(metadata["langgraph_node"])
assert "internal_notes" not in streamed_nodes, (
    "No tokens from the nostream model should appear in the stream"
)

if __name__ == "__main__":
    print("\n✓ nostream tag example works as expected")
# :remove-end:
# :snippet-end:
