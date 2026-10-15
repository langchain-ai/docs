# :snippet-start: langgraph-interrupts-validate-conditional-edge-pattern-py
from typing import TypedDict

from langgraph.graph import END, START, StateGraph
from langgraph.types import interrupt


class FormState(TypedDict):
    age: int | None
    pending_question: str | None


def get_age_node(state: FormState):
    question = state.get("pending_question") or "What is your age?"
    answer = interrupt(question)  # called exactly once per invocation
    if isinstance(answer, int) and answer > 0:
        return {"age": answer, "pending_question": None}
    return {"pending_question": f"'{answer}' is not a valid age. Please enter a positive number."}


def route(state: FormState):
    return END if state.get("age") is not None else "collect_age"


builder = StateGraph(FormState)
builder.add_node("collect_age", get_age_node)
builder.add_edge(START, "collect_age")
builder.add_conditional_edges("collect_age", route)
# :snippet-end:

# :remove-start:
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.types import Command

_pattern_graph = builder.compile(checkpointer=InMemorySaver())
_pattern_config = {"configurable": {"thread_id": "form-pattern-test"}}
_pattern_first = _pattern_graph.stream_events(
    {"age": None, "pending_question": None},
    config=_pattern_config,
    version="v3",
)
_ = _pattern_first.output
assert _pattern_first.interrupts

_pattern_retry = _pattern_graph.stream_events(
    Command(resume="thirty"), config=_pattern_config, version="v3"
)
_ = _pattern_retry.output
assert _pattern_retry.interrupts

_pattern_final = _pattern_graph.stream_events(
    Command(resume=30), config=_pattern_config, version="v3"
)
assert _pattern_final.output["age"] == 30
# :remove-end:

# :snippet-start: langgraph-interrupts-validate-conditional-edge-py
from typing import TypedDict

from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.types import Command, interrupt


class FormState(TypedDict):
    age: int | None
    pending_question: str | None


def get_age_node(state: FormState):
    question = state.get("pending_question") or "What is your age?"
    answer = interrupt(question)  # called exactly once per node invocation
    print(f"I got {answer}")  # runs exactly once per resume
    if isinstance(answer, int) and answer > 0:
        return {"age": answer, "pending_question": None}
    return {"pending_question": f"'{answer}' is not a valid age. Please enter a positive number."}


def route(state: FormState):
    # Loop back to collect_age until we have a valid age
    return END if state.get("age") is not None else "collect_age"


builder = StateGraph(FormState)
builder.add_node("collect_age", get_age_node)
builder.add_edge(START, "collect_age")
builder.add_conditional_edges("collect_age", route)

checkpointer = InMemorySaver()
graph = builder.compile(checkpointer=checkpointer)

config = {"configurable": {"thread_id": "form-1"}}
first = graph.stream_events({"age": None, "pending_question": None}, config=config, version="v3")
_ = first.output  # drive the stream to completion
print(first.interrupts)  # -> (Interrupt(value='What is your age?', ...),)

# Provide invalid data; the node re-prompts via the conditional edge
retry = graph.stream_events(Command(resume="thirty"), config=config, version="v3")
_ = retry.output
print(retry.interrupts)  # -> (Interrupt(value="'thirty' is not a valid age...", ...),)

# Provide valid data; route() returns END and the graph finishes
final = graph.stream_events(Command(resume=30), config=config, version="v3")
print(final.output["age"])  # -> 30
# :snippet-end:

# :remove-start:
if __name__ == "__main__":
    assert final.output["age"] == 30
    print("✓ langgraph-interrupts-validate-conditional-edge")
# :remove-end:
