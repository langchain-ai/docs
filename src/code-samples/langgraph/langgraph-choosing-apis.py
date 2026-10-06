# :snippet-start: langgraph-choosing-apis-graph-py
# :codegroup-tab: Graph API
from typing_extensions import TypedDict

from langgraph.graph import END, START, StateGraph


class State(TypedDict):
    number: int
    is_even: bool
    message: str


def check_even(state: State):
    return {"is_even": state["number"] % 2 == 0}


def format_message(state: State):
    return {
        "message": (
            "The number is even." if state["is_even"] else "The number is odd."
        )
    }


workflow = StateGraph(State)
workflow.add_node("check_even", check_even)
workflow.add_node("format_message", format_message)
workflow.add_edge(START, "check_even")
workflow.add_edge("check_even", "format_message")
workflow.add_edge("format_message", END)
graph = workflow.compile()

graph.invoke({"number": 7})
# :snippet-end:

# :remove-start:
assert graph.invoke({"number": 7})["message"] == "The number is odd."
# :remove-end:

# :snippet-start: langgraph-choosing-apis-functional-py
# :codegroup-tab: Functional API
from langgraph.func import entrypoint, task


@task
def is_even(number: int) -> bool:
    return number % 2 == 0


@task
def format_message(is_even: bool) -> str:
    return "The number is even." if is_even else "The number is odd."


@entrypoint()
def workflow(inputs: dict) -> str:
    even = is_even(inputs["number"]).result()
    return format_message(even).result()


workflow.invoke({"number": 7})
# :snippet-end:

# :remove-start:
assert workflow.invoke({"number": 7}) == "The number is odd."
print("✓ langgraph-choosing-apis")
# :remove-end:
