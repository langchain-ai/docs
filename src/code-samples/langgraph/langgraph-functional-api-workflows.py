# :snippet-start: langgraph-functional-api-workflows-simple-py
from langchain_core.utils.uuid import uuid7
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.func import entrypoint, task


@task
def is_even(number: int) -> bool:
    return number % 2 == 0


@task
def format_message(is_even: bool) -> str:
    return "The number is even." if is_even else "The number is odd."


checkpointer = InMemorySaver()


@entrypoint(checkpointer=checkpointer)
def workflow(inputs: dict) -> str:
    even = is_even(inputs["number"]).result()
    return format_message(even).result()


config = {"configurable": {"thread_id": str(uuid7())}}
result = workflow.invoke({"number": 7}, config=config)
print(result)
# :snippet-end:

# :remove-start:
assert result == "The number is odd.", result
# :remove-end:

# :snippet-start: langgraph-functional-api-workflows-dict-py
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.func import entrypoint

checkpointer = InMemorySaver()


@entrypoint(checkpointer=checkpointer)
def my_workflow(inputs: dict) -> dict:
    value = inputs["value"]
    another_value = inputs["another_value"]
    return {"sum": value + another_value}


config = {"configurable": {"thread_id": "1"}}
my_workflow.invoke({"value": 1, "another_value": 2}, config)
# :snippet-end:

# :remove-start:
assert my_workflow.invoke(
    {"value": 1, "another_value": 2}, {"configurable": {"thread_id": "2"}}
) == {"sum": 3}
# :remove-end:

# :snippet-start: langgraph-functional-api-workflows-parallel-py
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.func import entrypoint, task

checkpointer = InMemorySaver()


@task
def add_one(number: int) -> int:
    return number + 1


@entrypoint(checkpointer=checkpointer)
def workflow(numbers: list[int]) -> list[int]:
    futures = [add_one(i) for i in numbers]
    return [f.result() for f in futures]
# :snippet-end:

# :remove-start:
assert workflow.invoke([1, 2, 3], {"configurable": {"thread_id": "1"}}) == [2, 3, 4]
# :remove-end:

# :snippet-start: langgraph-functional-api-workflows-graph-py
from typing import TypedDict

from langchain_core.runnables import RunnableConfig
from langchain_core.utils.uuid import uuid7
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.func import entrypoint
from langgraph.graph import START, StateGraph


class State(TypedDict):
    foo: int


def double(state: State) -> State:
    return {"foo": state["foo"] * 2}


builder = StateGraph(State)
builder.add_node("double", double)
builder.add_edge(START, "double")
graph = builder.compile()

checkpointer = InMemorySaver()


@entrypoint(checkpointer=checkpointer)
def workflow(x: int, *, config: RunnableConfig) -> dict:
    result = graph.invoke({"foo": x}, config)
    return {"bar": result["foo"]}


config = {"configurable": {"thread_id": str(uuid7())}}
print(workflow.invoke(5, config=config))  # {'bar': 10}
# :snippet-end:

# :remove-start:
assert workflow.invoke(5, config={"configurable": {"thread_id": str(uuid7())}}) == {
    "bar": 10
}
# :remove-end:

# :snippet-start: langgraph-functional-api-workflows-nested-py
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.func import entrypoint

checkpointer = InMemorySaver()


@entrypoint()  # Inherits the checkpointer when invoked from my_workflow
def some_other_workflow(inputs: dict) -> int:
    return inputs["value"]


@entrypoint(checkpointer=checkpointer)
def my_workflow(inputs: dict) -> int:
    value = some_other_workflow.invoke({"value": 1})
    return value
# :snippet-end:

# :remove-start:
assert my_workflow.invoke({}, {"configurable": {"thread_id": "1"}}) == 1
# :remove-end:

# :snippet-start: langgraph-functional-api-workflows-nested-extended-py
from langchain_core.utils.uuid import uuid7
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.func import entrypoint

checkpointer = InMemorySaver()


@entrypoint()
def multiply(inputs: dict) -> int:
    return inputs["a"] * inputs["b"]


@entrypoint(checkpointer=checkpointer)
def main(inputs: dict) -> dict:
    result = multiply.invoke({"a": inputs["x"], "b": inputs["y"]})
    return {"product": result}


config = {"configurable": {"thread_id": str(uuid7())}}
print(main.invoke({"x": 6, "y": 7}, config=config))  # {'product': 42}
# :snippet-end:

# :remove-start:
assert main.invoke({"x": 6, "y": 7}, config=config) == {"product": 42}
# :remove-end:

# :snippet-start: langgraph-functional-api-workflows-parallel-llm-py
from langchain.chat_models import init_chat_model
from langchain_core.utils.uuid import uuid7
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.func import entrypoint, task

# :remove-start:
import os

os.environ.setdefault("ANTHROPIC_API_KEY", "sk-ant-test-key")
# :remove-end:
model = init_chat_model("claude-sonnet-4-6")
# :remove-start:
from langchain.messages import AIMessage
from langchain_core.language_models.fake_chat_models import GenericFakeChatModel

model = GenericFakeChatModel(
    messages=iter(
        [
            AIMessage(content="A paragraph."),
            AIMessage(content="A paragraph."),
            AIMessage(content="A paragraph."),
        ]
    )
)
# :remove-end:


@task
def generate_paragraph(topic: str) -> str:
    response = model.invoke([
        {"role": "system", "content": "You are a helpful assistant that writes educational paragraphs."},
        {"role": "user", "content": f"Write a paragraph about {topic}."}
    ])
    return response.text


checkpointer = InMemorySaver()


@entrypoint(checkpointer=checkpointer)
def workflow(topics: list[str]) -> str:
    futures = [generate_paragraph(topic) for topic in topics]
    paragraphs = [f.result() for f in futures]
    return "\n\n".join(paragraphs)


config = {"configurable": {"thread_id": str(uuid7())}}
result = workflow.invoke(["quantum computing", "climate change", "history of aviation"], config=config)
print(result)
# :snippet-end:

# :remove-start:
assert result == "A paragraph.\n\nA paragraph.\n\nA paragraph.", result
print("✓ langgraph-functional-api-workflows")
# :remove-end:
