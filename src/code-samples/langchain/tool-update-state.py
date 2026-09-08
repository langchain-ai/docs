# :snippet-start: tool-update-state-py
from langchain.agents import AgentState
from langchain.messages import ToolMessage
from langchain.tools import ToolRuntime, tool
from langgraph.types import Command


class CustomState(AgentState):
    user_name: str


@tool
def set_user_name(new_name: str, runtime: ToolRuntime[None, CustomState]) -> Command:
    """Set the user's name in the conversation state."""
    return Command(
        update={
            "user_name": new_name,
            "messages": [
                ToolMessage(
                    content=f"User name set to {new_name}.",
                    tool_call_id=runtime.tool_call_id,
                )
            ],
        }
    )


# :snippet-end:

# :remove-start:
if __name__ == "__main__":
    from langchain.agents import create_agent
    from langchain_anthropic import ChatAnthropic

    model = ChatAnthropic(model_name="claude-sonnet-4-6", timeout=None)

    agent = create_agent(
        model,
        tools=[set_user_name],
        state_schema=CustomState,
        system_prompt=(
            "You are a test harness. Always call the `set_user_name` tool when asked to "
            "set the user's name. Reply with a brief confirmation."
        ),
    )
    result = agent.invoke(
        {"messages": [{"role": "user", "content": "Set my name to Alice."}]}
    )

    assert result["user_name"] == "Alice"
    tool_messages = [m for m in result["messages"] if isinstance(m, ToolMessage)]
    assert len(tool_messages) == 1
    assert tool_messages[0].content == "User name set to Alice."
    assert tool_messages[0].tool_call_id, "expected tool_call_id to be set"

    print("✓ Tool works as expected")
# :remove-end:
