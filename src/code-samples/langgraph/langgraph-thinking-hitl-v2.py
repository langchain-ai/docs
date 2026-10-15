# :snippet-start: langgraph-thinking-hitl-v2-py
from typing import TypedDict

from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.types import Command, interrupt


class EmailState(TypedDict):
    email_content: str
    response_text: str | None


def human_review_node(state: EmailState):
    interrupt(
        {
            "approved": False,
            "edited_response": state.get("response_text") or "",
        }
    )
    return {"response_text": "placeholder"}


app = (
    StateGraph(EmailState)
    .add_node("human_review", human_review_node)
    .add_edge(START, "human_review")
    .add_edge("human_review", END)
    .compile(checkpointer=InMemorySaver())
)

initial_state = {
    "email_content": "I was charged twice for my subscription! This is urgent!",
    "response_text": "Draft response",
}

# Run with a thread_id for persistence
config = {"configurable": {"thread_id": "customer_123"}}
stream = app.stream_events(initial_state, config, version="v3")
_ = stream.output  # drive the stream to completion
# The graph will pause at human_review
print(f"human review interrupt:{stream.interrupts}")

human_response = Command(
    resume={
        "approved": True,
        "edited_response": "We sincerely apologize for the double charge. I've initiated an immediate refund...",
    }
)

# Resume execution
resumed = app.stream_events(human_response, config, version="v3")
final_state = resumed.output
print("Email sent successfully!")
# :snippet-end:

# :remove-start:
if __name__ == "__main__":
    assert stream.interrupted
    assert final_state["response_text"]
    print("✓ langgraph-thinking-hitl-v2")
# :remove-end:
