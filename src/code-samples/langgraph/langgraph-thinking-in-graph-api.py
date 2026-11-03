# :snippet-start: langgraph-thinking-in-graph-api-state-py
from typing import Literal, TypedDict


class EmailClassification(TypedDict):
    intent: Literal["question", "bug", "billing", "feature", "complex"]
    urgency: Literal["low", "medium", "high", "critical"]
    topic: str
    summary: str


class EmailAgentState(TypedDict):
    email_content: str
    sender_email: str
    email_id: str
    classification: EmailClassification | None
    search_results: list[str] | None  # Docs or ticket context
    draft_response: str | None


# :snippet-end:

# :remove-start:
assert set(EmailAgentState.__annotations__) == {
    "email_content",
    "sender_email",
    "email_id",
    "classification",
    "search_results",
    "draft_response",
}
print("✓ langgraph-thinking-in-graph-api-state-py validated")
# :remove-end:

# :snippet-start: langgraph-thinking-in-graph-api-nodes-py
from typing import Literal

from langgraph.graph import END
from langgraph.types import Command, interrupt


def read_email(state: EmailAgentState) -> dict:
    """Parse and normalize the incoming email."""
    return {}


def classify_intent(
    state: EmailAgentState,
) -> Command[Literal["search_documentation", "bug_tracking", "draft_response"]]:
    """Classify intent and urgency, then route to gather context or draft."""
    # Placeholder: replace with a real LLM call.
    # This heuristic matches the try-out sample so interrupt() runs.
    lowered = state["email_content"].lower()
    if "charged" in lowered or "billing" in lowered:
        classification: EmailClassification = {
            "intent": "billing",
            "urgency": "high",
            "topic": "billing",
            "summary": "Customer reports a billing problem",
        }
    elif "crash" in lowered or "bug" in lowered:
        classification = {
            "intent": "bug",
            "urgency": "medium",
            "topic": "product bug",
            "summary": "Customer reports a bug",
        }
    else:
        classification = {
            "intent": "question",
            "urgency": "low",
            "topic": "general",
            "summary": "Customer question",
        }

    if classification["intent"] in ("question", "feature"):
        goto = "search_documentation"
    elif classification["intent"] == "bug":
        goto = "bug_tracking"
    else:
        goto = "draft_response"

    return Command(update={"classification": classification}, goto=goto)


def search_documentation(
    state: EmailAgentState,
) -> Command[Literal["draft_response"]]:
    """Search knowledge base for relevant information."""
    classification = state.get("classification") or {}
    topic = classification.get("topic", "general")
    return Command(
        update={"search_results": [f"Docs related to {topic}"]},
        goto="draft_response",
    )


def bug_tracking(state: EmailAgentState) -> Command[Literal["draft_response"]]:
    """Create or update a bug tracking ticket."""
    ticket_id = "BUG-12345"
    return Command(
        update={"search_results": [f"Bug ticket {ticket_id} created"]},
        goto="draft_response",
    )


def draft_response(
    state: EmailAgentState,
) -> Command[Literal["human_review", "send_reply"]]:
    """Draft a reply, then route to review or send."""
    classification = state.get("classification") or {}
    context = state.get("search_results") or []
    draft = f"Thanks for your email about {classification.get('topic', 'your request')}."
    if context:
        draft += f" Context: {context[0]}"

    needs_review = (
        classification.get("intent") in ("billing", "complex")
        or classification.get("urgency") in ("high", "critical")
    )
    goto = "human_review" if needs_review else "send_reply"
    return Command(update={"draft_response": draft}, goto=goto)


def human_review(
    state: EmailAgentState,
) -> Command[Literal["send_reply", END]]:
    """Pause for human review, then send or end."""
    classification = state.get("classification") or {}

    # Nodes re-run from the start on resume. Keep work before interrupt() idempotent.
    human_decision = interrupt(
        {
            "email_id": state.get("email_id", ""),
            "original_email": state.get("email_content", ""),
            "draft_response": state.get("draft_response", ""),
            "urgency": classification.get("urgency"),
            "intent": classification.get("intent"),
            "action": "Please review and approve/edit this response",
        }
    )

    if human_decision.get("approved"):
        return Command(
            update={
                "draft_response": human_decision.get(
                    "edited_response", state.get("draft_response", "")
                )
            },
            goto="send_reply",
        )
    # Rejection: human handles the email outside the graph
    return Command(update={}, goto=END)


def send_reply(state: EmailAgentState) -> dict:
    """Send the email response."""
    return {}


# :snippet-end:

# :remove-start:
_billing_state: EmailAgentState = {
    "email_content": "I was charged twice for my subscription! This is urgent!",
    "sender_email": "customer@example.com",
    "email_id": "email_123",
    "classification": None,
    "search_results": None,
    "draft_response": None,
}
_cmd = classify_intent(_billing_state)
assert _cmd.goto == "draft_response"
assert _cmd.update["classification"]["intent"] == "billing"
print("✓ langgraph-thinking-in-graph-api-nodes-py validated")
# :remove-end:

# :remove-start:
from langgraph.graph import StateGraph

workflow = StateGraph(EmailAgentState)
# :remove-end:

# :snippet-start: langgraph-thinking-in-graph-api-retry-policy-py
from langgraph.types import RetryPolicy

workflow.add_node(
    "search_documentation",
    search_documentation,
    retry_policy=RetryPolicy(max_attempts=3),
)
# :snippet-end:

# :remove-start:
assert workflow.nodes["search_documentation"].retry_policy.max_attempts == 3
print("✓ langgraph-thinking-in-graph-api-retry-policy-py validated")
# :remove-end:

# :snippet-start: langgraph-thinking-in-graph-api-graph-py
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.types import RetryPolicy

workflow = StateGraph(EmailAgentState)

workflow.add_node("read_email", read_email)
workflow.add_node("classify_intent", classify_intent)
workflow.add_node(
    "search_documentation",
    search_documentation,
    retry_policy=RetryPolicy(max_attempts=3),
)
workflow.add_node(
    "bug_tracking",
    bug_tracking,
    retry_policy=RetryPolicy(max_attempts=3),
)
workflow.add_node("draft_response", draft_response)
workflow.add_node("human_review", human_review)
workflow.add_node("send_reply", send_reply)

workflow.add_edge(START, "read_email")
workflow.add_edge("read_email", "classify_intent")
workflow.add_edge("send_reply", END)

checkpointer = InMemorySaver()
app = workflow.compile(checkpointer=checkpointer)
# :snippet-end:

# :remove-start:
_graph_nodes = set(app.get_graph().nodes)
assert {
    "read_email",
    "classify_intent",
    "search_documentation",
    "bug_tracking",
    "draft_response",
    "human_review",
    "send_reply",
} <= _graph_nodes
print("✓ langgraph-thinking-in-graph-api-graph-py validated")
# :remove-end:

# :snippet-start: langgraph-thinking-in-graph-api-try-out-py
from langgraph.types import Command

config = {"configurable": {"thread_id": "customer_123"}}

result = app.invoke(
    {
        "email_content": "I was charged twice for my subscription! This is urgent!",
        "sender_email": "customer@example.com",
        "email_id": "email_123",
    },
    config,
)
# The graph pauses at human_review when urgency is high

app.invoke(
    Command(
        resume={
            "approved": True,
            "edited_response": "We sincerely apologize for the double charge. I've initiated an immediate refund...",
        }
    ),
    config,
)
# :snippet-end:

# :remove-start:
assert "__interrupt__" in result
_payload = result["__interrupt__"][0].value
assert _payload["intent"] == "billing"
assert _payload["urgency"] == "high"
_snapshot = app.get_state(config)
assert not _snapshot.next
assert _snapshot.values["draft_response"].startswith("We sincerely apologize")
assert _snapshot.values["classification"]["intent"] == "billing"

# Rejection path ends the run without sending.
_reject_config = {"configurable": {"thread_id": "customer_456"}}
app.invoke(
    {
        "email_content": "I was charged twice for my subscription! This is urgent!",
        "sender_email": "customer@example.com",
        "email_id": "email_456",
    },
    _reject_config,
)
app.invoke(Command(resume={"approved": False}), _reject_config)
assert not app.get_state(_reject_config).next
print("✓ langgraph-thinking-in-graph-api-try-out-py validated")
# :remove-end:
