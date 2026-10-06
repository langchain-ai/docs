# :remove-start:
import os

from langchain.messages import AIMessage, ToolMessage

os.environ.setdefault("ANTHROPIC_API_KEY", "sk-ant-test-key")


class _FakeArithmeticModel:
    def bind_tools(self, tools):
        return self

    def invoke(self, messages):
        if any(isinstance(message, ToolMessage) for message in messages):
            return AIMessage(content="The sum is 7.")
        return AIMessage(
            content="",
            tool_calls=[
                {
                    "name": "add",
                    "args": {"a": 3, "b": 4},
                    "id": "call_add_1",
                    "type": "tool_call",
                }
            ],
        )


# :remove-end:
# :snippet-start: langgraph-quickstart-functional-py
# Step 2: Define tools and model

from langchain.tools import tool
from langchain.chat_models import init_chat_model


model = init_chat_model(
    "claude-sonnet-4-6",
    temperature=0
)
# :remove-start:
model = _FakeArithmeticModel()
# :remove-end:


# Define tools
@tool
def multiply(a: int, b: int) -> int:
    """Multiply `a` and `b`.

    Args:
        a: First int
        b: Second int
    """
    return a * b


@tool
def add(a: int, b: int) -> int:
    """Adds `a` and `b`.

    Args:
        a: First int
        b: Second int
    """
    return a + b


@tool
def divide(a: int, b: int) -> float:
    """Divide `a` and `b`.

    Args:
        a: First int
        b: Second int
    """
    return a / b


# Augment the LLM with tools
tools = [add, multiply, divide]
tools_by_name = {tool.name: tool for tool in tools}
model_with_tools = model.bind_tools(tools)

from langgraph.graph import add_messages
from langchain.messages import (
    SystemMessage,
    HumanMessage,
    ToolCall,
)
from langchain_core.messages import BaseMessage
from langgraph.func import entrypoint, task


# Step 3: Define model task

@task
def call_llm(messages: list[BaseMessage]):
    """LLM decides whether to call a tool or not"""
    return model_with_tools.invoke(
        [
            SystemMessage(
                content="You are a helpful assistant tasked with performing arithmetic on a set of inputs."
            )
        ]
        + messages
    )


# Step 4: Define tool task

@task
def call_tool(tool_call: ToolCall):
    """Performs the tool call"""
    tool = tools_by_name[tool_call["name"]]
    return tool.invoke(tool_call)


# Step 5: Define agent

@entrypoint()
def agent(messages: list[BaseMessage]):
    model_response = call_llm(messages).result()

    while True:
        if not model_response.tool_calls:
            break

        # Execute tools
        tool_result_futures = [
            call_tool(tool_call) for tool_call in model_response.tool_calls
        ]
        tool_results = [fut.result() for fut in tool_result_futures]
        messages = add_messages(messages, [model_response, *tool_results])
        model_response = call_llm(messages).result()

    messages = add_messages(messages, model_response)
    return messages

# Step 6: Set up LangSmith tracing (optional)
# export LANGSMITH_TRACING=true
# export LANGSMITH_API_KEY="your-langsmith-api-key"

# Step 7: Run the agent
messages = [HumanMessage(content="Add 3 and 4.")]
messages = agent.invoke(messages)
for m in messages:
    m.pretty_print()
# :snippet-end:

# :remove-start:
tool_messages = [
    message for message in messages if isinstance(message, ToolMessage)
]
assert tool_messages, messages
assert "7" in str(tool_messages[0].content)
print("✓ langgraph-quickstart-functional")
# :remove-end:
