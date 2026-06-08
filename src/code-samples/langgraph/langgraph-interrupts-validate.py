import os
import tempfile

def _sqlite_db_path(filename: str) -> str:
    """Use a temp DB in CI; keep the documented filename for local runs."""
    if os.environ.get("CI") or os.environ.get("GITHUB_ACTIONS"):
        fd, path = tempfile.mkstemp(prefix="langgraph-", suffix=f"-{filename}")
        os.close(fd)
        return path
    return filename



# :snippet-start: langgraph-interrupts-validate-py
import sqlite3
from typing import TypedDict

from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.graph import END, START, StateGraph
from langgraph.types import Command, interrupt


class FormState(TypedDict):
    age: int | None


def get_age_node(state: FormState):
    prompt = "What is your age?"

    while True:
        answer = interrupt(prompt)

        if isinstance(answer, int) and answer > 0:
            return {"age": answer}

        prompt = f"'{answer}' is not a valid age. Please enter a positive number."


builder = StateGraph(FormState)
builder.add_node("collect_age", get_age_node)
builder.add_edge(START, "collect_age")
builder.add_edge("collect_age", END)

checkpointer = SqliteSaver(sqlite3.connect("forms.db"))
# :remove-start:
_db_path = _sqlite_db_path("forms.db")
_conn = sqlite3.connect(_db_path, check_same_thread=False)
checkpointer = SqliteSaver(_conn)
# :remove-end:
graph = builder.compile(checkpointer=checkpointer)

config = {"configurable": {"thread_id": "form-1"}}
first = graph.stream_events({"age": None}, config=config, version="v3")
_ = first.output  # drive the stream to completion
print(first.interrupts)  # -> (Interrupt(value='What is your age?', ...),)

# Provide invalid data; the node re-prompts
retry = graph.stream_events(Command(resume="thirty"), config=config, version="v3")
_ = retry.output  # drive the stream to completion
print(retry.interrupts)  # -> (Interrupt(value="'thirty' is not a valid age...", ...),)

# Provide valid data; loop exits and state updates
final = graph.stream_events(Command(resume=30), config=config, version="v3")
print(final.output["age"])  # -> 30
# :snippet-end:

# :remove-start:
if __name__ == "__main__":
    assert final.output["age"] == 30
    _conn.close()
    if os.environ.get("CI") or os.environ.get("GITHUB_ACTIONS"):
        os.unlink(_db_path)
    print("✓ langgraph-interrupts-validate")
# :remove-end:
