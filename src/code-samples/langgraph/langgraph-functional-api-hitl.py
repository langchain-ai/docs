# :snippet-start: langgraph-functional-api-hitl-pause-py
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.func import entrypoint, task
from langgraph.types import Command, interrupt


@task
def step_1(input_query):
    """Append bar."""
    return f"{input_query} bar"


@task
def human_feedback(input_query):
    """Append user input."""
    feedback = interrupt(f"Please provide feedback: {input_query}")
    return f"{input_query} {feedback}"


@task
def step_3(input_query):
    """Append qux."""
    return f"{input_query} qux"


checkpointer = InMemorySaver()


@entrypoint(checkpointer=checkpointer)
def workflow(input_query):
    result_1 = step_1(input_query).result()
    result_2 = human_feedback(result_1).result()
    result_3 = step_3(result_2).result()
    return result_3


config = {"configurable": {"thread_id": "1"}}

stream = workflow.stream_events("foo", config, version="v3")
_ = stream.output
print(stream.interrupts[0].value)
# -> 'Please provide feedback: foo bar'

stream = workflow.stream_events(Command(resume="baz"), config, version="v3")
print(stream.output)
# -> 'foo bar baz qux'
# :snippet-end:

# :remove-start:
assert stream.output == "foo bar baz qux", stream.output
# :remove-end:

# :snippet-start: langgraph-functional-api-hitl-review-helper-py
from typing import Any, Literal, TypedDict, Union

from langchain.messages import ToolMessage
from langgraph.types import interrupt


class ToolCallReview(TypedDict, total=False):
    action: Literal["continue", "update", "feedback"]
    data: Any


def review_tool_call(tool_call: dict) -> Union[dict, ToolMessage]:
    """Review a tool call, returning a validated version."""
    human_review: ToolCallReview = interrupt(
        {
            "question": "Is this correct?",
            "tool_call": tool_call,
        }
    )
    review_action = human_review["action"]
    review_data = human_review.get("data")
    if review_action == "continue":
        return tool_call
    if review_action == "update":
        return {**tool_call, "args": review_data}
    if review_action == "feedback":
        return ToolMessage(
            content=review_data, name=tool_call["name"], tool_call_id=tool_call["id"]
        )
    raise ValueError(f"Unknown review action: {review_action}")
# :snippet-end:

# :snippet-start: langgraph-functional-api-hitl-review-agent-py
from langchain.messages import AIMessage, HumanMessage, ToolMessage
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.func import entrypoint, task
from langgraph.graph import add_messages
from langgraph.types import Command


checkpointer = InMemorySaver()


@task
def call_model(messages: list) -> AIMessage:
    last = messages[-1]
    if isinstance(last, ToolMessage):
        return AIMessage(content="Search complete.")
    return AIMessage(
        content="",
        tool_calls=[
            {
                "name": "search",
                "args": {"query": "weather"},
                "id": "call_1",
                "type": "tool_call",
            }
        ],
    )


@task
def call_tool(tool_call: dict) -> ToolMessage:
    return ToolMessage(
        content=f"result for {tool_call['args']}",
        name=tool_call["name"],
        tool_call_id=tool_call["id"],
    )


@entrypoint(checkpointer=checkpointer)
def agent(messages, *, previous=None):
    if previous is not None:
        messages = add_messages(previous, messages)

    model_response = call_model(messages).result()
    while True:
        if not model_response.tool_calls:
            break

        # Review tool calls
        tool_results = []
        tool_calls = []
        updated_tool_calls = list(model_response.tool_calls)
        for i, tool_call in enumerate(model_response.tool_calls):
            review = review_tool_call(tool_call)
            if isinstance(review, ToolMessage):
                tool_results.append(review)
            else:  # is a validated tool call
                tool_calls.append(review)
                updated_tool_calls[i] = review

        if updated_tool_calls != list(model_response.tool_calls):
            model_response = model_response.model_copy(
                update={"tool_calls": updated_tool_calls}
            )

        # Execute remaining tool calls
        tool_result_futures = [call_tool(tool_call) for tool_call in tool_calls]
        remaining_tool_results = [fut.result() for fut in tool_result_futures]

        # Append to message list
        messages = add_messages(
            messages,
            [model_response, *tool_results, *remaining_tool_results],
        )

        # Call model again
        model_response = call_model(messages).result()

    # Generate final response
    messages = add_messages(messages, model_response)
    return entrypoint.final(value=model_response, save=messages)


config = {"configurable": {"thread_id": "2"}}

stream = agent.stream_events(
    [HumanMessage("What's the weather?")], config, version="v3"
)
_ = stream.output
print(stream.interrupts[0].value)
# -> {'question': 'Is this correct?', 'tool_call': {'name': 'search', ...}}

result = agent.invoke(Command(resume={"action": "continue"}), config)
print(result)
# :snippet-end:

# :remove-start:
assert result.content == "Search complete.", result
print("✓ langgraph-functional-api-hitl")
# :remove-end:
